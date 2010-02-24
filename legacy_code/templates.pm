package templates;

our $VERSION = '1.0';

use lib ("/home/superjoe/perl_modules");

use CGI;

use database;

my $query = CGI->new();

my $session = 0;

sub title {
	return "Custom Stinkoman Levels";
}

sub setSession {
	$session = shift;
}

sub mainpage { 
	my ($title,$head,$body,$js,$cookiesRef,$cgitype) = @_;
	
	#to avoid uninitialized string warnings
	$js   = "" if( ! defined $js);	
	$body = "" if( ! defined $body);	
	$head = "" if( ! defined $head);
	$title= "Custom Stinkoman Levels" if( ! defined $title);
	$cgitype = "text/html" if(! defined $cgitype);
	
	my @cookies;
	@cookies = @$cookiesRef if( $cookiesRef);
	
	#grab session cookie unless explicitly defined
	if( ! $session){
		$session = $query->cookie("session");
	
		if( ! defined $session || $session eq ""){
			# create a new session variable
			$session = database::create_hash(32);
			push( @cookies, $query->cookie(-name => 'session', -value => $session, -path => "/"));
		}
	} elsif( $session ne $query->cookie("session")) {
		# session was explicitly defined and different than session, change session cookie
		push( @cookies, $query->cookie(-name => 'session', -value => $session, -path => "/"));
	}
	
	#get username from session
	my $username = database::user_logged_in($session);
	
	
	my $loggedOutHTML = '<ul><li><a href="javascript:login();">Log in</a></li> <li><a href="/register">Register</a></li></ul>';
	my $loggedInHTML  = qq{<ul><li><a href="/user/$username">$username</a></li> <li><a href="/dashboard">Dashboard</a></li> <li><a href="javascript:logout();">Log out</a></li></ul>};
	my $loggedInJS    = qq{'<ul><li><a href="/user/' + user + '">' + user + '<\\/a><\\/li> <li><a href="/dashboard">Dashboard<\\/a><\\/li> <li><a href="javascript:logout();">Log out<\\/a><\\/li><\\/ul>'};
	my $loggedOutJS = '<ul><li><a href="javascript:login();">Log in<\\/a><\\/li> <li><a href="/register">Register<\\/a><\\/li><\\/ul>';
	
	my $loginFormJS = qq{'<table><tr><td>Username:<\\/td><td><input type="text" name="user" id="user" value=""  maxlength="24" /><\\/td><\\/tr><tr><td>Password:<\\/td><td><input type="password" name="pass" id="pass" value=""  maxlength="32" /><\\/td><\\/tr><tr><td>&nbsp;<\\/td><td><input type="checkbox" name="remember" id="remember" value="1" /> Remember me<\\/td><\\/tr><tr><td colspan="2"><input type="button" name="submit" value="Sign in" onClick="sendLoginRequest();" /><\\/td><\\/tr><\\/table>'};
	
	my $ajaxLoginHTML = $username ? $loggedInHTML : $loggedOutHTML ;
	
	my $onlineUsers = database::online_users();
	$onlineUsers = "none" if( ! $onlineUsers);
	
	return CGI::header(-type => $cgitype, -cookie => \@cookies ) . <<MAIN_PAGE;
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
   "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
	<title>$title</title>
	<link rel="stylesheet" type="text/css" href="/style.css" />
	<link rel="shortcut icon" href="/favicon.ico" type="image/x-icon" />
	
	<script type="text/javascript" language="JavaScript" src="/common.js"></script>
	
	<script type="text/javascript" language="JavaScript"><!--
	
	
	
	
	function login() {
		objById("login").innerHTML = $loginFormJS;
	}
	
	function logout() {
		var xmlHttp = newAjax();
		
		xmlHttp.onreadystatechange = function(){
			if( xmlHttp.readyState == 4){
				if( xmlHttp.responseText == 1 )
					objById("login").innerHTML = '$loggedOutJS';
				else
					alert("Error logging out");
			}
		}
		
		xmlHttp.open("GET", "/logout.cgi", true);
		xmlHttp.send(null);
	}
	
	function sendLoginRequest() {
		var xmlHttp = newAjax();
		
		var user = objById("user").value;
		var pass = objById("pass").value;
		var remember = objById("remember").value;
		
		xmlHttp.onreadystatechange = function(){
			if( xmlHttp.readyState == 4){
				if( xmlHttp.responseText.substring(0,1) == "#" ){
					alert("Unable to log in: "+xmlHttp.responseText.substring(1,xmlHttp.responseText.length));
				} else {
					objById("login").innerHTML = $loggedInJS;
				}
			}
		}
		
	
		xmlHttp.open("GET", "/login.cgi?name="+escape(user)+"&pass="+escape(pass)+"&remember="+escape(remember) ,true);
		xmlHttp.send(null);
	}


	$js
	//--></script>
	
	$head
</head>
<body>
	<div id="wrapper">
		<div id="menu">
			<h1>Custom Stinkoman Levels</h1>
			<div id="nav">
				<ul>
					<li><a href="/">Home</a></li>
					<li><a href="/browse">Browse</a></li>
					<li><a href="/submit">Submit</a></li>
					<li><a href="/download">Download</a></li>
				</ul>
			</div>
			<div id="login">
				$ajaxLoginHTML
			</div>
		</div>
		<div id="content">
			$body
		</div>
		<div id="copy">
			<div>
				Current users online: $onlineUsers
			</div>
			<br />
			<div>
				&copy; 2008 <a href="http://www.superjoesoftware.com/">Superjoe Software</a>
			</div>
			<div>
				Stinkoman is owned and copyrighted by <a href="http://www.homestarrunner.com">Homestar Runner</a>. See the <a href="http://www.homestarrunner.com/stinkogame/v7/stinkogame.html">original game</a>.
			</div>
		</div>
	</div>
</body>
</html>	
MAIN_PAGE
	
}



1;
