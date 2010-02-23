#!/usr/bin/perl -wT

use strict;

use lib ("/home/superjoe/perl_modules");

use CGI;

use database;
use templates;


#grab cookies!
my $query = CGI->new();
my $session = $query->cookie("session");

my $body;
	
if( database::user_logged_in($session) ){
	$body = <<BODY_HTML;
<h2>Submit a new Stinkoman level</h2>
<form enctype="multipart/form-data" action="upload" method="post">
    <table class="layout">
      <tr>
        <td align="right">
          Level Title:
        </td>
        <td>
          <input type="text" name="title" value="" maxlength="32" />
        </td>
      </tr>
      <tr>
        <td align="right">
          Level Stage:
        </td>
        <td>
          <select name="stage">
            <optgroup label="Level 1: Go Home!">
              <option value="1.1" selected>Stage 1.1</option>
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
        </td>
      </tr>
      <tr>
        <td align="right">
          Level Difficulty:
        </td>
        <td>
          <select name="difficulty">
           <option value="-2">Very Easy</option>
           <option value="-1">Easy</option>
           <option value="0" selected="selected">Medium</option>
           <option value="1">Hard</option>
           <option value="2">Very Hard</option>
          </select>
        </td>
      </tr>
      <tr>
        <td align="right">
          Level Length:
        </td>
        <td>
          <select name="length">
           <option value="-1">Short</option>
           <option value="0" selected="selected">Medium</option>
           <option value="1">Long</option>
          </select>
        </td>
      </tr>
      <tr><td colspan="2">&nbsp;</td></tr>
      <tr>
        <td align="right">
          Short description:
        </td>
        <td>
          <textarea name="comments" rows="6" cols="32"></textarea>
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
                <textarea name="xmlcode" rows="12" cols="30"></textarea>
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
BODY_HTML
} else {
	$body = <<BODY_HTML;
<h2>Submit a new Stinkoman level</h2>
<p>You must register an account to upload a new level. It's free and we don't require much information. <a href="register">Join</a></p>
<p>If you already have an account, use the log in button above!</p>
BODY_HTML
}

print templates::mainpage("Submit a new level - Custom Stinkoman Levels","",$body);

