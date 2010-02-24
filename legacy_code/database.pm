package database;

our $VERSION = '1.0';

use lib ("/home/superjoe/perl_modules");

use DBI;

use common;


my $defaultLimit = 20; # for limiting sql queries



my $dbh;
my $connected = 0;

sub dbconnect {
	if( ! $connected ){
		$dbh = DBI->connect('DBI:mysql:superjoe_site:localhost','superjoe_andy','boobies27') || die "MySQL Connection Error: $DBI::errstr\n";
		$connected = 1;
	}
	return $dbh;
}

sub create_table {	
	my $which_table = shift;
	
	dbconnect() if( ! $connected );
	
	my %tables = ( 'users' =>  "CREATE TABLE IF NOT EXISTS users ( screenname VARCHAR(24) PRIMARY KEY, email VARCHAR(32), password VARCHAR(32), activated BOOLEAN DEFAULT false, activatecode VARCHAR(32), registerdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP, session VARCHAR(32) UNIQUE, lastlogin TIMESTAMP NOT NULL);",
						'levels' => "CREATE TABLE IF NOT EXISTS levels (title VARCHAR(32) PRIMARY KEY, majorstage INT NOT NULL, minorstage INT NOT NULL, difficulty INT NOT NULL, length INT NOT NULL, author VARCHAR(24), comments VARCHAR(512), file VARCHAR(256), datecreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,ratecount INT NOT NULL DEFAULT 0,ratetotal INT NOT NULL DEFAULT 0, lastplayed TIMESTAMP NOT NULL);",
					 	'levelsession' => "CREATE TABLE IF NOT EXISTS levelsession (session VARCHAR(32) PRIMARY KEY, level VARCHAR(32), modifydate TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
					 	'levelcomments' => "CREATE TABLE IF NOT EXISTS levelcomments (indexkey INT AUTO_INCREMENT PRIMARY KEY, level VARCHAR(32), author VARCHAR(32), content VARCHAR(512), postdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
					 	'userleveldata' => "CREATE TABLE IF NOT EXISTS userleveldata (indexkey INT AUTO_INCREMENT PRIMARY KEY,  level VARCHAR(32), user VARCHAR(32), rating INT NOT NULL DEFAULT -1, victory INT NOT NULL DEFAULT 0);",
					 	'usercomments' => "CREATE TABLE IF NOT EXISTS usercomments (indexkey INT AUTO_INCREMENT PRIMARY KEY, user VARCHAR(32), author VARCHAR(32), content VARCHAR(512), postdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
					 	'chesscomp' => "CREATE TABLE IF NOT EXISTS chesscomp (indexkey INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50), facebook VARCHAR(256), email VARCHAR(50), joindate TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"
					 );

	if( ! exists $tables{$which_table} ){
		warn "Possible typo in confirming table existence of '$which_table'.";
		return 0; #error
	}
	
	my $sql = $tables{$which_table};
	my $sth = $dbh->prepare($sql);
	if( $sth->execute() ){
		return 1; #success
	} else {
		warn "MySQL Error confirming that the '$which_table' table exists: $DBI::errstr";
		return 0; #error
	}
}

sub user_exists {	
	#determine if a user exists in the database
	my $user = shift;
	create_table('users') || return -1;
	
	my $safeUser = protect_string($user);
	my $sql = "SELECT screenname FROM users WHERE screenname = '$safeUser';";
	my $sth = $dbh->prepare($sql);
	if( $sth->execute() ){
		return ( $sth->rows > 0 );
	} else {
		warn "MySQL Error checking if '$user' exists: $DBI::errstr";
		return -1;
	}
}

sub add_user {
	#add a user to database, return success
	my ($name,$email,$pass,$code) = @_;
	
	create_table('users') || return 0;
	
	$name  = protect_string($name);
	$email = protect_string($email);
	$pass  = protect_string($pass);
	$code  = protect_string($code);
	
	
	my $sql = "INSERT INTO users (screenname, email, password, activatecode) VALUES ('$name', '$email', '$pass', '$code');";
	my $sth = $dbh->prepare($sql);
	if( $sth->execute() ){
		return 1;
	} else {
		warn "MySQL Error adding new user: $DBI::errstr";
		return 0;
	}
}

sub user_logged_in {
	# get a user name from session cookie
	my ($session) = @_;
	
	create_table('users') || return 0;
	return 0 if( length($session) != 32);
	
	$session = protect_string($session);
	
	my $sql = "SELECT screenname FROM users WHERE session = '$session';";
	my $sth = $dbh->prepare($sql);
	if( $sth->execute() ){
		if( $sth->rows == 1 ){
			my ($screenname) = $sth->fetchrow_array();
			
			# update last user login
			$sql = "UPDATE users SET lastlogin = CURRENT_TIMESTAMP WHERE session = '$session';";
			$sth = $dbh->prepare($sql);
			$sth->execute();
			
			return $screenname;
		} else {
			return 0;
		}
	} else {
		warn "MySQL Error checking if user is logged in: $DBI::errstr";
		return 0;
	}
}

sub log_user_in {
	my ($user,$pass) = @_;
	
	create_table('users') || return "#Unable to create the users table";
	
	$user = protect_string($user);
	$pass = protect_string($pass);
	
	my $hash = create_hash(32);
	
	my $sql = "UPDATE users SET session = '$hash', lastlogin = CURRENT_TIMESTAMP WHERE (screenname = '$user' AND password = '$pass' AND activated = true);";
	my $sth = $dbh->prepare($sql);
	if( $sth->execute() ){
		return ($sth->rows == 1 ) ? $hash : "#Invaild username or password";
	} else {
		warn "MySQL Error checking login credentials: $DBI::errstr";
		return "#Database error";
	}
}

sub log_user_out {
	my $session = shift;
	
	create_table('users') || return 0;

	$session = protect_string($session);
	
	my $sql = "UPDATE users SET session = ' ' WHERE session = '$session';";
	my $sth = $dbh->prepare($sql);
	if( $sth->execute() ){
		return 1;
	} else {
		return 0;
	}
}


sub create_hash {
	my $length = shift;
	
	my @chars = ('a'..'z', 'A'..'Z', '0'..'9');
	my $code = "";
	for( my $i=1;$i<=$length;$i++ ){
		$code .= $chars[int(rand() * @chars)];
	}
	return $code;
}


sub protect_string {
	#make sure syntax won't mess up sql
	return common::escapeChar( shift ,"'");
}




sub html_sql_table {
	my($sql, $sub, $offset, $navSub, $headings, $limit, $noNav, $default) = @_;
	
	$limit = $defaultLimit if(! defined $limit);
	$noNav = 0 if( ! defined $noNav);
	$default = qq{<tr><td colspan="} . scalar(@$headings) . qq{">No rows returned</td></tr></table>} if(! defined $default); 
	
	my $newSub = sub {
		my ($i, $array) = @_;
		my $trclass = $i % 2 == 0 ? ' class="odd"' : '';
		return "<tr$trclass><td>" . join( "</td><td>" , &$sub(@$array))  . "</td></tr>"; 
	};
	
	my ($tableHTML, $navHTML) = html_sql_join($sql,$newSub, $offset, $navSub, $limit, $noNav, $default, 1  );
	
	return "$navHTML<table><tr><th>" . join( "</th><th>" , @$headings) . "</th></tr>" . $tableHTML . "</table>$navHTML";
}

sub html_sql_join {
	my($sql, $sub, $offset, $navSub, $limit, $noNav, $default, $yesTable) = @_;
	
	
	
	# execute sql without the limit to see how many rows are returned
	dbconnect() || return 0;
	my $sth = $dbh->prepare("$sql;");
	$sth->execute() || return 0;
	
	my $totalRows = $sth->rows;
	my $tableHTML = $head;
	
	# now execute the real one
	$sth = $dbh->prepare("$sql LIMIT $limit OFFSET $offset;");
	$sth->execute() || return 0;
	
	# build the table
	if( $sth->rows > 0 ){
		my $i = 0;
		while( my @data = $sth->fetchrow_array() ){
			$tableHTML .= &$sub($i,\@data);
			$i++;
		}
	} else {
		$tableHTML = $default;
	}
	
	# navigation
	my $navHTML = "";
	
	if( ! $noNav) {
		my $numPages = common::ceiling($totalRows / $limit);
		my $curPage = int($offset / $limit)+1;
	
		if( $numPages > 1 ){
	
			# first and previous page
			if( $curPage > 1 ){
				$navHTML .= '<a href="' . &$navSub(0)  .  '">&lt;&lt;</a> <a href="' . &$navSub( ($curPage-2) * $limit ) . '">prev</a>';
			}
	
			# numbers
			for(my $i=$curPage-2; $i<=$curPage+2; $i++){
				if( $i >= 1 && $i <= $numPages ) {
					if( $i == $curPage ){
						$navHTML .= "$i ";
					} else {
						$navHTML .= '<a href="' . &$navSub( ($i-1) * $limit ) . qq{">$i</a> };
					}
				}
			}
	
			# next and last page
			if( $curPage < $numPages ){
				$navHTML .= '<a href="' . &$navSub( $curPage * $limit )  .  '">next</a> <a href="' . &$navSub( ($numPages-1) * $limit ) . '">&gt;&gt;</a>';
			}
		}
	}
	
	if( $yesTable ){
		return ($tableHTML, $navHTML);
	} else {
		return $navHTML . $tableHTML . $navHTML;
	}
	
}

sub online_users {
	# return a list of users who last logged in in the last 5 minutes
	create_table("users") || return 0;
	my $sql = "SELECT screenname FROM users WHERE TIMESTAMPDIFF(MINUTE, lastlogin, CURRENT_TIMESTAMP) < 10 LIMIT 30;";
	my $sth = $dbh->prepare($sql);
	$sth->execute() || return 0;
	my $str = "";
	while(my ($screenname) = $sth->fetchrow_array() ) {
		$str .= qq{<a href="/user/$screenname">$screenname</a> };
	}
	return $str;
}

1;
