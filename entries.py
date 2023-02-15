def getEntry(text):
	entries = {
		"sin(𝑥)":"math.sin( ` )",
		"cos(𝑥)":"math.cos( ` )",
		"tan(𝑥)":"math.tan( ` )",
		"asin(𝑥)":"math.asin( ` )",
		"acos(𝑥)":"math.acos( ` )",
		"atan(𝑥)":"math.atan( ` )",
		"sinh(𝑥)":"math.sinh( ` )",
		"cosh(𝑥)":"math.cosh( ` )",
		"tanh(𝑥)":"math.tanh( ` )",
		"degrees(𝑥)":"math.degrees( ` )",
		"radians(𝑥)":"math.radians( ` )",

		"+":" + `",
		"-":" - `",
		"×":" * `",
		"÷":" / `",
		"%":" % `",
		"√":"math.sqrt( ` )",
		"^":" ** `",
		"//":" // `",

		"(":"( `",
		")":" )`",

		"𝑥":"x`",
		"π":"math.pi`",
		"𝑒":"math.e`",
		"τ (tau)":"math.tau`",

		"ceil(𝑥)":"math.ceil( ` )",
		"floor(𝑥)":"math.floor( ` )",
		"abs(𝑥)":"abs( ` )",
		"logn(𝑥)":"math.log10( ` )",
		"random(start, stop)":"random.randrange(`,9)",
		"uniform(start, stop)":"random.uniform(`,9)",
		"round(𝑥,n)":"round(x,`)"
	}
	return entries[text]
