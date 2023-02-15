import json

def readJson(path):
	f = open(path, 'r')
	file = json.load(f)
	f.close()
	return file

def writeJson(path, text):
	f = open(path, 'w')
	f.write(json.dumps(text, indent = 4))
	f.close()

def writeFile(path, text):
	f = open(path, 'w')
	f.write(text)
	f.close()

def toJson(dictionary):
	return json.dumps(dictionary)