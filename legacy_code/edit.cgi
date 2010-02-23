#!/usr/bin/perl -wT

use strict;

use lib ("/home/superjoe/perl_modules");

use CGI;

use database;
use templates;
use common;


my $query = CGI->new();

#my $level = $query->param('level');
my $level;

#get from uri
if( ! defined $level){	
	($level) =  $ENV{REQUEST_URI} =~ m/\/edit\/(.*)$/ ;
	$level = CGI::unescape($level) if( defined $level);
}

my $session = $query->cookie("session");
if( ! defined $session || $session eq "" ) {
	$session = database::create_hash(32);
	templates::setSession($session);
}
my $username = database::user_logged_in($session);


# validate level
invalid('The level you are trying to play does not exist. Try <a href="/browse">browsing</a> for levels to play.') if( ! defined $level || $level eq "");

my $safeLevel = database::protect_string($level);
my $escLevel = CGI::escape($level);
my $htmlLevel = common::removeHTML($level);
# get info from database about level


my $sql = "SELECT majorstage, minorstage, difficulty, length, author, comments, file, datecreated FROM levels WHERE title = '$safeLevel'";
my $dbh = database::dbconnect();
my $sth = $dbh->prepare($sql);

invalid('Error loading data about that level. Please try again later.') if( ! $sth->execute() || $sth->rows == 0 );

my($major, $minor, $diff, $length, $auth, $comments, $file, $date) = $sth->fetchrow_array();

invalid('You can only edit your own levels') if( $username ne $auth);
	

if( ! open(FILE, "levels/$file") ){
	warn "Error opening $file: $!";
	invalid('Error opening file');
}
my $xml = join("\n", <FILE>);
close(FILE);


my $stageDropDown = <<STAGE_DROPDOWN;
<select name="stage">
            <optgroup label="Level 1: Go Home!">
              <option value="1.1">Stage 1.1</option>
              <option value="1.2">Stage 1.2</option>
            </optgroup>
            <optgroup label="Level 2: Pick a Bone!">
              <option value="2.1">Stage 2.1</option>
              <option value="2.2">Stage 2.2</option>
            </optgroup>
            <optgroup label="Level 3: Dumb Wall!">
              <option value="3.3">Stage 3.3</option>
            </optgroup>
            <optgroup label="Level 4: Fisticuff!">
              <option value="4.1">Stage 4.1</option>
              <option value="4.2">Stage 4.2</option>
              <option value="4.3">Stage 4.3</option>
            </optgroup>
            <optgroup label="Level 5: Oh, the Moon!">
              <option value="5.1">Stage 5.1</option>
              <option value="5.2">Stage 5.2</option>
              <option value="5.3">Stage 5.3</option>
            </optgroup>
            <optgroup label="Level 6: Stratosfear!">
              <option value="6.1">Stage 6.1</option>
              <option value="6.2">Stage 6.2</option>
              <option value="6.3">Stage 6.3</option>
            </optgroup>
            <optgroup label="Level 7: Ice 2 Meet U">
              <option value="7.1">Stage 7.1</option>
              <option value="7.2">Stage 7.2</option>
              <option value="7.3">Stage 7.3</option>
            </optgroup>
            <optgroup label="Level 8: Negatory!">
              <option value="8.1">Stage 8.1</option>
              <option value="8.2">Stage 8.2</option>
              <option value="8.3">Stage 8.3</option>
            </optgroup>
            <optgroup label="Level 9: Turbolence!">
              <option value="9.1">Stage 9.1</option>
              <option value="9.2">Stage 9.2</option>
              <option value="9.3">Stage 9.3</option>
            </optgroup>
          </select>
STAGE_DROPDOWN

my $diffDropDown = qq{
<select name="difficulty">
           <option value="-2">Very Easy</option>
           <option value="-1">Easy</option>
           <option value="0">Medium</option>
           <option value="1">Hard</option>
           <option value="2">Very Hard</option>
          </select>
};

my $lengthDropDown = qq{
          <select name="length">
           <option value="-1">Short</option>
           <option value="0">Medium</option>
           <option value="1">Long</option>
          </select>
};

$stageDropDown =~ s/value\=\"$major\.$minor\"\>/value="$major.$minor" selected="selected">/;

$diffDropDown =~ s/value\=\"$diff\"\>/value="$diff" selected="selected">/;

$lengthDropDown =~ s/value\=\"$length\"\>/value="$length" selected="selected">/;

my $html = <<EDIT_HTML;
<h2>Editing $htmlLevel</h2> 
<form enctype="multipart/form-data" action="/upload" method="post">
	<input type="hidden" name="title" value="$htmlLevel">
    <table class="layout">
      <tr>
        <td align="right">
          Level Title:
        </td>
        <td>
         <p>You can't change this because it would change the URL of the level, and people might have linked to it.</p> 
        </td>
      </tr>
      <tr>
        <td align="right">
          Level Stage:
        </td>
        <td>
		$stageDropDown
          </td>
      </tr>
      <tr>
        <td align="right">
          Level Difficulty:
        </td>
        <td>
		$diffDropDown
       </td>
      </tr>
      <tr>
        <td align="right">
          Level Length:
        </td>
        <td>
		$lengthDropDown 
	</td>
      </tr>
      <tr><td colspan="2">&nbsp;</td></tr>
      <tr>
        <td align="right">
          Short description:
        </td>
        <td>
          <textarea name="comments" rows="6" cols="32">$comments</textarea>
        </td>
      </tr>
      <tr>
        <td colspan="2">
          &nbsp;
        </td>
      </tr>
      <tr>
        <td colspan="2">
          <p>
            Now, paste XML code into the box or provide the filename of the level.
          </p>
        </td>
      </tr>
      <tr>
        <td colspan="2">
          <table class="layout">
            <tr>
              <td>
                <textarea name="xmlcode" rows="12" cols="30">$xml</textarea>
              </td>
              <td>
                <input type="file" name="xmlfile" />
              </td>
            </tr>
          </table>
        </td>
      </tr>
      <tr>
        <td colspan="2" align="center">
          <input type="submit" value="Upload" /> 
        </td>
      </tr>
    </table>
  </form>



EDIT_HTML




print templates::mainpage("Edit level - Custom Stinkoman Levels", "", $html);




sub invalid {
	my $msg = shift;
	warn "tried to edit $level ";
	print templates::mainpage("Edit level - Custom Stinkoman Levels", "", "<p>$msg</p>");
	exit(0);
}

