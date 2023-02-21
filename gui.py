import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import fileHandler as fh
import math
import numpy as np
import random
import entries

class DEFAULTS:
	NAME = "New LFO"
	EQUATION = "math.sin(x)"
	SMOOTH = False
	X_START = -math.pi
	X_END = math.pi
	Y_START = -1
	Y_END = 1
	RESOLUTION = 17
	PHASE = 0

# https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
class Tooltip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget: ttk.Widget, text: str):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget: ttk.Widget = widget
        self.text: str = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id_copy = self.id
        self.id = None
        if id_copy:
            self.widget.after_cancel(id_copy)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + self.widget.winfo_width() - 25
        y += self.widget.winfo_rooty() - 6
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = ttk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()


def main():
	root = tk.Tk()
	root.title("EquaFO")
	root.resizable(width=False, height=False)
	root.geometry("+10+10")

	style = ttk.Style()
	style.theme_use('clam')

	root2 = ttk.Frame(root)
	root2.grid(row = 0, column = 0, sticky = tk.NSEW)

	main = ttk.Frame(root2)
	main.grid(row = 0, column = 0, padx = 10, pady = (10,0))

	# Vars
	trigOptions = ['sin(𝑥)','cos(𝑥)','tan(𝑥)','asin(𝑥)','acos(𝑥)','atan(𝑥)','sinh(𝑥)','cosh(𝑥)','tanh(𝑥)','degrees(𝑥)','radians(𝑥)']
	operatorOptions = ['+','-','×','÷','%','√','^','//']
	symbolOptions = ['(',')']
	variableOptions = ['𝑥','π','𝑒','τ (tau)']
	miscOptions = ['ceil(𝑥)','floor(𝑥)','abs(𝑥)','loge(𝑥)', 'log2(𝑥)', 'log10(𝑥)','random(start, stop)', 'uniform(start, stop)', 'round(𝑥,n)']
	presetsDB = fh.readJson("presets.json")
	presetOptions = list(presetsDB.keys())
	canvasWidth = 650
	canvasHeight = 300

	#Images
	loadIcon = tk.PhotoImage(file="icons/loadIcon.png")
	saveIcon = tk.PhotoImage(file="icons/saveIcon.png")
	trashIcon = tk.PhotoImage(file="icons/trashIcon.png")
	newIcon = tk.PhotoImage(file="icons/newIcon.png")
	leftIcon = tk.PhotoImage(file="icons/leftIcon.png")
	rightIcon = tk.PhotoImage(file="icons/rightIcon.png")
	backspaceIcon = tk.PhotoImage(file="icons/backspaceIcon.png")

	#Functions
	def fixEquation():
		toIndex = equation.get().find('`')
		eqHold = equation.get()
		equation.delete(0,tk.END)
		equation.insert(0,eqHold.replace('`',''))
		equation.icursor(toIndex)
		setFocus(1)

	def addTrigToEquation():
		equation.insert(equation.index(tk.INSERT), entries.getEntry(trigSelected.get()))
		fixEquation()

	def addOperatorToEquation():
		equation.insert(equation.index(tk.INSERT), entries.getEntry(OperatorSelected.get()))
		fixEquation()

	def addSymbolToEquation():
		equation.insert(equation.index(tk.INSERT), entries.getEntry(SymbolSelected.get()))
		fixEquation()

	def addVariableToEquation():
		equation.insert(equation.index(tk.INSERT), entries.getEntry(VariableSelected.get()))
		fixEquation()

	def addMiscToEquation():
		equation.insert(equation.index(tk.INSERT), entries.getEntry(MiscSelected.get()))
		fixEquation()

	def addNumberToEquation():
		equation.insert(equation.index(tk.INSERT), NumberSelected.get().strip() + '`')
		fixEquation()

	def savePresetToDB():
		values = {"smooth":smooth.get(),"equation":equation.get().strip(), "range":[(eval(xStartTextField.get().strip())), (eval(xEndTextField.get().strip())), (eval(yStartTextField.get().strip())), (eval(yEndTextField.get().strip()))], 'resolution':resolutionValue.get(),'xPhase':xPhase.get()}
		presetsDB[name.get().strip()] = values
		fh.writeJson('presets.json', presetsDB)
		presetName.set(name.get().strip())
		updatePresets()

	def loadSelectedPreset():
		name.delete(0,tk.END)
		name.insert(0, presetName.get())

		preset = presetsDB[presetName.get()]
		smooth.set(preset['smooth'])
		equation.delete(0,tk.END)
		equation.insert(0,preset['equation'])
		xStartTextField.delete(0,tk.END)
		xStartTextField.insert(0,preset['range'][0])
		xEndTextField.delete(0,tk.END)
		xEndTextField.insert(0,preset['range'][1])
		yStartTextField.delete(0,tk.END)
		yStartTextField.insert(0,preset['range'][2])
		yEndTextField.delete(0,tk.END)
		yEndTextField.insert(0,preset['range'][3])
		resolutionValue.set(preset['resolution'])
		xPhase.set(presetsDB[presetName.get()]['xPhase'])
		updateXYPlot()

	def deletePresetFromDB():
		if len(presetsDB) > 1:
			presetsDB.pop(presetName.get())
			fh.writeJson('presets.json',presetsDB)
			updatePresets()

	def updatePresets():
		presetsDB = fh.readJson("presets.json")
		presetOptions = list(presetsDB.keys())
		presetMenu = ttk.OptionMenu(header, presetName, presetOptions[0], *presetOptions)
		presetMenu.grid(row = 0, column = 5, sticky = tk.W)

	def initPreset():
		name.delete(0,tk.END)
		name.insert(0, DEFAULTS.NAME)
		smooth.set(DEFAULTS.SMOOTH)
		equation.delete(0,tk.END)
		equation.insert(0,DEFAULTS.EQUATION)
		xStartTextField.delete(0,tk.END)
		xStartTextField.insert(0,DEFAULTS.X_START)
		xEndTextField.delete(0,tk.END)
		xEndTextField.insert(0,DEFAULTS.X_END)
		yStartTextField.delete(0,tk.END)
		yStartTextField.insert(0,DEFAULTS.Y_START)
		yEndTextField.delete(0,tk.END)
		yEndTextField.insert(0,DEFAULTS.Y_END)
		resolutionValue.set(DEFAULTS.RESOLUTION)
		phaseOffsetValue.set(DEFAULTS.PHASE)
		updateXYPlot()

	def getPoints(xStart, xEnd, yStart, yEnd):
		numPoints = resolutionValue.get()
		xRange = abs(xEnd-xStart)
		xpoints = np.arange(xStart, xEnd, (xEnd - xStart) / (numPoints - 1))
		xpoints = np.append(xpoints, xEnd)

		ypoints = []
		try:
			x = xpoints
			ypoints = eval(equation.get().replace('math.', 'np.'))

			if scaleY.get() == False:
				ypoints = np.clip(ypoints, min(yStart, yEnd), max(yStart, yEnd))

		except Exception:
			ypoints = [0 for i in range(len(xpoints))]
			xyPlot.create_text(20,10, text = "Error", fill = 'red')

		points = {'x':xpoints,'y':ypoints}
		return points

	def scaleToRange(arr, start, end):
		scaled = np.ndarray.tolist(np.interp(arr, (min(arr), max(arr)), (start, end)))
		# scaled = [round(i, 3) for i in scaled]
		return scaled

	def updateXYPlot():
		try:
			xStart = eval(xStartTextField.get().strip())
			xEnd = eval(xEndTextField.get().strip())
			yStart = eval(yStartTextField.get().strip())
			yEnd = eval(yEndTextField.get().strip())

			points = getPoints(xStart, xEnd, yStart, yEnd)

			xpoints = scaleToRange(points['x'],0,canvasWidth)

			yMin = min(points['y'])
			yMax = max(points['y'])

			if scaleY.get():
				ypoints = scaleToRange(points['y'],canvasHeight,0)
			else:
				ypoints = canvasHeight - (canvasHeight * (points['y'] - yStart)) / (yEnd - yStart)

			canvasXAxis = scaleToRange([yStart, 0, yEnd], canvasHeight, 0)
			canvasYAxis = scaleToRange([xStart, 0, xEnd], 0, canvasWidth)

			combined = np.array([xpoints, ypoints]).T.tolist()

			xyPlot.delete("all")

			xyPlot.create_text(canvasYAxis[1]+10, canvasHeight-10, text = yMin if scaleY.get() else eval(yStartTextField.get().strip()))
			xyPlot.create_text(canvasYAxis[1]+10, 10, text = yMax if scaleY.get() else eval(yEndTextField.get().strip()))
			xyPlot.create_text(10, canvasXAxis[1]+10, text = min(points['x']))
			xyPlot.create_text(canvasWidth-10, canvasXAxis[1]+10, text = max(points['x']))
			xyPlot.create_line(canvasYAxis[1], canvasXAxis[0], canvasYAxis[1], canvasXAxis[2], canvasYAxis[1], canvasXAxis[1], canvasWidth, canvasXAxis[1], 0, canvasXAxis[1], fill = 'red', width = 2, smooth = False)

			radius = 2
			diameter = 2 * radius
			if viewPoints.get() == True:
				for px, py in combined:
					x1 = round(px-radius)
					y1 = round(py-radius)
					x1 = min(max(x1, 0), canvasWidth - diameter)
					y1 = min(max(y1, 0), canvasHeight - diameter)

					x2 = x1 + diameter
					y2 = y1 + diameter

					xyPlot.create_oval(x1, y1, x2, y2, fill = 'black', outline = 'black')
			else:
				pass

			if viewUnsmoothedVal.get() == True:
				xyPlot.create_line(combined, fill = 'darkGrey', width = 1, smooth = False)

			xyPlot.create_line(combined, fill = 'Black', width = 1, smooth = smooth.get())

		except Exception as e:
			print(e)
			xyPlot.create_text(20,10, text = "Error")

	def	updateEvent(event):
		updateXYPlot()
		createLFOPresetJSON()

	def handleResolutionChanged(event):
		resolutionValue.set(round(float(resolutionValue.get())))
		updateXYPlot()

	def handlePhaseChanged(event):
		phaseOffsetValue.set(round(float(phaseOffsetValue.get()), 5))
		updateXYPlot()

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

	def createLFOPresetJSON():
		points = getPoints(eval(xStartTextField.get().strip()), (eval(xEndTextField.get().strip())), (eval(yStartTextField.get().strip())), (eval(yEndTextField.get().strip())))
		xpoints = scaleToRange(points['x'],0,1)
		ypoints = scaleToRange(points['y'],1,0)
		assert len(xpoints) == len(ypoints)

		combined = np.array([xpoints, ypoints]).T.tolist()

		root.clipboard_clear()
		lfo = {"name":name.get().strip(),"num_points":resolutionValue.get(),"points":combined, "powers":[0.0 for i in range(len(xpoints))],"smooth":smooth.get()}
		root.clipboard_append(fh.toJson(lfo))
		return fh.toJson(lfo)

	def handleEquationUpdated(var, indx, mode):
		prettyEquationString.set(equation.get().strip().replace('math.','').replace('**','^').replace('sqrt','√').replace('random.',''))
		updateXYPlot()

	def exportAsLFOPreset():
		path = filedialog.asksaveasfile(mode = 'w', defaultextension = 'VITALLFO', initialfile = name.get().strip())
		if path is not None:
			path.write(createLFOPresetJSON())
			path.close()

	def handleShiftLeftButtonClick():
		equation.icursor(equation.index(tk.INSERT)-1)
		setFocus(1)

	def handleShiftRightButtonClick():
		equation.icursor(equation.index(tk.INSERT)+1)
		setFocus(1)

	def handleClearButtonClick():
		equation.delete(0,tk.END)
		setFocus(1)

	def handleBackspaceButtonClick():
		equation.delete(equation.index(tk.INSERT)-1,equation.index(tk.INSERT))
		setFocus(1)

	reg = root.register(intEntryCallback)

	# Header
	header = ttk.Frame(main)
	header.grid(row = 0, column = 0)

	ttk.Label(header, text = "LFO Name: ") .grid(row = 0, column = 0, sticky = tk.E)
	ttk.Label(header, text = "  Smooth: ") .grid(row = 0, column = 2, sticky = tk.E)
	ttk.Label(header, text = "  Preset: ") .grid(row = 0, column = 4, sticky = tk.E)

	name = ttk.Entry(header, width = 40) # SET THE LFO NAME
	name.grid(row = 0, column = 1, sticky = tk.W)

	smooth = tk.BooleanVar() #ENABLE SMOOTHING
	ttk.Checkbutton(header, var = smooth) .grid(row = 0, column = 3, sticky = tk.W)

	presetName = tk.StringVar() # LOAD PRESETS
	presetMenu = ttk.OptionMenu(header, presetName, presetOptions[0], *presetOptions, command = lambda e: loadSelectedPreset())
	presetMenu.grid(row = 0, column = 5, sticky = tk.W)

	loadPresetButton = ttk.Button(header, image = loadIcon, command = loadSelectedPreset)
	loadPresetButton.grid(row = 0, column = 6, sticky = tk.W)
	loadPresetButtonTT = Tooltip(loadPresetButton, 'Load the selected preset from presets file')
	savePresetButton = ttk.Button(header, image = saveIcon, command = savePresetToDB)
	savePresetButton.grid(row = 0, column = 7, sticky = tk.W)
	savePresetButtonTT = Tooltip(savePresetButton, 'Save the current equation as preset in presets file')
	deletePresetButton = ttk.Button(header, image = trashIcon, command = deletePresetFromDB)
	deletePresetButton.grid(row = 0, column = 8, sticky = tk.W)
	deletePresetButtonTT = Tooltip(deletePresetButton, 'Delete the selected preset from presets file')
	initPresetButton = ttk.Button(header, image = newIcon, command = initPreset)
	initPresetButton.grid(row = 0, column = 9, sticky = tk.W)
	initPresetButtonTT = Tooltip(initPresetButton, 'Initialize a new preset')

	ttk.Separator(main, orient = 'horizontal') .grid(row = 1, column = 0, sticky = tk.NSEW, pady = 10)

	# Adder
	adder = ttk.Frame(main)
	adder.grid(row = 2, column = 0, sticky = tk.NS)

	# TRIG
	ttk.Label(adder, text = "Trig: ") .grid(row = 0, column = 0, sticky = tk.W)
	trigSelected = tk.StringVar()
	ttk.OptionMenu(adder, trigSelected, trigOptions[0], *trigOptions) .grid(row = 1, column = 0, sticky = tk.NSEW)
	trigAddButton = ttk.Button(adder, text = "Add", command = addTrigToEquation)
	trigAddButton.grid(row = 1, column = 1, sticky = tk.NSEW, padx = 5)
	trigAddButtonTT = Tooltip(trigAddButton, "Add to raw equation at index")

	# Operators
	ttk.Label(adder, text = "Operators: ") .grid(row = 0, column = 2, sticky = tk.W)
	OperatorSelected = tk.StringVar()
	ttk.OptionMenu(adder, OperatorSelected, operatorOptions[0], *operatorOptions) .grid(row = 1, column = 2, sticky = tk.NSEW)
	operatorsAddButton = ttk.Button(adder, text = "Add", command = addOperatorToEquation)
	operatorsAddButton.grid(row = 1, column = 3, sticky = tk.NSEW, padx = 5)
	operatorsAddButtonTT = Tooltip(operatorsAddButton, "Add to raw equation at index")

	# Symbols
	ttk.Label(adder, text = "Symbols: ") .grid(row = 0, column = 4, sticky = tk.W)
	SymbolSelected = tk.StringVar()
	ttk.OptionMenu(adder, SymbolSelected, symbolOptions[0], *symbolOptions) .grid(row = 1, column = 4, sticky = tk.NSEW)
	symbolsAddButton = ttk.Button(adder, text = "Add", command = addSymbolToEquation)
	symbolsAddButton.grid(row = 1, column = 5, sticky = tk.NSEW, padx = 5)
	symbolsAddButtonTT = Tooltip(symbolsAddButton, "Add to raw equation at index")

	# Variables
	ttk.Label(adder, text = "Variables: ") .grid(row = 2, column = 0, sticky = tk.W)
	VariableSelected = tk.StringVar()
	ttk.OptionMenu(adder, VariableSelected, variableOptions[0], *variableOptions) .grid(row = 3, column = 0, sticky = tk.NSEW)
	varAddButton = ttk.Button(adder, text = "Add", command = addVariableToEquation)
	varAddButton.grid(row = 3, column = 1, sticky = tk.NSEW, padx = 5)
	varAddButtonTT = Tooltip(varAddButton, "Add to raw equation at index")

	# Misc
	ttk.Label(adder, text = "Misc: ") .grid(row = 2, column = 2, sticky = tk.W)
	MiscSelected = tk.StringVar()
	ttk.OptionMenu(adder, MiscSelected, miscOptions[0], *miscOptions) .grid(row = 3, column = 2, sticky = tk.NSEW)
	miscAddButton = ttk.Button(adder, text = "Add", command = addMiscToEquation)
	miscAddButton.grid(row = 3, column = 3, sticky = tk.NSEW, padx = 5)
	miscAddButtonTT = Tooltip(miscAddButton, "Add to raw equation at index")

	# Number
	ttk.Label(adder, text = "Number: ") .grid(row = 2, column = 4, sticky = tk.W)
	NumberSelected = ttk.Entry(adder, width = 16)
	NumberSelected.grid(row = 3, column = 4, sticky = tk.NSEW)
	numAddButton = ttk.Button(adder, text = "Add", command = addNumberToEquation)
	numAddButton.grid(row = 3, column = 5, sticky = tk.NSEW, padx = 5)
	numAddButtonTT = Tooltip(numAddButton, "Add to raw equation at index")

	resolutionValue = tk.IntVar()
	"""Number of discrete points in wave"""

	ttk.Label(adder, text = "Resolution: ") .grid(row = 4, column = 0, sticky = tk.E)
	resolution = ttk.Scale(adder,from_ = 4, to = 100, orient = 'horizontal', variable = resolutionValue, value = 10, command = handleResolutionChanged)
	resolution.grid(row = 4, column = 1, columnspan = 4, sticky = tk.NSEW, pady = 5, padx = 5)
	ttk.Label(adder, textvariable = resolutionValue) .grid(row = 4, column = 5, sticky = tk.W)

	phaseOffsetValue = tk.DoubleVar()

	ttk.Label(adder, text = "x Phase:" ) .grid(row = 7, column = 0, sticky = tk.E)

	xPhase = ttk.Scale(adder, from_ = -1, to = 1, orient = 'horizontal', variable = phaseOffsetValue, value = 0, command = handlePhaseChanged)
	xPhase.grid(row = 7, column = 1, columnspan = 4, sticky = tk.NSEW, pady = 5, padx = 5)
	xPhase.bind('<Double-1>', lambda event: xPhase.set(0))
	ttk.Label(adder, textvariable = phaseOffsetValue) .grid(row = 7, column = 5, sticky = tk.W)

	ttk.Label(adder, text = "x Start: ") .grid(row = 5, column = 0, sticky = tk.E)
	ttk.Label(adder, text = "x End: ") .grid(row = 5, column = 2, sticky = tk.E)
	xStartTextField = ttk.Entry(adder, width = 10)
	xStartTextField.grid(row = 5, column = 1, sticky = tk.W)

	xEndTextField = ttk.Entry(adder, width = 10)
	xEndTextField.grid(row = 5, column = 3, sticky = tk.W)

	ttk.Label(adder, text = "y Start: ") .grid(row = 6, column = 0, sticky = tk.E)
	ttk.Label(adder, text = "y End: ") .grid(row = 6, column = 2, sticky = tk.E)
	yStartTextField = ttk.Entry(adder, width = 10)
	yStartTextField.grid(row = 6, column = 1, sticky = tk.W)
	yEndTextField = ttk.Entry(adder, width = 10)
	yEndTextField.grid(row = 6, column = 3, sticky = tk.W)

	xStartTextField.config(validate="key", validatecommand=(reg, '%P'))
	xEndTextField.config(validate="key", validatecommand=(reg, '%P'))
	yStartTextField.config(validate="key", validatecommand=(reg, '%P'))
	yEndTextField.config(validate="key", validatecommand=(reg, '%P'))

	# ttk.Separator(main, orient = 'horizontal') .grid(row = 3, column = 0, sticky = tk.NSEW, pady = 10)

	# Equater
	equater = ttk.Frame(main)
	equater.grid(row = 4, column = 0)

	ttk.Label(equater, text = "Raw Equation: ") .grid(row = 0, column = 0, sticky = tk.NSEW)

	equationString = tk.StringVar()
	equation = ttk.Entry(equater, width = 95, textvariable = equationString)
	equation.grid(row = 1, column = 0, sticky = tk.W, ipady = 5)

	equationString.trace_add('write',handleEquationUpdated)

	eqButtons = ttk.Frame(equater)
	eqButtons.grid(row = 2, column = 0, sticky = tk.N)

	ttk.Button(eqButtons, image = leftIcon, command = handleShiftLeftButtonClick) .grid(row = 0, column = 0)
	ttk.Button(eqButtons, image = rightIcon, command = handleShiftRightButtonClick) .grid(row = 0, column = 1)
	ttk.Button(eqButtons, image = trashIcon, command = handleClearButtonClick) .grid(row = 0, column = 2)
	ttk.Button(eqButtons, image = backspaceIcon, command = handleBackspaceButtonClick) .grid(row = 0, column = 3)

	ttk.Label(eqButtons, text = "Scale Y to fit: ") .grid(row = 0, column = 4, sticky = tk.W)
	scaleY = tk.BooleanVar()
	scaleY.set(0)
	ttk.Checkbutton(eqButtons, variable = scaleY) .grid(row = 0, column = 5, sticky = tk.W)

	ttk.Separator(main, orient = 'horizontal') .grid(row = 5, column = 0, sticky = tk.NSEW, pady = 10)

	# Previewer
	previewer = ttk.Frame(main)
	previewer.grid(row = 6, column = 0, sticky = tk.N)
	previewer.columnconfigure(0, weight = 2)

	prettyEquationString = tk.StringVar()


	prettyEquation = ttk.Entry(previewer, textvariable=prettyEquationString, state='readonly', width=108)
	prettyEquation.grid(row = 0, column = 0, sticky = tk.N, columnspan=8)

	prettyEqScroll = ttk.Scrollbar(previewer, orient='horizontal', command=prettyEquation.xview, )
	prettyEquation.config(xscrollcommand=prettyEqScroll.set)
	prettyEqScroll.grid(row=1,column=0,sticky=tk.NSEW,columnspan=8)

	xyPlot = tk.Canvas(previewer, width = canvasWidth, height = canvasHeight, bg = 'white')
	xyPlot.grid(row = 2, column = 0, sticky = tk.NSEW, columnspan = 7)

	updatePlotButton = ttk.Button(previewer, text = "Update", command = updateXYPlot)
	updatePlotButton.grid(row = 3, column = 0, sticky = tk.NSEW, pady = (0,10))
	updatePlotButtonTT = Tooltip(updatePlotButton, "Force updates the x/y plot")

	ttk.Button(previewer, text = "Copy LFO to clipboard", command = createLFOPresetJSON) .grid(row = 3, column = 1, sticky = tk.NSEW, pady = (0,10))
	ttk.Button(previewer, text = "Export LFO to file", command = exportAsLFOPreset) .grid(row = 3, column = 2, sticky = tk.NSEW, pady = (0,10))

	ttk.Label(previewer, text = "View Points: ") .grid(row = 3, column = 3, sticky = tk.E)
	viewPoints = tk.BooleanVar()
	viewPoints.set(True)
	ttk.Checkbutton(previewer, var = viewPoints) .grid(row = 3, column = 4, sticky = tk.W)

	ttk.Label(previewer, text = "View Unsmoothed: ") .grid(row = 3, column = 5, sticky = tk.E)
	viewUnsmoothedVal = tk.BooleanVar()
	viewUnsmoothedVal.set(True)
	ttk.Checkbutton(previewer, var = viewUnsmoothedVal) .grid(row = 3, column = 6, sticky = tk.W)

	# StatusBar
	# status = ttk.Label(root2, text = 'Welcome to EquaFO!', borderwidth = 1, relief = "sunken")
	# status.grid(row = 1, column = 0, sticky = tk.NSEW, ipady = 3)

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

	initPreset()
	root.mainloop()

if __name__ == '__main__':
	main()
