#!/usr/bin/perl -wT

use strict;
use lib ("/home/superjoe/perl_modules");
use CGI;
use database;

my $imgCheck  = qq{<img src="/img/check.gif" />};
my $imgInvalid = qq{<img src="/img/invalid.gif" />};

my $query = CGI->new();

my $name = $query->param('name');

print CGI::header();

exit(1) if( ! defined $name);

#validate name
if( $name =~ m/[^a-zA-Z0-9_]/ ){
	print "$imgInvalid please use A-Z, 0-9, _";
	exit(0);
}

if( length($name) < 2 || length($name) > 32 ){
	print "$imgInvalid please use 2-32 characters";
	exit(0);
}

#confirm users table
my $dbh = database::dbconnect() && database::create_table("users") || bail("<i>Unable to connect to database</i>");
my $x = database::user_exists($name);
if( $x == -1 ){
	bail("<i>Database error</i>");
} else {
	print $x ? "$imgInvalid unavailable." : "$imgCheck OK";
}


sub bail {
	my $msg = shift;
	print $msg;
	exit(1);
}
