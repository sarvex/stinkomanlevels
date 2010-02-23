#!/usr/bin/perl -wT

use strict;


use lib ("/home/superjoe/perl_modules");

use CGI;

use database;
use templates;

my $query = CGI->new();

my $name = $query->param('name');
my $code = $query->param('code');

finish("We are unable to activate your account.") if( ! defined $name || ! defined $code || length($name) > 32 || length($code) != 32 || $code =~ m/[^a-zA-Z0-9]/ );

my $safeScreenname = database::protect_string($name);

database::create_table('users') || bail("There was an error confirming your account. Please come back later and try again.");
my $dbh = database::dbconnect();

#check if code is correct
my $sql = "SELECT activatecode FROM users WHERE screenname = '$safeScreenname';";
my $sth = $dbh->prepare($sql);
if( ! $sth->execute()){
	warn "MySQL Error checking activation code for '$name': $DBI::errstr";
	bail("There was an error confirming your account. Please come back later and try again.");
}
my ($realCode) = $sth->fetchrow_array();

finish("The confirmation code you supplied is invalid.") if( $code ne $realCode );


$sql = "UPDATE users SET activated = true WHERE screenname = '$safeScreenname';";
$sth = $dbh->prepare($sql);
if( ! $sth->execute() ){
	warn "MySQL Error activating account of '$name': $DBI::errstr";
	bail("There was an error confirming your account. Please come back later and try again.");
}

finish(qq{Your account was successfully activated! <a href="javascript:login();">Log in</a>});


sub bail {
	my $msg = shift;
	print templates::mainpage("Error - Custom Stinkoman Levels","","<h2>Account confirmation</h2><p>$msg</p>");
	exit(1);
}

sub finish {
	my $msg = shift;
	print templates::mainpage("Account Activation - Custom Stinkoman Levels", "", "<h2>Account confirmation</h2><p>$msg</p>");
	exit(0);
}
