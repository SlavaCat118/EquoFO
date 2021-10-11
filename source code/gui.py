from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import fileHandler as fh
import math
import numpy
import random
import entries

def main():

	root = Tk()
	root.title("EquaFO")
	root.resizable(width=False, height=False)
	root.geometry("+10+10")

	style = ttk.Style()
	style.theme_use('clam')
	
	root2 = ttk.Frame(root)
	root2.grid(row = 0, column = 0, sticky = NSEW)

	main = ttk.Frame(root2)
	main.grid(row = 0, column = 0, padx = 10, pady = (10,0))

	# Vars
	trigOptions = ['sin(𝑥)','cos(𝑥)','tan(𝑥)','asin(𝑥)','acos(𝑥)','atan(𝑥)','sinh(𝑥)','cosh(𝑥)','tanh(𝑥)','degrees(𝑥)','radians(𝑥)']
	operatorOptions = ['+','-','×','÷','%','√','^','//']
	symbolOptions = ['(',')']
	variableOptions = ['𝑥','π','𝑒','τ (tau)']
	miscOptions = ['ceil(𝑥)','floor(𝑥)','abs(𝑥)','logn(𝑥)','random(start, stop)', 'uniform(start, stop)', 'round(𝑥,n)']
	presets = fh.readJson("presets.json")
	presetOptions = list(presets.keys())
	canvasWidth = 650
	canvasHeight = 300

	#Images
	loadIcon = PhotoImage(file="icons/loadIcon.png")
	saveIcon = PhotoImage(file="icons/saveIcon.png")
	trashIcon = PhotoImage(file="icons/trashIcon.png")
	newIcon = PhotoImage(file="icons/newIcon.png")
	leftIcon = PhotoImage(file="icons/leftIcon.png")
	rightIcon = PhotoImage(file="icons/rightIcon.png")
	backspaceIcon = PhotoImage(file="icons/backspaceIcon.png")


	#Functions
	def fixEquation():
		toIndex = equation.get().find('`')
		eqHold = equation.get()
		equation.delete(0,END)
		equation.insert(0,eqHold.replace('`',''))
		equation.icursor(toIndex)
		setFocus(1)
	def addTrig():
		equation.insert(equation.index(INSERT), entries.getEntry(trigSelected.get()))
		fixEquation()
	def addOpe():
		equation.insert(equation.index(INSERT), entries.getEntry(OperatorSelected.get()))
		fixEquation()
	def addSym():
		equation.insert(equation.index(INSERT), entries.getEntry(SymbolSelected.get()))
		fixEquation()
	def addVar():
		equation.insert(equation.index(INSERT), entries.getEntry(VariableSelected.get()))
		fixEquation()
	def addMis():
		equation.insert(equation.index(INSERT), entries.getEntry(MiscSelected.get()))
		fixEquation()
	def addNum():
		equation.insert(equation.index(INSERT), NumberSelected.get().strip() + '`')
		fixEquation()
	def save():
		values = {"smooth":smooth.get(),"equation":equation.get().strip(), "range":[(eval(xStart.get().strip())), (eval(xEnd.get().strip())), (eval(yStart.get().strip())), (eval(yEnd.get().strip()))], 'resolution':resRead.get(),'xPhase':xPhase.get()}
		presets[name.get().strip()] = values
		fh.writeJson('presets.json', presets)
		preset.set(name.get().strip())
		updatePresets()
	def loade(e):
		load()
	def load():
		name.delete(0,END)
		name.insert(0, preset.get())
		smooth.set(presets[preset.get()]['smooth'])
		equation.delete(0,END)
		equation.insert(0,presets[preset.get()]['equation'])
		xStart.delete(0,END)
		xStart.insert(0,presets[preset.get()]['range'][0])
		xEnd.delete(0,END)
		xEnd.insert(0,presets[preset.get()]['range'][1])
		yStart.delete(0,END)
		yStart.insert(0,presets[preset.get()]['range'][2])
		yEnd.delete(0,END)
		yEnd.insert(0,presets[preset.get()]['range'][3])
		resRead.set(presets[preset.get()]['resolution'])
		xPhase.set(presets[preset.get()]['xPhase'])
		updatePreview()
	def deletePreset():
		if len(presets) > 1:
			presets.pop(preset.get())
			fh.writeJson('presets.json',presets)
			updatePresets()
	def updatePresets():
		presets = fh.readJson("presets.json")
		presetOptions = list(presets.keys())
		presetMenu = ttk.OptionMenu(header, preset, presetOptions[0], *presetOptions) 
		presetMenu.grid(row = 0, column = 5, sticky = W)
	def newPreset():
		name.delete(0,END)
		name.insert(0, "EquoFo LFO")
		smooth.set(True)
		equation.delete(0,END)
		equation.insert(0,'math.sin(x)')
		xStart.delete(0,END)
		xStart.insert(0,-10)
		xEnd.delete(0,END)
		xEnd.insert(0,10)
		yStart.delete(0,END)
		yStart.insert(0,-10)
		yEnd.delete(0,END)
		yEnd.insert(0,10)
		resRead.set(30)
		phaseRead.set(0)
		updatePreview()

	def getPoints(numPoints, xStart, xEnd, yStart, yEnd):
		xRange = abs(xEnd-xStart)
		xpoints = scaleToRange([i for i in range(numPoints)], 0, xRange)
		xpoints = [i+xStart for i in xpoints]

		ypoints = []
		try:
			for i in xpoints:
				x = i + xPhase.get()

				try:
					result = eval(equation.get())
				except ValueError:
					result = yStart
				
				if result < yStart:
					ypoints.append(yStart)
				elif result > yEnd:
					ypoints.append(yEnd)
				else:
					ypoints.append(result)
		except Exception:
			ypoints = [0 for i in range(len(xpoints))]
			lfoPreview.create_text(20,10, text = "Error", fill = 'red')

		if scaleY.get() == False:
			ypoints.extend([yStart, yEnd])

		points = {'x':xpoints,'y':ypoints}
		return points

	def scaleToRange(unscaled,range_start,range_end):
		scaled = numpy.ndarray.tolist(numpy.interp(unscaled, (min(unscaled), max(unscaled)), (range_start,range_end)))
		scaled = [round(i,3) for i in scaled]
		return scaled

	def updatePreview():
		try:
			points = getPoints(resRead.get(), (eval(xStart.get().strip())), (eval(xEnd.get().strip())), (eval(yStart.get().strip())), (eval(yEnd.get().strip())))

			xpoints = scaleToRange(points['x'],0,canvasWidth)
			ypoints = scaleToRange(points['y'],canvasHeight,0)

			canvasXAxis = scaleToRange([eval(yStart.get().strip()), 0, eval(yEnd.get().strip())],canvasHeight,0)
			canvasYAxis = scaleToRange([eval(xStart.get().strip()), 0, eval(xEnd.get().strip())], 0, canvasWidth)

			combined = []
			for i in range(len(xpoints)):
				combined.append(xpoints[i])
				combined.append(ypoints[i]+1)


			lfoPreview.delete("all")

			lfoPreview.create_text(canvasYAxis[1]+10, canvasHeight-10, text = eval(yStart.get().strip()))
			lfoPreview.create_text(canvasYAxis[1]+10, 10, text = eval(yEnd.get().strip()))
			lfoPreview.create_text(10, canvasXAxis[1]+10, text = eval(xStart.get().strip()))
			lfoPreview.create_text(canvasWidth-10, canvasXAxis[1]+10, text = eval(xEnd.get().strip()))
			lfoPreview.create_line(canvasYAxis[1], canvasXAxis[0], canvasYAxis[1], canvasXAxis[2], canvasYAxis[1], canvasXAxis[1], canvasWidth, canvasXAxis[1], 0, canvasXAxis[1], fill = 'red', width = 2, smooth = False)
			

			pW = 2
			if viewPoints.get() == True:
				for i in range(len(xpoints)):
					lfoPreview.create_oval(xpoints[i]-pW, ypoints[i]+pW, xpoints[i]+pW, ypoints[i]-pW, fill = 'black', outline = 'black')
			else:
				pass

			if viewHints.get() == True:
				lfoPreview.create_line(combined, fill = 'lightGrey', width = 1, smooth = False)

			lfoPreview.create_line(combined, fill = 'Black', width = 1, smooth = smooth.get())

		except Exception:
			lfoPreview.create_text(20,10, text = "Error")

	def	updateEvent(event):
		updatePreview()
		getLfo()

	def roundRes(event):
		resRead.set(round(float(resRead.get())))
		updatePreview()

	def roundPhase(event):
		phaseRead.set(round(float(phaseRead.get()), 5))
		updatePreview()

	def intEntryCallback(text):
		allowedChars = "1234567890-+/*."
		valid = True
		for i in text:
			if i not in allowedChars:
				valid = False
		if valid:
			return True
		else:
			return False

 	# {"name":"Triangle","num_points":3,"points":[0.0,1.0,0.5,0.0,1.0,1.0],"powers":[0.0,0.0,0.0],"smooth":false}

	def getLfo():
		points = getPoints(resRead.get(), (eval(xStart.get().strip())), (eval(xEnd.get().strip())), (eval(yStart.get().strip())), (eval(yEnd.get().strip())))
		xpoints = scaleToRange(points['x'],0,1)
		ypoints = scaleToRange(points['y'],1,0)

		combined = []
		for i in range(len(xpoints)):
			combined.append(xpoints[i])
			combined.append(ypoints[i])

		root.clipboard_clear()
		lfo = {"name":name.get().strip(),"num_points":resRead.get(),"points":combined, "powers":[0.0 for i in range(len(xpoints))],"smooth":smooth.get()}
		root.clipboard_append(fh.toJson(lfo))
		return fh.toJson(lfo)

	def onHover(event):
		btn = event.widget
		pressed = btn.cget("image")[0]

		if pressed == 'pyimage1':
			status.config(text = 'Load the selected preset')
		if pressed == 'pyimage2':
			status.config(text = 'Save the current equation as preset')
		if pressed == 'pyimage3':
			status.config(text = 'Delete the selected preset')
		if pressed == 'pyimage4':
			status.config(text = 'Initialize preset')

	def onExit(event):
		status.config(text = '')

	def updateEquation(var, indx, mode):
		prettyEquation.config(text = equation.get().strip().replace('math.','').replace('**','^').replace('sqrt','√').replace('random.',''))
		updatePreview()

	def exportLfo():
		path = filedialog.asksaveasfile(mode = 'w', defaultextension = 'VITALLFO', initialfile = name.get().strip())
		if path is not None:
			path.write(getLfo())
			path.close()
	def indexLeft():
		equation.icursor(equation.index(INSERT)-1)
		setFocus(1)
	def indexRight():
		equation.icursor(equation.index(INSERT)+1)
		setFocus(1)
	def deleteEquation():
		equation.delete(0,END)
		setFocus(1)
	def backspace():
		equation.delete(equation.index(INSERT)-1,equation.index(INSERT))
		setFocus(1)

	reg = root.register(intEntryCallback)

	# Header
	header = ttk.Frame(main)
	header.grid(row = 0, column = 0)

	ttk.Label(header, text = "LFO Name: ") .grid(row = 0, column = 0, sticky = E)
	ttk.Label(header, text = "  Smooth: ") .grid(row = 0, column = 2, sticky = E)
	ttk.Label(header, text = "  Preset: ") .grid(row = 0, column = 4, sticky = E)

	name = ttk.Entry(header, width = 40) # SET THE LFO NAME
	name.grid(row = 0, column = 1, sticky = W)
	name.delete(0,END)
	name.insert(0,"EquaFO LFO")

	smooth = BooleanVar() #ENABLE SMOOTHING
	ttk.Checkbutton(header, var = smooth) .grid(row = 0, column = 3, sticky = W)

	preset = StringVar() # LOAD PRESETS
	presetMenu = ttk.OptionMenu(header, preset, presetOptions[0], *presetOptions, command = loade) 
	presetMenu.grid(row = 0, column = 5, sticky = W)

	loadB = ttk.Button(header, image = loadIcon, command = load) 
	loadB.grid(row = 0, column = 6, sticky = W)
	deleteB = ttk.Button(header, image = trashIcon, command = deletePreset) 
	deleteB.grid(row = 0, column = 8, sticky = W)
	newB = ttk.Button(header, image = newIcon, command = newPreset) 
	newB.grid(row = 0, column = 9, sticky = W)
	saveB = ttk.Button(header, image = saveIcon, command = save) 
	saveB.grid(row = 0, column = 7, sticky = W)

	loadB.bind("<Enter>", onHover)
	loadB.bind("<Leave>", onExit)
	deleteB.bind("<Enter>", onHover)
	deleteB.bind("<Leave>", onExit)
	newB.bind("<Enter>", onHover)
	newB.bind("<Leave>", onExit)
	saveB.bind("<Enter>", onHover)
	saveB.bind("<Leave>", onExit)

	ttk.Separator(main, orient = 'horizontal') .grid(row = 1, column = 0, sticky = NSEW, pady = 10)



	# Adder
	adder = ttk.Frame(main)
	adder.grid(row = 2, column = 0, sticky = NS)

	# TRIG
	ttk.Label(adder, text = "Trig: ") .grid(row = 0, column = 0, sticky = W)
	trigSelected = StringVar()
	ttk.OptionMenu(adder, trigSelected, trigOptions[0], *trigOptions) .grid(row = 1, column = 0, sticky = NSEW)
	ttk.Button(adder, text = "Add", command = addTrig) .grid(row = 1, column = 1, sticky = NSEW, padx = 5)

	# Operators
	ttk.Label(adder, text = "Operators: ") .grid(row = 0, column = 2, sticky = W)
	OperatorSelected = StringVar()
	ttk.OptionMenu(adder, OperatorSelected, operatorOptions[0], *operatorOptions) .grid(row = 1, column = 2, sticky = NSEW)
	ttk.Button(adder, text = "Add", command = addOpe) .grid(row = 1, column = 3, sticky = NSEW, padx = 5)

	# Symbols
	ttk.Label(adder, text = "Symbols: ") .grid(row = 0, column = 4, sticky = W)
	SymbolSelected = StringVar()
	ttk.OptionMenu(adder, SymbolSelected, symbolOptions[0], *symbolOptions) .grid(row = 1, column = 4, sticky = NSEW)
	ttk.Button(adder, text = "Add", command = addSym) .grid(row = 1, column = 5, sticky = NSEW, padx = 5)

	# Variables
	ttk.Label(adder, text = "Variables: ") .grid(row = 2, column = 0, sticky = W)
	VariableSelected = StringVar()
	ttk.OptionMenu(adder, VariableSelected, variableOptions[0], *variableOptions) .grid(row = 3, column = 0, sticky = NSEW)
	ttk.Button(adder, text = "Add", command = addVar) .grid(row = 3, column = 1, sticky = NSEW, padx = 5)

	# Misc
	ttk.Label(adder, text = "Misc: ") .grid(row = 2, column = 2, sticky = W)
	MiscSelected = StringVar()
	ttk.OptionMenu(adder, MiscSelected, miscOptions[0], *miscOptions) .grid(row = 3, column = 2, sticky = NSEW)
	ttk.Button(adder, text = "Add", command = addMis) .grid(row = 3, column = 3, sticky = NSEW, padx = 5)

	# Number
	ttk.Label(adder, text = "Number: ") .grid(row = 2, column = 4, sticky = W)
	NumberSelected = ttk.Entry(adder, width = 16)
	NumberSelected.grid(row = 3, column = 4, sticky = NSEW)
	ttk.Button(adder, text = "Add", command = addNum) .grid(row = 3, column = 5, sticky = NSEW, padx = 5)

	resRead = IntVar()


	ttk.Label(adder, text = "Resolution: ") .grid(row = 4, column = 0, sticky = E)
	resolution = ttk.Scale(adder,from_ = 4, to = 100, orient = 'horizontal', variable = resRead, value = 10, command = roundRes)
	resolution.grid(row = 4, column = 1, columnspan = 4, sticky = NSEW, pady = 5, padx = 5)
	ttk.Label(adder, textvariable = resRead) .grid(row = 4, column = 5, sticky = W)

	phaseRead = DoubleVar()


	ttk.Label(adder, text = "x Phase:" ) .grid(row = 7, column = 0, sticky = E)

	xPhase = ttk.Scale(adder, from_ = -1, to = 1, orient = 'horizontal', variable = phaseRead, value = 0, command = roundPhase)
	xPhase.grid(row = 7, column = 1, columnspan = 4, sticky = NSEW, pady = 5, padx = 5)
	ttk.Label(adder, textvariable = phaseRead) .grid(row = 7, column = 5, sticky = W)

	ttk.Label(adder, text = "x Start: ") .grid(row = 5, column = 0, sticky = E)
	ttk.Label(adder, text = "x End: ") .grid(row = 5, column = 2, sticky = E)
	xStart = ttk.Entry(adder, width = 10)
	xStart.grid(row = 5, column = 1, sticky = W)
	xEnd = ttk.Entry(adder, width = 10)
	xEnd.grid(row = 5, column = 3, sticky = W)

	ttk.Label(adder, text = "y Start: ") .grid(row = 6, column = 0, sticky = E)
	ttk.Label(adder, text = "y End: ") .grid(row = 6, column = 2, sticky = E)
	yStart = ttk.Entry(adder, width = 10)
	yStart.grid(row = 6, column = 1, sticky = W)
	yEnd = ttk.Entry(adder, width = 10)
	yEnd.grid(row = 6, column = 3, sticky = W)

	xStart.insert(0, -3.14)
	xEnd.insert(0, 3.14)
	yStart.insert(0, -1)
	yEnd.insert(0, 1)

	xStart.config(validate="key", validatecommand=(reg, '%P'))
	xEnd.config(validate="key", validatecommand=(reg, '%P'))
	yStart.config(validate="key", validatecommand=(reg, '%P'))
	yEnd.config(validate="key", validatecommand=(reg, '%P'))

	# ttk.Separator(main, orient = 'horizontal') .grid(row = 3, column = 0, sticky = NSEW, pady = 10)


	# Equater
	equater = ttk.Frame(main)
	equater.grid(row = 4, column = 0)

	ttk.Label(equater, text = "Raw Equation: ") .grid(row = 0, column = 0, sticky = NSEW)

	equationHolder = StringVar()
	equation = ttk.Entry(equater, width = 95, textvariable = equationHolder)
	equation.insert(0,"math.sin(x`)")
	equation.grid(row = 1, column = 0, sticky = W, ipady = 5)

	equationHolder.trace_add('write',updateEquation)

	eqButtons = ttk.Frame(equater)
	eqButtons.grid(row = 2, column = 0, sticky = N)

	ttk.Button(eqButtons, image = leftIcon, command = indexLeft) .grid(row = 0, column = 0)
	ttk.Button(eqButtons, image = rightIcon, command = indexRight) .grid(row = 0, column = 1)
	ttk.Button(eqButtons, image = trashIcon, command = deleteEquation) .grid(row = 0, column = 2)
	ttk.Button(eqButtons, image = backspaceIcon, command = backspace) .grid(row = 0, column = 3)

	ttk.Label(eqButtons, text = "Scale Y to fit: ") .grid(row = 0, column = 4, sticky = W)
	scaleY = BooleanVar()
	scaleY.set(0)
	ttk.Checkbutton(eqButtons, variable = scaleY) .grid(row = 0, column = 5, sticky = W)

	ttk.Separator(main, orient = 'horizontal') .grid(row = 5, column = 0, sticky = NSEW, pady = 10)



	# Previewer
	previewer = ttk.Frame(main)
	previewer.grid(row = 6, column = 0, sticky = N)
	previewer.columnconfigure(0, weight = 2)


	prettyEquation = ttk.Label(previewer, text = "To be Filled") 
	prettyEquation.grid(row = 0, column = 0, sticky = W)

	lfoPreview = Canvas(previewer, width = canvasWidth, height = canvasHeight, bg = 'white')
	lfoPreview.grid(row = 1, column = 0, sticky = NSEW, columnspan = 7)

	ttk.Button(previewer, text = "Update", command = updatePreview) .grid(row = 2, column = 0, sticky = NSEW, pady = (0,10))
	ttk.Button(previewer, text = "Copy LFO to clipboard", command = getLfo) .grid(row = 2, column = 1, sticky = NSEW, pady = (0,10))
	ttk.Button(previewer, text = "Export LFO to file", command = exportLfo) .grid(row = 2, column = 2, sticky = NSEW, pady = (0,10))

	ttk.Label(previewer, text = "View Points: ") .grid(row = 2, column = 3, sticky = E)
	viewPoints = BooleanVar()
	ttk.Checkbutton(previewer, var = viewPoints) .grid(row = 2, column = 4, sticky = W)

	ttk.Label(previewer, text = "View Unsmoothed: ") .grid(row = 2, column = 5, sticky = E)
	viewHints = BooleanVar()
	ttk.Checkbutton(previewer, var = viewHints) .grid(row = 2, column = 6, sticky = W)

	# StatusBar
	status = ttk.Label(root2, text = 'Welcome to EquaFO!', borderwidth = 1, relief = "sunken")
	status.grid(row = 1, column = 0, sticky = NSEW, ipady = 2)

	def setFocus(event):
		equation.focus_set()
	def endFocus(event):
		root.focus_set()
	# KEYBONDINGS
	# root.bind("<Return>", updateEvent)
	root.bind("<ButtonRelease-1>", updateEvent)
	adder.bind("<Enter>", setFocus)
	equation.bind("<Enter>",setFocus)
	eqButtons.bind("<Enter>",setFocus)
	adder.bind("<Leave>", endFocus)

	newPreset()
	updatePreview()
	root.mainloop()

main()