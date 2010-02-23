#!/usr/bin/perl -wT

use strict;

use lib ("/home/superjoe/perl_modules");

use CGI;

use database;
use templates;
use common;

my $commentLimit = 10;

my $query = CGI->new();

#my $user = $query->param('user');
my $user;

my $session = $query->cookie('session');

#get from uri
if( ! defined $user){	
	($user) =  $ENV{REQUEST_URI} =~ m/\/user\/(.*)$/ ;
	$user = CGI::unescape($user) if( defined $user);
}

invalid("The user you tried to access does not exist. Use the buttons above to explore the site.") if( ! defined $user);

my $safeUser = database::protect_string($user);
my $escUser = CGI::escape($user);

# make sure it's a real user
database::create_table("users") || bail();
my $dbh = database::dbconnect() || bail();
my $sql = "SELECT activated, registerdate, lastlogin FROM users WHERE screenname = '$safeUser';";
my $sth = $dbh->prepare($sql);
$sth->execute() || bail();
invalid("The user you tried to access does not exist. Use the buttons above to explore the site.") if( $sth->rows == 0);
my($activated, $registerdate, $lastlogin) = $sth->fetchrow_array();

my $htmlUser = common::removeHTML($user);
my $body = "";
my $js = "";
if( $activated ){

	# create levels table
	$sql = "SELECT title, majorstage, minorstage, difficulty, length, datecreated, ratecount, ratetotal FROM levels WHERE author = '$safeUser'";
	my $sub = sub {
		# assume parameter is an array of all the above entries. return an array which will fill the columns.
		my $escTitle 		= CGI::escape($_[0]);
		my $htmlTitle		= common::removeHTML($_[0]);
		my $rating   		= $_[7] == 0 ? "unrated" : common::round(($_[6] / $_[7])*100) . "%" ;
		my @difficultyStr = ("Very Easy", "Easy", "Medium", "Hard", "Very Hard");
		my @lengthStr 		= qw(Short Medium Long);
		return ("<a href=\"/play/$escTitle\">$htmlTitle</a>", $rating, "$_[1].$_[2]", $difficultyStr[$_[3]+2], $lengthStr[$_[4]+1], common::fmtsqldate($_[5]));
	};
	my $navSub = sub {
		# assume parameter is the start index and return a link to browse to that start index
		return "javascript:getPage($_[0]);";	
	};
	my @headings = (
		qq{Title} ,
		qq{Rating} , 
		qq{Stage} , 
		qq{Difficulty} , 
		qq{Length} , 
		qq{Date Added}		);

	my $levelTable = database::html_sql_table($sql, $sub, 0, $navSub, \@headings);
	$levelTable = "<p>Error accessing levels.</p>" if( ! $levelTable);
	
	# generate html for the comments on this user's page
	my $reviewForm = "";
	my $escAuthor = "";
	my $htmlAuthor = "";
	my $username = database::user_logged_in($session);
	if( $username){
		$escAuthor = CGI::escape($username);
		$htmlAuthor = CGI::escape($username);
		# create post review form
		$reviewForm = qq{<form action="/"><textarea name="content" rows="8" cols="48"></textarea><br /><input type="button" value="Post" onClick="post(content.value);" /></form>};
	} else {
		$reviewForm = "<p>Log in to post comments.</p>";
	}
	
	# comments
	my $commentCount = 0;
	my $comments = "<p>Error loading comments</p>";
	if( database::create_table('usercomments') ){
		$sql = "SELECT indexkey, author, content, postdate FROM usercomments WHERE user = '$safeUser' ORDER BY postdate DESC";
		my $rowSub = sub {
			my ($i, $array) = @_;
			my $htmlContent = common::removeHTML($$array[2]);
			my $htmlAuthor = common::removeHTML($$array[1]);
			my $escAuthor = CGI::escape($$array[1]);
			my $htmlDate = common::fmtsqldate($$array[3]);
			
			my $odd = $i % 2 == 0 ? '' : ' class="odd"';
			$commentCount = $i if($i > $commentCount);
		
			return qq{<div$odd><h4>$htmlDate by <a href="/user/$escAuthor">$htmlAuthor</a></h4>$htmlContent</div>};
		};
	
		my $navSub = sub {
			return "javascript:gotoPage($_[0]);";
		};
	
		my $x = database::html_sql_join($sql, $rowSub, 0, $navSub, $commentLimit, 0, "<p>No one has posted a comment on this page yet.</p>");
		$comments = $x if( $x);
	
	}
	
	
	# javascript
	$js = <<JAVA_SCRIPT;
var reviewCount = $commentCount;
var styleOdd = ' class="odd"';

function post(review) {
	var xmlHttp = newAjax();
	
	var rfHTML = objById("reviewform").innerHTML;
	objById("reviewform").innerHTML = "<p>Posting your review...<\\/p>";

	xmlHttp.onreadystatechange = function(){
		if( xmlHttp.readyState == 4){
			if( xmlHttp.responseText == 1 ){
				//success
				objById("reviewform").innerHTML = rfHTML;
				var newHTML = '<div' + (reviewCount % 2 == 0 ? '' : styleOdd )  + '><h4>Just now by <a href="/user/$escAuthor">$htmlAuthor<\\/a><\\/h4>' + removeHTML(review) + '<\\/div>';
				if( reviewCount == 0)
					objById("reviews").innerHTML = newHTML;
				else
					objById("reviews").innerHTML = newHTML + objById("reviews").innerHTML;
				reviewCount++;
			} else {
				objById("reviewform").innerHTML = "<p>Error posting review.<\\/p>";
			}
		}
	}


	xmlHttp.open("GET", "../post.cgi?user=$escUser&review="+escape(review) ,true);
	xmlHttp.send(null);
}


function removeHTML(str) {
	
	
	var newstr = replaceInStr(str, "&", "&amp;");
	
	newstr = replaceInStr(newstr, '"', "&quot;");
	newstr = replaceInStr(newstr, "  ", "&nbsp;&nbsp;");
	newstr = replaceInStr(newstr, "<", "&lt;");
	newstr = replaceInStr(newstr, ">", "&gt;");

	return newstr;
}

function replaceInStr(str, sfind, sreplace) {
	
	var newstr = "";
	for( var i=0; i<str.length; i++){
		if( str.substring(i,i+sfind.length) == sfind ){
			newstr += sreplace;
			i += sfind.length-1;
		} else {
			newstr += str.substring(i,i+1);
		}
	}
	
	return newstr;
}


JAVA_SCRIPT
	
	my $memberSince = common::fmtsqldate($registerdate);
	my $loginDate = common::fmtsqldate($lastlogin);
	$body = <<MAIN_BODY;
<h2>$htmlUser</h2>
<p>
	Been a member since: $memberSince <br />
	Last login: $loginDate <br />
</p>
<h2>${htmlUser}'s levels</h2>
$levelTable
<div id="comments">
	<h2>Comments</h2>
	<div id="reviews">
		$comments
	</div>
	<h3>Post a comment</h3>
	<div id="reviewform">
		$reviewForm
	</div>
</div>
MAIN_BODY
	
} else {
	$body = qq{<h2>$htmlUser</h2><p>$htmlUser is has not activated his/her account yet. It will be automatically deleted if he/she does not activate it in 1 day.</p>};
}

print templates::mainpage("$user - Custom Stinkoman Levels","",$body, $js);

sub bail {
	print templates::mainpage("User page - Custom Stinkoman Levels", "", "<p>There was an error accessing this user's page. Please try again or come back later.</p>");
	exit(1);
}

sub invalid {
	print templates::mainpage("User page - Custom Stinkoman Levels", "", "<p>$_[0]</p>");
	exit(0);
}
