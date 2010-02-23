#!/usr/bin/perl -wT

use strict;


use lib ("/home/superjoe/perl_modules");


use CGI;

use templates;
use database;

my $rowsToShow = 5;

my $sql = "SELECT title, author, ratecount, ratetotal FROM levels ORDER BY datecreated DESC";
my $colSub = sub {
	my $escTitle = CGI::escape($_[0]);
	my $escAuthor = CGI::escape($_[1]);
	my $rating = $_[3] == 0 ? "unrated" : common::round(($_[2] / $_[3])*100) . "%" ;
	return ("<a href=\"/play/$escTitle\">$_[0]</a>", "<a href=\"/user/$escAuthor\">$_[1]</a>", $rating);
};
my @headings = qw(Level Creator Rating);
my $newLevelsTable = database::html_sql_table($sql, $colSub, 0, 0, \@headings, $rowsToShow, 1);

$sql = "SELECT title, author, ratecount, ratetotal FROM levels ORDER BY (ratecount / ratetotal) DESC";
my $topLevelsTable = database::html_sql_table($sql, $colSub, 0, 0, \@headings, $rowsToShow, 1);


my $body = <<MAIN_HTML;
<h2>Uh oh</h2>
<p>
	<font color="red">It looks like login and register is broken. I'm going to fix it in one week. It is Feb 21 2010 right now so if it's more than a week later, I suck.</font>
</p>
<h2>Welcome!</h2>
<p>
	Welcome to the Custom Stinkoman Levels site, where you can upload your own alterations of Stinkoman levels for all to see. If you don't have it yet, grab the <a href="/download">level editor</a> and get to work.
</p>
<h2>Your old stuff</h2>
<p>
	If you were a part of this way back when, I still have your levels! <a href="/oldlevels">Find your stuff</a> and upload it again please.
</p>
<div class="tablesection">
	<div class="tableblock">
		<h3>New Levels</h3>
		$newLevelsTable
	</div>
	<div class="tableblock">
		<h3>Top Levels</h3>
		$topLevelsTable
	</div>
	<div class="clear"><br /></div>
</div>
MAIN_HTML

print templates::mainpage("Custom Stinkoman Levels","",$body);

