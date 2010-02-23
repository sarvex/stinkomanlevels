#!/usr/bin/perl -wT

use strict;


use lib ("/home/superjoe/perl_modules");


use CGI;

use templates;



my $body = <<MAIN_HTML;
<h2>Download the Stinkoman Level Editor</h2>
<div class="wrapblock">
	<div class="block">
		<h3>Windows</h3>
		<br />
		<a href="/StinkomanLE-9.4.1.exe">Setup 9.4.1</a> - 7 MB
	</div>
	<div class="block">
		<h3>Mac</h3>
		<p>Under development</p>
	</div>
	<div class="block">
		<h3>Linux</h3>
		<p>Under development</p>
	</div>
</div>
<div class="clear">&nbsp;</div>
<p>This is the Stinkoman Level Editor. Use it to create levels and upload them here! I'm really busy with other stuff, but if I get a ton of emails wanting me to port it to Mac and Linux, I will do that. Hopefully, The Brothers Chaps release level 10 sometime soon!</p>

<h2>Download a custom made level</h2>
<p>To download a level, <a href="/browse">browse</a> through the levels to find one and then click on its name. Next look for the download link to the right of the page.</p>
MAIN_HTML

print templates::mainpage("Download the level editor - Custom Stinkoman Levels","",$body);

