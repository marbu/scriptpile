/^Name.*/, /^Description.*/ {
	if ($1 == "Name") {
		name = $3
	}
	if ($1 == "License" && $3 == "GPLv2") {
		print name;
	}
}
