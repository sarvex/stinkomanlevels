#!/usr/bin/perl -wT

use strict;

use lib ("/home/superjoe/perl_modules");

use CGI;

use database;

my $query = CGI->new();

my $session = $query->cookie('session');

print CGI::header();
print database::log_user_out($session);

sub bail {
	print "0";
	exit(1);
}
