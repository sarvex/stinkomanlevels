#!/usr/bin/perl -wT

use strict;

# add extra perl modules (this is for MIME::Lite)
BEGIN {
     my $homedir = (getpwuid($>))[7];
     my $n_inc = scalar @INC;
     for (my $i = 0; $i < $n_inc; $i++ ) {
		  if (-d $homedir . '/perl' . $INC[$i]) {
			   unshift(@INC,$homedir . '/perl' . $INC[$i]);
			   $n_inc++;
			   $i++;
		  }
     }
}

use lib ("/home/superjoe/perl_modules");

use CGI;

# for sending emails
use MIME::Lite::TT::HTML;
use MIME::Lite;

use templates;
use database;

my $query = CGI->new();

my $name  = $query->param('name');
my $email = $query->param('email');
my $pass  = $query->param('pass');
my $action= $query->param('action');

my $msg = "";
my $outputform = 1;

if( defined $action ){
	#validate parameters
	if(! defined $name || $name =~ m/[^a-zA-Z0-9_]/ || length($name) < 2 || length($name) > 32 ){
		$msg = '<div class="err">Invalid submission. Please check your screen name and try again.</div>';
	} elsif( ! defined $email || index($email,"@") == -1 || index($email, ".") == -1 || length($email) < 7 || length($email) > 32 ) {
		$msg = '<div class="err">Invalid submission. Please check your email address and try again.</div>';
	} elsif( ! defined $pass || length($pass) < 4 || length($pass) > 32 ) {
		$msg = '<div class="err">Invalid submission. Please check your password and try again.</div>';
	} else {
		#see if screen name is available
		my $x = database::user_exists($name);
		if( $x == -1 ){
			$msg = '<div class="err">Sorry, there was an error processing your request. Please try again or come back later.</div>';
		} elsif ($x) {
			$msg = '<div class="err">The screen name you requested is taken already. Please use another one and try again.</div>';
		} else {
			$outputform = 0;
			
			#generate confirmation code
			my $code = database::create_hash(32);
			
			#add user to database
			database::add_user($name,$email,$pass,$code) || bail("There was an error creating your account. Please come back later and try again");
			
			#set up email template
			my %params;
			$params{screen_name}  = CGI::escape($name);
			$params{confirm_code} = CGI::escape($code);
			
			#send confirmation email
			my $emailMessage = MIME::Lite::TT::HTML->new(
		       From        => 'admin@superjoesoftware.com',
		       To          => $email,
		       Subject     => "Account Confirmation - Custom Stinkoman Levels",
		       Template    => {
		                         text    =>  'accountconfirm.txt.tt',
		                         html    =>  'accountconfirm.html.tt',
		                      },
		       Charset     => 'utf8',
		       TmplParams  => \%params,
		     );
		     
			# secure env{path}
			($ENV{PATH}) = $ENV{PATH} =~ m/(.*)/;

			if( ! $emailMessage->send ){
				warn "Error sending mail: $!";
				bail("There was an error sending you a confirmation email. Please come back later and try again.");
			}
		}
	}
}

my ($head, $body, $title, $js);

if( $outputform ) {
	$head = "";
	$js = <<JAVA_SCRIPT;
	
var imgCheck = new Image();
imgCheck.src = "/img/check.gif";
var imgInvalid = new Image();
imgInvalid.src = "/img/invalid.gif";

function checkName(screenname) {
	var xmlHttp = newAjax();
	
	xmlHttp.onreadystatechange = function(){
		if( xmlHttp.readyState == 4){
			objById("namecheck").innerHTML = xmlHttp.responseText;
		}
	}
	
	xmlHttp.open("GET", "namecheck.cgi?name="+escape(screenname), true);
	xmlHttp.send(null);
}

function checkEmail(email) {
	var x = email.indexOf("@");
	var y = email.indexOf(".");
	
	if( email.length < 7 || email.length > 32 || x == -1 || y == -1 || x > y )
		objById("emailcheck").innerHTML = '<img src="'+imgInvalid.src+'" /> invalid email address';
	 else 
		objById("emailcheck").innerHTML = '<img src="'+imgCheck.src+'" /> OK';
	
}

function checkPassword(pass) {
	
	if( pass.length < 4 )
		objById("passcheck").innerHTML = '<img src="'+imgInvalid.src+'" /> too short';
	else if( pass.length > 32 )
		objById("passcheck").innerHTML = '<img src="'+imgInvalid.src+'" /> too long';
	else
		objById("passcheck").innerHTML = '<img src="'+imgCheck.src+'" /> OK';
	
}

function checkConfirm(confirm, pass) {
	
	if( pass != confirm )
		objById("confirmcheck").innerHTML = '<img src="'+imgInvalid.src+'" /> passwords do not match';
	else
		objById("confirmcheck").innerHTML = '<img src="'+imgCheck.src+'" /> OK';
	
}

JAVA_SCRIPT

	$body = <<BODY_HTML;
<h2>Create an account</h2>
$msg
<form action="register" method="post">
	<table class="layout">
		<tr>
			<td>Screen name:</td>
			<td><input type="text" name="name" value="" maxlength="24" onChange="checkName(this.value);" /></td>
			<td><div id="namecheck">&nbsp;</div></td>
		</tr>
		<tr>
			<td>Email address:</td>
			<td><input type="text" name="email" value="" maxlength="32" onChange="checkEmail(this.value);" /></td>
			<td><div id="emailcheck">&nbsp;</div></td>
		</tr>
		<tr>
			<td colspan="3">
				&nbsp;
			</td>
		</tr>
		<tr>
			<td>
				Password: 
			</td>
			<td>
				<input type="password" name="pass" value="" maxlength="32" onChange="checkPassword(this.value);" />
			</td>
			<td>
				<div id="passcheck">&nbsp;</div>
			</td>
		</tr>
		<tr>
			<td>Confirm:</td>
			<td><input type="password" name="confirm" value="" maxlength="32" onChange="checkConfirm(this.value,pass.value);" /></td>
			<td><div id="confirmcheck">&nbsp;</div></td>
		</tr>
		<tr>
			<td colspan="3">&nbsp;</td>
		</tr>
		<tr>
			<td colspan="3"><input name="action" type="submit" value="OK" /></td>
		</tr>
	</table>
</form>
BODY_HTML

	$title = "Create an account - Custom Stinkoman Levels";

} else {
	
	$head = "";
	$js = "";
	
	$body = <<BODY_HTML;
<h2>Account created</h2>
<p>
	An email was sent to the address you provided to confirm your account. Please check your email right now!
</p>
BODY_HTML
	
	$title = "Account created - Custom Stinkoman Levels";
}

print templates::mainpage($title,$head,$body, $js);

sub bail {
	my $msg = shift;
	print templates::mainpage("Error - Custom Stinkoman Levels","","<p>$body</p>");
	exit(1);
}
