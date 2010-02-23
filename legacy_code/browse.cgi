#!/usr/bin/perl -wT

use strict;

use lib ("/home/superjoe/perl_modules");

use CGI;

use templates;
use database;
use common;

my $query = CGI->new();

my $sort  = $query->param('sort');
my $order = $query->param('order');
my $offset= $query->param('start');

my @sorts = qw(title stage difficulty length author datecreated rating);

my %validSort = map {$_ => $_} @sorts;
$validSort{'rating'} =  "(ratecount / ratetotal)"; #"((ratecount+1) / (ratetotal+1))";
$validSort{'stage'} = "(majorstage + (minorstage/10))";

$sort = 'title' if( ! defined $sort || ! $validSort{$sort});
$order = 'ASC' if (! defined $order || uc($order) ne "DESC");
my $newOrder = $order eq 'ASC' ? 'DESC' : 'ASC';
$offset = 0 if(! defined $offset || $offset < 0);
$offset = int($offset);

my %columnOrders = map {$_ => 'ASC'} @sorts;
$columnOrders{datecreated} = 'DESC';
$columnOrders{rating} = 'DESC';
$columnOrders{$sort} = $newOrder;

database::create_table('levels') || bail("There was an error loading the levels. Please try again or come back later.");

# create the table to browse levels
my $sql = "SELECT title, majorstage, minorstage, difficulty, length, author, datecreated, ratecount, ratetotal FROM levels ORDER BY $validSort{$sort} $order";
my $sub = sub {
	# assume parameter is an array of all the above entries. return an array which will fill the columns.
	my $escTitle 		= CGI::escape($_[0]);
	my $escAuthor		= CGI::escape($_[5]);
	my $rating   		= $_[8] == 0 ? "unrated" : common::round(($_[7] / $_[8])*100) . "%" ;
	my @difficultyStr = ("Very Easy", "Easy", "Medium", "Hard", "Very Hard");
	my @lengthStr 		= qw(Short Medium Long);
	return ("<a href=\"/play/$escTitle\">$_[0]</a>", "<a href=\"/user/$escAuthor\">$_[5]</a>", $rating, "$_[1].$_[2]", $difficultyStr[$_[3]+2], $lengthStr[$_[4]+1], common::fmtsqldate($_[6]));
};
my $navSub = sub {
	# assume parameter is the start index and return a link to browse to that start index
	return "/browse?start=$_[0]&amp;sort=$sort&amp;order=$order";	
};
my @headings = (
qq{<a href="browse?sort=title&amp;order=$columnOrders{title}">Title</a>} ,
qq{<a href="browse?sort=author&amp;order=$columnOrders{author}">Author</a>} ,
qq{<a href="browse?sort=rating&amp;order=$columnOrders{rating}">Rating</a>} , 
qq{<a href="browse?sort=stage&amp;order=$columnOrders{stage}">Stage</a>} , 
qq{<a href="browse?sort=difficulty&amp;order=$columnOrders{difficulty}">Difficulty</a>} , 
qq{<a href="browse?sort=length&amp;order=$columnOrders{length}">Length</a>} , 
qq{<a href="browse?sort=datecreated&amp;order=$columnOrders{datecreated}">Date Added</a>}		);

my $x = database::html_sql_table($sql, $sub, $offset, $navSub, \@headings) || bail("There was an error loading the levels. Please try again or come back later.");



my $body = "<h2>Browse Levels</h2>$x";


print templates::mainpage("Browsing Levels - Custom Stinkoman Levels", "", $body);


sub bail {
	my $msg = shift;
	print $msg;
	exit(1);
}
