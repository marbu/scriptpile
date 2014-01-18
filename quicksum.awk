#!/usr/bin/awk -f
BEGIN { sum = 0 }
/[0-9\.\,]+/ {
	sub(",", ".", $0);
	sum += $0;
}
END { print sum }
