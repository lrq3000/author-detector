#!/usr/local/bin/perl

########################################################################
#                                                                      #
#  tokenisation script for tagger preprocessing                        #
#  Author: Helmut Schmid, IMS, University of Stuttgart                 #
#                                                                      #
#  Description:                                                        #
#  - splits input text into tokens (one token per line)                #
#  - cuts off punctuation, parentheses etc.                            #
#  - cuts of clitics like n't in English                               #
#  - disambiguates periods                                             #
#  - preserves SGML markup                                             #
#  - reads the whole file at once and should therefore not be called   #
#    with very large files                                             #
#                                                                      #
########################################################################

use Getopt::Std;
getopts('hfeia:');

# Modify the following lines in order to adapt the tokeniser to other
# types of text and/or languages

# characters which have to be cut off at the beginning of a word
my $PChar='[{(\´\`"»«\202\204\206\207\213\221\222\223\224\225\226\227\233';

# characters which have to be cut off at the end of a word
my $FChar=']}\'\`\"),;:\!\?\%»«\202\204\205\206\207\211\213\221\222\223\224\225\226\227\233';

# character sequences which have to be cut off at the beginning of a word
my $PClitic='';

# character sequences which have to be cut off at the end of a word
my $FClitic;

if (defined($opt_e)) {
  # English
  $FClitic = '\'(s|re|ve|d|m|em|ll)|n\'t';
}
if (defined($opt_i)) {
  # Italian
  $PClitic = '[dD][ae]ll\'|[nN]ell\'|[Aa]ll\'|[lLDd]\'|[Ss]ull\'|[Qq]uest\'|[Uu]n\'|[Ss]enz\'|[Tt]utt\'';
}
if (defined($opt_f)) {
  # French
  $PClitic = '[dcjlmnstDCJLNMST]\'|[Qq]u\'|[Jj]usqu\'|[Ll]orsqu\'';
  $FClitic = '-t-elles?|-t-ils?|-t-on|-ce|-elles?|-ils?|-je|-la|-les?|-leur|-lui|-mêmes?|-m\'|-moi|-nous|-on|-toi|-tu|-t\'|-vous|-en|-y|-ci|-là';
}


### NO MODIFICATIONS REQUIRED BEYOND THIS LINE #########################

if (defined($opt_h)) {
  die "
Usage: tokenize.perl [ options ] ...files...

Options:
-e : English text 
-f : French text
-i : Italian text
-a <file>: <file> contains a list of words which are either abbreviations or
           words which should not be further split.
";
}

# Read the list of abbreviations and words
if (defined($opt_a)) {
  die "file not found: $opt_a\n"  unless (open(FILE, $opt_a));
  while (<FILE>) {
    s/^[ \t\r\n]+//;
    s/[ \t\r\n]+$//;
    next if (/^\#/ || /^\s$/);   # ignore comments
    $Token{$_} = 1;
  }
  close FILE;
}

# read the whole file at once
undef $/;
$_ = <>;

# replace newlines and tab characters with blanks
tr/\n\t/  /;

# replace blanks within SGML tags
while (s/(<[^<> ]*) ([^<>]*>)/$1\377$2/g) {};

# replace whitespace with a special character
tr/ /\376/;

# restore SGML tags
tr/\377\376/ \377/;

# prepare SGML-Tags for tokenisation
s/(<[^<>]*>)/\377$1\377/g;
s/^\377//;
s/\377$//;
s/\377\377\377*/\377/g;

@S = split("\377");
for( $i=0; $i<=$#S; $i++) {
  $_ = $S[$i];
  
  if (/^<.*>$/) {
    # SGML tag
    print $_,"\n";
  }
  else {
    # add a blank at the beginning and the end of each segment
    $_ = ' '.$_.' ';
    # insert missing blanks after punctuation
    s/(\.\.\.)/ ... /g;
    s/([;\!\?])([^ ])/$1 $2/g;
    
    @F = split;
    for( $j=0; $j<=$#F; $j++) {
      my $suffix="";
      $_ = $F[$j];
      # separate punctuation and parentheses from words
      do {
	$finished = 1;
	# cut off preceding punctuation
	if (s/^([$PChar])(.)/$2/) {
	  print $1,"\n";
	  $finished = 0;
	}
	# cut off trailing punctuation
	if (s/(.)([$FChar])$/$1/) {
	  $suffix = "$2\n$suffix";
	  $finished = 0;
	}
	# cut off trailing periods if punctuation precedes
	if (s/([$FChar])\.$//) { 
	  $suffix = ".\n$suffix";
	  if ($_ eq "") {
	    $_ = $1;
	  }
	  else {
	    $suffix = "$1\n$suffix";
	  }
	  $finished = 0; 
	}
      }	while (!$finished);
                
      # handle explicitly listed tokens
      if (defined($Token{$_})) {
	print "$_\n$suffix";
	next;
      }
                
      # abbreviations of the form A. or U.S.A.
      if (/^([A-Za-zÁÂÃÈý®Ð×ÝÞÍðÎÓÔÕØÙãõš›€ß‚ƒ„‡ˆ‰Š‹ŒŽøŸ÷·”“’]\.)+$/) {
	print "$_\n$suffix";
	next;
      }
                 
      # disambiguate periods
      if (/^(..*)\.$/ && $_ ne "..." && !/^[0-9]+\.$/) {
	$_ = $1;
	$suffix = ".\n$suffix";
	if (defined($Token{$_})) {
	  print "$_\n$suffix";
	  next;
	}
      }
                 
      # cut off clitics
      if ($PClitic ne '') {
	while (s/^($PClitic)(.)/$2/) {
	  print $1,"\n";
	}
      }
      if ($FClitic ne '') {
	while (s/(.)($FClitic)$/$1/) {
	  $suffix = "$2\n$suffix";
	}
      }
                 
      print "$_\n$suffix";
    }
  }
}
