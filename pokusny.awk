BEGIN { NUM = 1; }
/^stream$/ { OUT = "pokusny."NUM; NUM = NUM + 1; }
/^stream$/,/^endstream$/ {
	if ( ($1 == "stream") || ($1 == "endstream") )
		next;
	print $1 >> OUT;
}
