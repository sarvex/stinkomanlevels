#!/usr/bin/perl -wT

use strict;

use lib ("/home/superjoe/perl_modules");

use CGI;

use database;
use templates;
use common;

my $reviewLimit = 10;

my $query = CGI->new();

#my $level = $query->param('level');
my $level;

#get from uri
if( ! defined $level){	
	($level) =  $ENV{REQUEST_URI} =~ m/\/play\/(.*)$/ ;
	$level = CGI::unescape($level) if( defined $level);
}


# validate level
invalid('The level you are trying to play does not exist. Try <a href="/browse">browsing</a> for levels to play.') if( ! defined $level || $level eq "");

my $safeLevel = database::protect_string($level);
my $escLevel = CGI::escape($level);

# get info from database about level

database::create_table('levelsession') || bail("There was an error loading the level. Please try again or come back later.");
my $dbh = database::dbconnect();
my $sql = "SELECT majorstage, minorstage, difficulty, length, author, comments, file, datecreated, ratecount, ratetotal, file FROM levels WHERE title = '$safeLevel';";
my $sth = $dbh->prepare($sql);
if( ! $sth->execute() ){
	warn "MySQL Error getting level data for '$level': $DBI::errstr";
	bail("There was an error loading the level. Please try again or come back later.");
}
invalid('The level you are trying to play does not exist. Try <a href="/browse">browsing</a> for levels to play.') if( $sth->rows != 1);

my @data = $sth->fetchrow_array();

my $author = $data[4];
# set up this session for playing the level
# get session cookie, create new if necessary
my $session = $query->cookie("session");
if( ! defined $session || $session eq "" ) {
	$session = database::create_hash(32);
	templates::setSession($session);
}

# delete existing entry
my $safeSession = database::protect_string($session);
$sql = "DELETE FROM levelsession WHERE session = '$safeSession';";
$sth = $dbh->prepare($sql);
if( ! $sth->execute() ){
	warn "MySQL Error deleting session from levelsessions: $DBI::errstr";
	bail('There was an error loading the level. Please try again or come back later.');
}

# add session entry
$sql = "INSERT INTO levelsession (session, level) VALUES ('$safeSession', '$safeLevel');";
$sth = $dbh->prepare($sql);
if( ! $sth->execute() ){
	warn "MySQL Error adding a session to levelsessions: $DBI::errstr";
	bail('There was an error loading the level. Please try again or come back later.');
}

# remember lastplayed time
$sql = "UPDATE levels SET lastplayed = CURRENT_TIMESTAMP WHERE title = '$safeLevel';";
$sth = $dbh->prepare($sql);
$sth->execute();


# stage instructions
my $stageInstructions;
if( $data[1] == 3 ){
	# stage x.3
	my $showStage = "$data[0].2";
	$stageInstructions = qq{This is a boss level. Press &quot;Continute&quot; and select <u>Stage $showStage</u> to play this level.};
} else {
	# normal stage
	$stageInstructions = qq{This level is meant to be played on <u>Stage $data[0].$data[1]</u>; make sure you press &quot;Continute&quot; and select that stage!};
}

# if author notes is blank, put default message
$data[5] = "The author has not entered any notes." if($data[5] eq "");

my @lengthStr = qw(Short Medium Long);
my @difficultyStr = ("Very Easy","Easy","Medium","Hard","Very Hard");

# make stuff html safe
my $htmlTitle   = common::removeHTML($level);
my $htmlAuthor  = common::removeHTML($data[4]);
my $htmlComments= common::removeHTML($data[5]);

my $escAuthor = CGI::escape($data[4]);

my $htmlLength = $lengthStr[$data[3]+1];
my $htmlDifficulty = $difficultyStr[$data[2]+2];

my $htmlRating;
if( $data[9] == 0 ){
	$htmlRating = "not rated";
} else {
	$htmlRating = common::round(($data[8] / $data[9]) * 100) . "%";
}

# download
my $downLink = "/levels/" . CGI::escape($data[10]);
my $sizeStr = common::sizeString(-s "../levels/$data[10]");            #;;;

# create the html for rating the level and posting a review
my $noRatingHTML = qq{Rate this level: <a href="javascript:rate(0);">-1</a> <a href="javascript:rate(1);">0</a> <a href="javascript:rate(2);">+1</a>};
my $rateHTML = "";
my $reviewForm = "";
my $escUser = "";
my $htmlUser = "";
my $username = database::user_logged_in($session);
my $escLevel = common::escapeChar(common::escapeChar(CGI::escape($level),"\\"),'"');

if( $username){	
	$escUser = CGI::escape($username);
	$htmlUser = common::removeHTML($username);
	# figure out what the user rated this level as
	$sql = "SELECT rating FROM userleveldata WHERE (level = '$safeLevel' AND user = '$username' );";
	$sth = $dbh->prepare($sql);
	if( $sth->execute() ){

		if( $sth->rows ==1 ){
			my ($rating) = $sth->fetchrow_array();
			my @scoreStr = ("-1", "0" , "+1");
	

		
			if( $rating < 0 ){
				$rateHTML = $noRatingHTML;
			} else {
				$rateHTML = qq{You rated this level $scoreStr[$rating]. <a href="javascript:rate(-1);">Undo</a>};
			}
		} else {
			$rateHTML = $noRatingHTML;
		}
	} else {
		$rateHTML = "Error loading level rating";
	}


	# create post review form
	$reviewForm = <<REVIEW_FORM;
	<form action="/">
		<textarea name="content" rows="8" cols="48"></textarea><br />
		<input type="button" value="Post" onClick="post(content.value);" />
	</form>
REVIEW_FORM
	

} else {
	$rateHTML = "Log in to rate levels";
	$reviewForm = "<p>Log in to post a review.</p>";
}

my $reviewCount = 0;
# comments
my $reviews = "<p>Error loading reviews</p>";
if( database::create_table('levelcomments') ){
	$sql = "SELECT indexkey, author, content, postdate FROM levelcomments WHERE level = '$safeLevel' ORDER BY postdate DESC";
	my $rowSub = sub {
		my ($i, $array) = @_;
		my $htmlContent = common::removeHTML($$array[2]);
		my $htmlAuthor = common::removeHTML($$array[1]);
		my $escAuthor = CGI::escape($$array[1]);
		my $htmlDate = common::fmtsqldate($$array[3]);
		
		my $odd = $i % 2 == 0 ? '' : ' class="odd"';
		$reviewCount = $i if($i > $reviewCount);
		
		return qq{<div$odd><h4>$htmlDate by <a href="/user/$escAuthor">$htmlAuthor</a></h4>$htmlContent</div>};
	};
	
	my $navSub = sub {
		return "javascript:gotoPage($_[0]);";
	};
	
	my $x = database::html_sql_join($sql, $rowSub, 0, $navSub, $reviewLimit, 0, "<p>No one has posted a review for this level yet.</p>");
	$reviews = $x if( $x);
	
}

# javascript
my $js = <<JAVA_SCRIPT;
var reviewCount = $reviewCount;
var styleOdd = ' class="odd"';

function rate(score) {
	var xmlHttp = newAjax();

	xmlHttp.onreadystatechange = function(){
		if( xmlHttp.readyState == 4){
			objById("rate").innerHTML = xmlHttp.responseText;
		}
	}


	xmlHttp.open("GET", "../rate.cgi?level=$escLevel&score="+score ,true);
	xmlHttp.send(null);
}

function post(review) {
	var xmlHttp = newAjax();
	
	var rfHTML = objById("reviewform").innerHTML;
	objById("reviewform").innerHTML = "<p>Posting your review...<\\/p>";

	xmlHttp.onreadystatechange = function(){
		if( xmlHttp.readyState == 4){
			if( xmlHttp.responseText == 1 ){
				//success
				objById("reviewform").innerHTML = rfHTML;
				objById("reviews").innerHTML = '<div' + (reviewCount % 2 == 0 ? '' : styleOdd )  + '><h4>Just now by <a href="/user/$escUser">$htmlUser<\\/a><\\/h4>' + removeHTML(review) + '<\\/div>' + objById("reviews").innerHTML;
				reviewCount++;
			} else {
				objById("reviewform").innerHTML = "<p>Error posting review.<\\/p>";
			}
		}
	}


	xmlHttp.open("GET", "../post.cgi?level=$escLevel&review="+escape(review) ,true);
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

my $editText = "";
if( $username eq $author ) {
	$editText = qq{<span class="edit"><a href="/edit/$escLevel">(edit)</a></span>};
} 

# create body html
my $body = <<BODY_HTML;

<div id="gameinfo">
	$editText<h3>Level Info</h3>
	Author: <a href="/user/$escAuthor">$htmlAuthor</a><br />
	Length: $htmlLength <br />
	Difficulty: $htmlDifficulty <br />
	Rating: $htmlRating <br />
	<br />
	<div id="gamedesc">
		$htmlComments
	</div>
	<p>$stageInstructions</p>
</div>

<div id="game">
	<h2><span class="supertext"><a href="$downLink">Download ($sizeStr)</a></span>$htmlTitle</h2>
   <object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0" width="550" height="400">
   <param name="movie" value="stinkogame.swf">
   <param name="quality" value="low">
   <embed src="stinkogame.swf" quality="low" width="550" height="400" name="video" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer">
   </embed>
   </object>
   <div id="rate">$rateHTML</div>
</div>

<div id="comments">
	<h3>Level Reviews</h3>
	<div id="reviews">
		$reviews
	</div>
	<h3>Post a Review</h3>
	<div id="reviewform">
		$reviewForm
	</div>
</div>
BODY_HTML


print templates::mainpage("$htmlTitle - Custom Stinkoman Levels","",$body,$js);

sub invalid {
	my $msg = shift;
	warn "tried to play $level ";
	print templates::mainpage("Play level - Custom Stinkoman Levels", "", "<p>$msg</p>");
	exit(0);
}

sub bail {
	my $msg = shift;
	print templates::mainpage("Error playing level - Custom Stinkoman Levels", "", "<p>$msg</p>");
	exit(1);
}
