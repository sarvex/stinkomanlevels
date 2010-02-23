#!/usr/bin/perl -wT

use strict;

use lib ("/home/superjoe/perl_modules");

use CGI;

use database;

print CGI::header();

my $query = CGI->new();

my $level = $query->param('level');
my $user = $query->param('user');
my $review = $query->param('review');


bail() if( (! defined $level && ! defined $user) || ! defined $review );

my $session = $query->cookie('session');
my $username = database::user_logged_in($session) || bail();

my $tableName = (defined $level) ? 'levelcomments' : 'usercomments';
database::create_table($tableName) || bail();
my $dbh = database::dbconnect() || bail();

my $safeContent = database::protect_string($review);
my $safeAuthor = database::protect_string($username);

my $sql;

if( defined $level ){
	my $safeLevel = database::protect_string($level);
	$sql = "INSERT INTO levelcomments (level, author, content) VALUES ('$safeLevel', '$safeAuthor', '$safeContent' );";
} else {
	my $safeUser = database::protect_string($user);
	$sql = "INSERT INTO usercomments (user, author, content) VALUES ('$safeUser', '$safeAuthor', '$safeContent' );";
}

my $sth = $dbh->prepare($sql);
$sth->execute() || bail();


print "1";


sub bail {
	print "0";
	exit(1);
}
