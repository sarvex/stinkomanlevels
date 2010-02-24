package common;

our $VERSION = '1.0';


my @abbrmonths = qw(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec);

sub round {
  my($number,$digits) = @_;
  if(defined $digits && $digits > 0){
    return round($number*(10**$digits)) / (10**$digits);
  } else {
    return int($number + .5 * ($number <=> 0));
  }
}

sub ceiling {
	my( $number ) = @_;
	return $number == int($number) ? $number : int($number+1) ;
}


sub removeHTML {
  my $string = $_[0];

  #change html codes
  $string =~ s/\&/&amp;/g; #must be first
  
  $string =~ s/\"/&quot;/g;
  $string =~ s/  /&nbsp;&nbsp;/g;
  $string =~ s/\</&lt;/g;
  $string =~ s/\>/&gt;/g;

  return $string;
}


sub escapeChar {
  my ($string,$char) = @_;
  
  my $safeChar = quotemeta($char);
	$string =~ s/$safeChar/\\$char/g;
  
  return $string;
}

sub sizeString {
	my $size = shift;
	
	if($size < 1024){ #bytes
		$size .= " bytes";
	} elsif( $size < 1024*1024){ #kilobytes
		$size = round($size / 1024,1) . " KB";
	} elsif( $size < 1024*1024*1024){ #megabytes
		$size = round($size / (1024*1024),2) . " MB";
	} else { #gigabytes
		$size = round($size / (1024*1024*1024),2) . " GB";
	}
	
	return $size;
}

sub fmtsqldate {
	my ($sqldate) = @_;
	
	my ($y,$m,$d) = $sqldate =~ m/(\d{4})-(\d{2})-(\d{2})/;
	
	return "$abbrmonths[$m-1] $d, $y";
	

}

1;
