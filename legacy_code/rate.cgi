#!/usr/bin/perl -wT

use strict;

use lib ("/home/superjoe/perl_modules");

use CGI;

use database;

print CGI::header();

my $query = CGI->new();
my $session = $query->cookie("session");
my $level = $query->param('level');
my $score = $query->param('score');


#validate score
$score = -1 if(! defined $score || $score > 2 || $score < -1);
$score = int($score);

my $username = database::user_logged_in($session) || bail("You are not logged in");

database::create_table("userleveldata") || bail();

my $safeLevel = database::protect_string($level);

my $dbh = database::dbconnect();
my $sql = "SELECT rating FROM userleveldata WHERE (level = '$safeLevel' AND user = '$username');";
my $sth = $dbh->prepare($sql);

$sth->execute() || bail();

if($sth->rows == 1){
	my($oldRating) = $sth->fetchrow_array();
	
	$sql = "UPDATE userleveldata SET rating = $score WHERE (level = '$safeLevel' AND user = '$username');";
	$sth = $dbh->prepare($sql);
	$sth->execute() || bail();
	
	if( $oldRating >= 0 && $score >= 0 ){
		# change ratings
		$sql = "UPDATE levels SET ratecount = ratecount + $score - $oldRating WHERE title = '$safeLevel';";
	} elsif ($oldRating >= 0 && $score < 0) {
		# remove rating
		$sql = "UPDATE levels SET ratecount = ratecount - $oldRating, ratetotal = ratetotal - 2 WHERE title = '$safeLevel';";
	} elsif ($oldRating < 0 && $score >= 0 ){
		# add new rating
		$sql = "UPDATE levels SET ratecount = ratecount + $score, ratetotal = ratetotal + 2 WHERE title = '$safeLevel';";
	}	
	$sth = $dbh->prepare($sql);
	$sth->execute() || bail();
	
} else {
	$sql = "INSERT INTO userleveldata (level,user,rating) VALUES ('$safeLevel','$username',$score);";
	$sth = $dbh->prepare($sql);
	$sth->execute() || bail();
	
	if ( $score >= 0){
		$sql = "UPDATE levels SET ratecount = ratecount + $score, ratetotal = ratetotal + 2 WHERE title = '$safeLevel';";
		$sth = $dbh->prepare($sql);
		$sth->execute() || bail();
	}
}



# success!
my @scoreStr = ("-1", "0" , "+1");
if( $score < 0 ){
	print qq{Rate this level: <a href="javascript:rate(0);">-1</a> <a href="javascript:rate(1);">0</a> <a href="javascript:rate(2);">+1</a>};
} else {
	print qq{You rated this level $scoreStr[$score]. <a href="javascript:rate(-1);">Undo</a>};
}



sub bail {
	my ($msg) = @_;
	$msg = "Error rating level" if(! defined $msg);
	print $msg;
	exit(1);
}
