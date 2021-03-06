def getEntry(text):
	entries = {
		"sin(๐ฅ)":"math.sin( ` )",
		"cos(๐ฅ)":"math.cos( ` )",
		"tan(๐ฅ)":"math.tan( ` )",
		"asin(๐ฅ)":"math.asin( ` )",
		"acos(๐ฅ)":"math.acos( ` )",
		"atan(๐ฅ)":"math.atan( ` )",
		"sinh(๐ฅ)":"math.sinh( ` )",
		"cosh(๐ฅ)":"math.cosh( ` )",
		"tanh(๐ฅ)":"math.tanh( ` )",
		"degrees(๐ฅ)":"math.degrees( ` )",
		"radians(๐ฅ)":"math.radians( ` )",

		"+":" + `",
		"-":" - `",
		"ร":" * `",
		"รท":" / `",
		"%":" % `",
		"โ":"math.sqrt( ` )",
		"^":" ** `",
		"//":" // `",

		"(":"( `",
		")":" )`",

		"๐ฅ":"x`",
		"ฯ":"math.pi`",
		"๐":"math.e`",
		"ฯ (tau)":"math.tau`",

		"ceil(๐ฅ)":"math.ceil( ` )",
		"floor(๐ฅ)":"math.floor( ` )",
		"abs(๐ฅ)":"abs( ` )",
		"logn(๐ฅ)":"math.log10( ` )",
		"random(start, stop)":"random.randrange(`,9)",
		"uniform(start, stop)":"random.uniform(`,9)",
		"round(๐ฅ,n)":"round(x,`)"
	}
	return entries[text]
