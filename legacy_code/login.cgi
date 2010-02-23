#!/usr/bin/perl -wT

use strict;

use lib ("/home/superjoe/perl_modules");

use CGI;

use database;

my $query = CGI->new();

my $name = $query->param('name');
my $pass = $query->param('pass');
my $remember = $query->param('remember');

bail() if(! defined $name || ! defined $pass );


my $x = database::log_user_in($name,$pass);
if( substr($x,0,1) eq '#'){
	print CGI::header();
	print $x;
} else {
	my $exp = $remember ? "+7y" : "now";
	my $cookie = $query->cookie(-name => 'session', -value => $x, -path => "/", -expires => $exp, -domain => ".superjoesoftware.com");
	print CGI::header(-cookie => $cookie);
	print $x;
}


sub bail {
	print CGI::header();
	print "#Invalid name and password supplied.";
	exit(1);
}
