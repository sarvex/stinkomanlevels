#!/usr/bin/perl -wT

use strict;

use lib ("/home/superjoe/perl_modules");

use CGI;

use database;
use templates;


my $maxCommentsLength = 512;
my $maxFileSize = 307200; #300 KB



#grab cookies!
my $query = CGI->new();
my $session = $query->cookie("session");

my $username = database::user_logged_in($session);

# must be logged in to submit levels
if( ! $username){
	print CGI::redirect("submit");
	exit(0);
}

# get parameters
my $title = $query->param("title");
my $stage = $query->param("stage");
my $comments = $query->param("comments");
my $difficulty = $query->param("difficulty");
my $length = $query->param("length");

my $xmlcode = $query->param("xmlcode");
my $xmlfile = $query->param("xmlfile");

#validate parameters
invalid('Invalid level title. Please <a href="javascript:history.go(-1);">try another one</a>.') if( ! defined $title || $title eq "" || length($title) > 32 );
invalid("Invalid stage.") if( ! defined $stage || ! ($stage =~ m/^\d\.\d$/) );
invalid("Invalid difficulty.") if( ! defined $difficulty || $difficulty eq "");
invalid("Invalid length.") if( ! defined $length || $length eq "" );

#more validation
$difficulty = int($difficulty);
$length = int($length);
if( defined $comments){
	$comments = substr($comments,0,$maxCommentsLength-3) . "..." if( length($comments) > $maxCommentsLength);
} else {
	$comments = "";
}

#make sure title is unique
my $safeTitle = database::protect_string($title);
database::create_table('levels') || bail("Error creating level data");
my $dbh = database::dbconnect();
my $sql = "SELECT title, author, file FROM levels WHERE title = '$safeTitle';";
my $sth = $dbh->prepare($sql);
if(! $sth->execute() ){
	warn "MySQL Error determining if $title is unique: $DBI::errstr";
	bail("Error validating data. Please try again or come back later.");
}

my $exists = $sth->rows > 0;
my($level_title, $author, $file);
($level_title, $author, $file)  = $sth->fetchrow_array() if($exists);

	# if it's the author, overwrite data
invalid("That level title is already taken. Please try another one.") if($exists && $username ne $author );

# make sure the levels directory exists
if(! $exists && ! -e "levels/"){
	mkdir("levels",0777);
}

# create a suitable filename

my($filename, $ext);
if( ! $exists ) {
	$filename = substr($title,0,24);
	$filename =~ s/[^a-zA-Z0-9_\-\.]/\_/g;


	#extension
	$ext = ".xml";
	
	#if it exists, rename it counting up numbers till the file does not exist.
	if(-e "levels/$filename$ext"){
		my $count = 1;
		my $fstr = substr($filename,0,20);
		my $cstr = "0001";
		while(-e "levels/$fstr$cstr$ext"){
		  $count++;
		  $cstr = $count;
		  while(length($cstr) < 4){
			 $cstr = "0" . $cstr;
		  }
		}
		$filename = $fstr . $cstr . $ext;
	
	} else {
		$filename .= $ext;
	}
	
	#secure dependency
	$filename =~ m/(.*)/;
	$filename = $1;
} else {
	$filename = $file;
}

if( (defined $xmlcode && length($xmlcode) > 0) && (! defined $xmlfile || length($xmlfile) == 0)  ){
	# pasted code
	if( length($xmlcode) <= $maxFileSize ){
	  # make the file
	  if ( open(FILE,">levels/$filename") ){
		 print FILE $xmlcode;
		 close(FILE);
	  } else {
		 warn "Error opening levels/$filename for writing: $!";
		 bail("Error creating level file. Please try again or come back later.");
	  }
	} else {
	  # file too big
	  invalid("The file is too big to upload.");
	}
} elsif ( (! defined $xmlcode || length($xmlcode) == 0) && (defined $xmlfile && length($xmlfile) > 0)  ) {
	#strip stuff off the file name we don't want
	#$xmlfile =~ m/^.*(\\|\/)(.*)/;  

	if( open(FILE,">levels/$filename") ){
	  binmode(FILE);
	  my $flen = 0;
	  
	  while(my $bytes = <$xmlfile>){
		 $flen += length($bytes);
		 if($flen > $maxFileSize){
		   # file too big
		   close(FILE);
		   unlink("levels/$filename") || warn "Error deleting levels/$filename after realizing file was too big: $!";
		   invalid("The file is too big to upload.");
		 }
		 print FILE $bytes;
	  }
	  close(FILE);
	} else {
	  warn "Error opening levels/$filename for writing: $!";
	  bail("Error creating the level file.");
	}
} else {
	# upload a file OR paste code
	invalid("Either upload a file OR paste the code into the box.");
}


# file has been written to disk, now save level information
my ($major,$minor) = $stage =~ m/^(\d)\.(\d)$/;
my $safeAuthor = database::protect_string($username);
my $safeComments = database::protect_string($comments);
my $safeFile = database::protect_string($filename);

if( $exists ){
	$sql = "UPDATE levels SET majorstage=$major, minorstage=$minor, difficulty=$difficulty, length=$length, comments='$safeComments' WHERE title='$safeTitle';";
} else {
	$sql = "INSERT INTO levels (title, majorstage, minorstage, difficulty, length, author, comments, file) VALUES ('$safeTitle', $major, $minor, $difficulty, $length, '$safeAuthor', '$safeComments', '$safeFile');";
}

$sth = $dbh->prepare($sql);
if(! $sth->execute() ) {
	warn "MySQL Error: Unable to add level data to database: $DBI::errstr";
	bail("Error saving level data");
} 

my $escapedTitle = CGI::escape($title);
print templates::mainpage("Upload level - " . templates::title(), "", qq{<h2>Upload level</h2><p>Your level was uploaded successfully! <a href="play/$escapedTitle">Go play it</a> or <a href="submit">upload another</a>.</p>});


sub invalid {
	my $msg = shift;
	print templates::mainpage("Upload level - " . templates::title(),"", "<h2>Unable to upload level</h2><p>$msg</p>" );
	exit(0);
}

sub bail {
	my $msg = shift;
	print templates::mainpage("Upload error - " . templates::title(),"", "<h2>Error uplodaing level</h2><p>$msg</p>" );
	exit(1);
}
