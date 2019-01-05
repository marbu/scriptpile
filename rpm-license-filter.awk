/^Name.*/, /^Description.*/ {
	if ($1 == "Name") {
		name = $3
	}
	if ($1 == "License" && $3 == license_id) {
		print name;
	}
}
