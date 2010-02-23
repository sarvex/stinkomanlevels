#!/usr/bin/perl -wT

use strict;


use lib ("/home/superjoe/perl_modules");


use CGI;

use templates;
use database;
use common;

my $reviewLimit = 20;
my $levelLimit = 10;

my $query = CGI->new();
my $session = $query->cookie("session");

bail("You are not logged in.") if( ! defined $session || $session eq "");

my $username = database::user_logged_in($session) || bail("You are not logged in.");
my $safeUser = database::protect_string($username);

# get new comments on user's levels
my $reviews = "<p>Error loading reviews</p>";
if( database::create_table('levelcomments') && database::create_table('levels') ){
	my $sql = "SELECT indexkey, author, content, postdate, level FROM levelcomments WHERE level IN (SELECT title FROM levels WHERE author = '$safeUser') ORDER BY postdate DESC";
	my $rowSub = sub {
		my ($i, $array) = @_;
		my $htmlContent = common::removeHTML($$array[2]);
		my $htmlAuthor = common::removeHTML($$array[1]);
		my $escAuthor = CGI::escape($$array[1]);
		my $htmlDate = common::fmtsqldate($$array[3]);
		my $htmlLevel = common::removeHTML($$array[4]);
		my $escLevel = CGI::escape($$array[4]);
		
		my $odd = $i % 2 == 0 ? '' : ' class="odd"';
		#$reviewCount = $i if($i > $reviewCount);
		
		return qq{<div$odd><h4>$htmlDate by <a href="/user/$escAuthor">$htmlAuthor</a> in <a href="/play/$escLevel">$htmlLevel</a></h4>$htmlContent</div>};
	};
	
	my $navSub = sub {
		return "javascript:gotoPage($_[0]);";
	};
	
	my $x = database::html_sql_join($sql, $rowSub, 0, $navSub, $reviewLimit, 0, "<p>No reviews on your levels yet.</p>");
	$reviews = $x if( $x);
	
}

# levels the user has not rated
my $unrated = "<p>Error loading unrated levels</p>";
if( database::create_table("levels") && database::create_table("userleveldata")) {
	my $sql = "SELECT title, author, datecreated FROM levels WHERE title NOT IN (SELECT level FROM userleveldata WHERE user = '$safeUser' AND rating >= 0 ) ORDER BY datecreated ASC";
	my $colSub = sub {
		my $escTitle = CGI::escape($_[0]);
		my $escAuthor = CGI::escape($_[1]);
		my $datecreated = common::fmtsqldate($_[2]);
		return ("<a href=\"/play/$escTitle\">$_[0]</a>", "<a href=\"/user/$escAuthor\">$_[1]</a>", $datecreated);
	};
	my @headings = ("Level", "Creator" ,"Date Created");
	$unrated = database::html_sql_table($sql, $colSub, 0, 0, \@headings, $levelLimit, 1);
}


my $body = <<MAIN_HTML;
<h2>Dashboard</h2>
<h3>Levels you have not rated:</h3>
$unrated
<h3>Your level reviews</h3>
<div id="comments">
	<div id="reviews">
		$reviews
	</div>
</div>
MAIN_HTML

print templates::mainpage("Dashboard - Custom Stinkoman Levels","",$body);

sub bail {
	print templates::mainpage("Dashboard - Custom Stinkoman Levels", "", "<h2>Dashboard</h2><p>$_[0]</p>");
	exit(1);
}
