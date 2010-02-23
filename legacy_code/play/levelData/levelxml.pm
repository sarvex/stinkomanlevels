package levelxml;

our $VERSION = '1.0';

use lib ("/home/superjoe/perl_modules");

use CGI;

use database;


sub printlevel {
	my $stage = shift;
	my ($stageMajor,$stageMinor) = $stage =~ m/(\d)\.(\d)/;
	
	my $x = "";
	
	# no caching
	$x=$x. "Cache-Control: no-cache\n";
	$x=$x. "Pragma: no-cache\n";

	$x=$x. CGI::header(-type => "text/xml");
	
	# find which level to play
	my $query = CGI->new();
	my $session = $query->cookie("session");
	
	if( ! defined $session || $session eq ""){
		$x=$x. ' ';
		return $x;
	}
	
	my $safeSession = database::protect_string($session);
	
	if( ! database::create_table("levelsession") ){
		$x=$x. ' ';
		return $x;
	}
	my $dbh = database::dbconnect();
	my $sql = "SELECT level FROM levelsession WHERE session = '$safeSession';";
	my $sth = $dbh->prepare($sql);
	if( ! $sth->execute() ){
		warn "MySQL Error getting which level to play from levelsessions: $DBI::errstr";
		$x=$x. ' ';
		return $x;
	}
	if( $sth->rows == 0){
		$x=$x. ' ';
		return $x;
	}
	
	my ($level) = $sth->fetchrow_array();
	
	# get level info
	my $safeTitle = database::protect_string($level);
	$sql = "SELECT majorstage, minorstage, file FROM levels WHERE title = '$safeTitle';";
	$sth = $dbh->prepare($sql);
	if( ! $sth->execute() ){
		warn "MySQL Error getting level data for $level: $DBI::errstr";
		$x=$x. ' ';
		return $x;
	}
	if( $sth->rows != 1){
		$x=$x. ' ';
		return $x;
	} 
	
	my ($major,$minor, $file) = $sth->fetchrow_array();
	
	# make sure the level was made to be played on this stage.
	if( $major == $stageMajor && $minor == $stageMinor ){
		# correct level, print the file
		if( ! open(FILE, "../../levels/$file") ){
			warn "Error opening ../../levels/$file for reading: $!";
			$x=$x. ' ';
			return $x;
		}
		$x=$x. join("\n",<FILE>);
		close(FILE);
	} elsif ( $minor == 3 && $major == $stageMajor && $stageMinor == 2) {
		# print an instant win level
		if( ! open(FILE, "../instantwin.xml") ){
			warn "Error opening ../instantwin.xml for reading: $!";
			$x=$x. ' ';
			return $x;
		}
		$x=$x. join("\n",<FILE>);
		close(FILE);
	} else {
		print ' ';
		return $x;
	}
	
	return $x;
}



1;
