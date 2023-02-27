import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import fileHandler as fh
import math
import numpy as np
from scipy import special
import random
import entries
import soundfile as sf
import traceback
import re

PADDING = 2

# support for all math.{name} functions
np.tau = math.tau
np.fsum = np.sum
np.acos = np.arccos
np.acosh = np.arccosh
np.asin = np.arcsin
np.asinh = np.arcsinh
np.atan = np.arctan
np.atanh = np.arctanh
np.atan2 = np.arctan2
np.pow = np.power
np.factorial = special.factorial
np.gamma = special.gamma
np.lgamma = special.gammaln
np.erf = special.erf
np.erfc = special.erfc
np.perm = special.perm
np.comb = special.comb

class AppState:
	def __init__(self):
		self.name = tk.StringVar()
		self.equation = tk.StringVar()
		self.smooth = tk.BooleanVar() # enables smoothing on x/y plot
		self.xStart = tk.StringVar()
		self.xEnd = tk.StringVar()
		self.yStart = tk.StringVar()
		self.yEnd = tk.StringVar()
		self.resolution = tk.IntVar()
		self.phase = tk.DoubleVar()
		self.z = tk.DoubleVar() # z position (x/y/z axis)
		self.numFrames = tk.IntVar() # num wavetable frames (1-256)
		self.reset()
	def reset(self):
		self.name.set("New LFO")
		self.equation.set("math.sin(x)")
		self.smooth.set(False)
		self.xStart.set(-math.pi)
		self.xEnd.set(math.pi)
		self.yStart.set(-1)
		self.yEnd.set(1)
		self.resolution.set(17)
		self.phase.set(0)
		self.z.set(0)
		self.numFrames.set(256)
	def getXStart(self):
		return float(self.xStart.get())
	def getXEnd(self):
		return float(self.xEnd.get())
	def getYStart(self):
		return float(self.yStart.get())
	def getYEnd(self):
		return float(self.yEnd.get())


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
        x += self.widget.winfo_rootx() + self.widget.winfo_width() - 5
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
	def rescale(sourceValue, sourceRangeMin, sourceRangeMax, targetRangeMin, targetRangeMax):
		# protecc from ZeroDivisionError
		assert (sourceRangeMax != sourceRangeMin)
		return targetRangeMin + ((targetRangeMax - targetRangeMin) * (sourceValue - sourceRangeMin)) / (sourceRangeMax - sourceRangeMin)

	def limit(v, low, high):
		return min(max(v, low), high)

	def fixEquation():
		toIndex = equationTextInput.get().find('`')
		eqHold = equationTextInput.get()
		equationTextInput.delete(0,tk.END)
		equationTextInput.insert(0,eqHold.replace('`',''))
		equationTextInput.icursor(toIndex)
		setFocus(1)

	def addTrigToEquation():
		equationTextInput.insert(equationTextInput.index(tk.INSERT), entries.getEntry(trigSelected.get()))
		fixEquation()

	def addOperatorToEquation():
		equationTextInput.insert(equationTextInput.index(tk.INSERT), entries.getEntry(OperatorSelected.get()))
		fixEquation()

	def addSymbolToEquation():
		equationTextInput.insert(equationTextInput.index(tk.INSERT), entries.getEntry(SymbolSelected.get()))
		fixEquation()

	def addVariableToEquation():
		equationTextInput.insert(equationTextInput.index(tk.INSERT), entries.getEntry(VariableSelected.get()))
		fixEquation()

	def addMiscToEquation():
		equationTextInput.insert(equationTextInput.index(tk.INSERT), entries.getEntry(MiscSelected.get()))
		fixEquation()

	def addNumberToEquation():
		equationTextInput.insert(equationTextInput.index(tk.INSERT), NumberSelected.get().strip() + '`')
		fixEquation()

	def savePresetToDB():
		values = {
			"smooth": state.smooth.get(),
			"equation": state.equation.get().strip(),
			"range":[
				state.getXStart(),
				state.getXEnd(),
				state.getYStart(),
				state.getYEnd(),
			],
			'resolution': state.resolution.get(),
			'xPhase':state.phase.get(),
			'zPosition': state.z.get(),
			'numFrames': state.numFrames.get(),
		}
		presetsDB[state.name.get().strip()] = values
		fh.writeJson('presets.json', presetsDB)
		presetName.set(state.name.get().strip())
		updatePresets()

	def loadSelectedPreset():
		key = presetName.get()
		preset = presetsDB[key]

		state.name.set(key)
		state.smooth.set(preset['smooth'])
		state.equation.set(preset['equation'])
		state.xStart.set(preset['range'][0])
		state.xEnd.set(preset['range'][1])
		state.yStart.set(preset['range'][2])
		state.yEnd.set(preset['range'][3])
		state.resolution.set(preset['resolution'])

		xPhase.set(preset['xPhase'])
		zScale.set(preset.get('zPosition', 0))
		numFramesScale.set(preset.get('numFrames', 256))

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
		state.reset()
		updateXYPlot()

	def clampZToNumFrames(z):
		numFrames = state.numFrames.get()
		if numFrames > 1:
			fraction = 1 / (numFrames - 1)
			# round to nearest multiple of fraction
			return round(z / fraction) * fraction
		return 0

	def executeEquationForList(x, z):
		def np_uniform(low, high):
			return np.random.uniform(low, high, state.resolution.get())
		def np_randint(low, high):
			return np.random.randint(low, high, state.resolution.get())
		equationString = state.equation.get()
		equationString = equationString.replace('math.', 'np.')
		equationString = equationString.replace('numpy.', 'np.')
		equationString = equationString.replace('round', 'np.around')
		equationString = equationString.replace('random.uniform', 'np_uniform')
		equationString = equationString.replace('random.randrange', 'np_randint')

		y = eval(equationString)
		return y

	# def execute_equation_for_val(x):
	# 	y = eval(equationString)
	# 	return y

	def getPoints(numPoints, z):
		xStart = state.getXStart()
		xEnd = state.getXEnd()
		yStart = state.getYStart()
		yEnd = state.getYEnd()

		xpoints = np.arange(xStart, xEnd, (xEnd - xStart) / (numPoints - 1))
		xpoints = np.append(xpoints, xEnd)

		ypoints = []
		err = None
		try:
			x = xpoints + state.phase.get() * (xEnd - xStart)

			ypoints = executeEquationForList(x, z)

			# raising a negative number to the power of a negative number can produce complex numbers
			if np.any(np.iscomplex(ypoints)):
				# cannot plot complex numbers for Y axis on our graph
				raise ValueError("Calculated value is a complex number.")

			# functions like log, acos etc will often produce NaN for values like -2
			# this will set them to 0
			ypoints = np.nan_to_num(ypoints)

			if scaleY.get() == False:
				ypoints = np.clip(ypoints, min(yStart, yEnd), max(yStart, yEnd))

		except Exception:
			err = traceback.format_exc()
			ypoints = np.empty(numPoints)
			ypoints.fill((yEnd - yStart) * 0.5)

		points = {'x': xpoints,'y': ypoints, 'error': err}
		return points

	def scaleToRange(arr, start, end):
		scaled = np.interp(arr, (min(arr), max(arr)), (start, end))
		# scaled = [round(i, 3) for i in scaled]
		return scaled

	def updateXYPlot():
		try:
			# clear canvas
			xyPlot.delete("all")

			z = clampZToNumFrames(state.z.get())
			points = getPoints(state.resolution.get(),  z)
			if points['error'] is not None:
				lines = points['error'].split('\n')
				lines.insert(0, "Found error in equation \"%s\"" % state.equation.get())
				lines.insert(1, "")
				y = 10
				for line in lines:
					xyPlot.create_text(20,y, text=line, fill="red", anchor=tk.NW)
					y += 12
				return

			xStart = state.getXStart()
			xEnd = state.getXEnd()
			yStart = state.getYStart()
			yEnd = state.getYEnd()

			xpoints = scaleToRange(points['x'],0,canvasWidth)

			xMin = min(points['x'])
			xMax = max(points['x'])
			yMin = min(points['y'])
			yMax = max(points['y'])

			if scaleY.get():
				ypoints = scaleToRange(points['y'],canvasHeight, 0)
				plane0Y = rescale(0, yMin, yMax, 0, canvasHeight)
				yLimTop = yMax
				yLimBottom = yMin
			else:
				ypoints = np.interp(points['y'], (yStart,yEnd), (canvasHeight, 0))
				plane0Y = rescale(0, yStart, yEnd, canvasHeight, 0)
				yLimTop = yEnd
				yLimBottom = yStart

			plane0X = rescale(0, xMin, xMax, 0, canvasWidth)

			combined = np.array([xpoints, ypoints]).T.tolist()

			# draw axis
			xyPlot.create_line(0, plane0Y, canvasWidth, plane0Y, fill = 'red', width = 2, smooth = False)
			xyPlot.create_line(plane0X, 0, plane0X, canvasHeight, fill = 'red', width = 2, smooth = False)
			# draw axis labels
			xyPlot.create_text(0, limit(plane0Y + 8, 0, canvasHeight), text=str(round(xStart, 3)), fill='black', anchor=tk.W)
			xyPlot.create_text(canvasWidth, limit(plane0Y + 8, 0, canvasHeight), text=str(round(xEnd,3)), fill='black', anchor=tk.E)
			xyPlot.create_text(plane0X+2, 0, text=str(round(yLimTop,3)), fill='black', anchor=tk.NW)
			xyPlot.create_text(plane0X+2, canvasHeight, text=str(round(yLimBottom,3)), fill='black', anchor=tk.SW)

			if viewPoints.get() == True:
				radius = 2
				diameter = 2 * radius

				for px, py in combined:
					x1 = round(px-radius)
					y1 = round(py-radius)
					x1 = min(max(x1, 0), canvasWidth - diameter)
					y1 = min(max(y1, 0), canvasHeight - diameter)

					x2 = x1 + diameter
					y2 = y1 + diameter

					xyPlot.create_oval(x1, y1, x2, y2, fill = 'black', outline = 'black')

			if viewUnsmoothedVal.get() == True:
				xyPlot.create_line(combined, fill = 'darkGrey', width = 1, smooth = False)

			xyPlot.create_line(combined, fill = 'Black', width = 1, smooth = state.smooth.get())

		except Exception as e:
			# print(traceback.format_exc())
			xyPlot.create_text(20,10, text = "Error")

	def handleResolutionChanged(event):
		state.resolution.set(round(float(state.resolution.get())))
		updateXYPlot()

	def handleNumFramesChanged(event):
		state.numFrames.set(round(float(state.numFrames.get())))
		updateXYPlot()

	def handlePhaseChanged(event):
		state.phase.set(round(float(state.phase.get()), 5))
		updateXYPlot()

	def handleZPositionChanged(event):
		state.z.set(round(float(state.z.get()), 5))
		updateXYPlot()

	def intEntryCallback(text):
		allowedChars = "1234567890-+/*."
		for i in text:
			if i not in allowedChars:
				return False
		return True

	def normalizeXYPlotToLFOPreset():
		z = clampZToNumFrames(state.z.get())
		points = getPoints(state.resolution.get(), z)
		if 'error' in points:
			return ([0,0], [0,0])
		xpoints = scaleToRange(points['x'],0,1)
		ypoints = scaleToRange(points['y'],0,1)
		assert len(xpoints) == len(ypoints)

		return xpoints, ypoints

	def serializeIntoGHOSTLFOPreset():

		xpoints, ypoints = normalizeXYPlotToLFOPreset()
		combined = np.array([xpoints, ypoints]).T

		pointObjects = [{'x': x, 'y': y, 'skew': 0.5} for x, y in combined]

		data = {
			"version": "0.3.9",
			"lfo": {
				"name": state.name.get(),
				"points": pointObjects,
			}
		}
		return fh.toJson(data)

	def serializeIntoVitalLFOPreset():
		xpoints, ypoints = normalizeXYPlotToLFOPreset()
		combined = np.concatenate(np.array([xpoints, ypoints]).T).tolist()

		root.clipboard_clear()
		data = {
			"name":state.name.get().strip(),
			"num_points":state.resolution.get(),
			"points":combined,
			"powers":[0.0 for i in range(len(xpoints))],
			"smooth":state.smooth.get(),
		}
		return fh.toJson(data)

	def copyLFOPresetToClipboard():
		data = serializeIntoVitalLFOPreset()
		root.clipboard_append(data)

	def handleEquationUpdated(var, indx, mode):
		prettyEquationString.set(state.equation.get().strip().replace('math.','').replace('**','^').replace('sqrt','√').replace('random.',''))
		updateXYPlot()

	def exportAsLFOPreset():
		file = filedialog.asksaveasfile(
			mode = 'w',
			filetypes=(
				("GHOST", "*.json"),
				("Vital", "*.vitallfo")),
			#defaultextension = 'JSON', # GHOST FTW!
			initialfile = state.name.get().strip())
		if file is not None:
			filename = file.name.lower()
			if filename.endswith('.json'):
				file.write(serializeIntoGHOSTLFOPreset())
			elif filename.endswith('.vitallfo'):
				file.write(serializeIntoVitalLFOPreset())
			file.close()

	def equationUsesZ():
		match = re.search(r'[^a-z]*z[^a-z]*', state.equation.get())
		return match is not None

	def exportAsWavetable():
		file = filedialog.asksaveasfile(
			mode = 'w',
			filetypes=(
				("FLAC", "*.flac"),
				("AIFF", "*.aiff"),
				("WAV", "*.wav"),),
			# defaultextension = '.flac',
			initialfile = state.name.get().strip())
		if file is not None:
			filename = file.name
			filename_lower = filename.lower()
			file.close()

			# TODO: check if z is being used
			data = []
			if state.numFrames.get() == 1 or not equationUsesZ():
				z = clampZToNumFrames(state.z.get())
				points = getPoints(2048, z)
				if points['error'] is None:
					data.extend(points['y'])
			else:
				inc = 1 / (state.numFrames.get()  - 1)
				pos = 0
				for i in range(int(state.numFrames.get())):
					z = clampZToNumFrames(pos)
					points = getPoints(2048, z)
					if points['error'] is None:
						data.extend(points['y'])
					pos += inc

			data = scaleToRange(data, -1.0, 1.0)

			subtype = 'PCM_24' if filename_lower.endswith('.flac') else 'FLOAT'

			sf.write(
				file=filename,
				data=data,
				samplerate=48000 * 2,
				subtype=subtype)

	def handleShiftLeftButtonClick():
		equationTextInput.icursor(equationTextInput.index(tk.INSERT)-1)
		setFocus(1)

	def handleShiftRightButtonClick():
		equationTextInput.icursor(equationTextInput.index(tk.INSERT)+1)
		setFocus(1)

	def handleClearButtonClick():
		equationTextInput.delete(0,tk.END)
		setFocus(1)

	def handleBackspaceButtonClick():
		equationTextInput.delete(equationTextInput.index(tk.INSERT)-1,equationTextInput.index(tk.INSERT))
		setFocus(1)

	reg = root.register(intEntryCallback)

	state = AppState()

	# Header
	header = ttk.Frame(main)
	header.grid(row = 0, column = 0)

	ttk.Label(header, text = "LFO Name: ") .grid(row = 0, column = 0, sticky = tk.E)
	ttk.Label(header, text = "  Preset: ") .grid(row = 0, column = 4, sticky = tk.E)

	nameTextInput = ttk.Entry(header, width = 40, textvariable=state.name) # SET THE LFO NAME
	nameTextInput.grid(row = 0, column = 1, sticky = tk.W)

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

	# ttk.Separator(main, orient = 'horizontal') .grid(row = 1, column = 0, sticky = tk.NSEW, pady = PADDING)

	# Adder
	adderFrame = ttk.LabelFrame(main)
	adder = ttk.Frame(adderFrame)
	adderFrame.grid(row=2, column=0, sticky = tk.NSEW)
	adderFrame.columnconfigure(1, weight=2)
	adder.grid(row = 0, column = 0, sticky = tk.N, columnspan=2)

	# TRIG
	ttk.Label(adder, text = "Trig: ") .grid(row = 0, column = 0, sticky = tk.W)
	trigSelected = tk.StringVar()
	ttk.OptionMenu(adder, trigSelected, trigOptions[0], *trigOptions) .grid(row = 1, column = 0, sticky = tk.NSEW)
	trigAddButton = ttk.Button(adder, text = "Add", command = addTrigToEquation)
	trigAddButton.grid(row = 1, column = 1, sticky = tk.W, padx = PADDING)
	trigAddButtonTT = Tooltip(trigAddButton, "Add to raw equation at index")

	# Operators
	ttk.Label(adder, text = "Operators: ") .grid(row = 0, column = 2, sticky = tk.W)
	OperatorSelected = tk.StringVar()
	ttk.OptionMenu(adder, OperatorSelected, operatorOptions[0], *operatorOptions) .grid(row = 1, column = 2, sticky = tk.NSEW)
	operatorsAddButton = ttk.Button(adder, text = "Add", command = addOperatorToEquation)
	operatorsAddButton.grid(row = 1, column = 3, sticky = tk.NSEW, padx = PADDING)
	operatorsAddButtonTT = Tooltip(operatorsAddButton, "Add to raw equation at index")

	# Symbols
	ttk.Label(adder, text = "Symbols: ") .grid(row = 0, column = 4, sticky = tk.W)
	SymbolSelected = tk.StringVar()
	ttk.OptionMenu(adder, SymbolSelected, symbolOptions[0], *symbolOptions) .grid(row = 1, column = 4, sticky = tk.NSEW)
	symbolsAddButton = ttk.Button(adder, text = "Add", command = addSymbolToEquation)
	symbolsAddButton.grid(row = 1, column = 5, sticky = tk.NSEW, padx = PADDING)
	symbolsAddButtonTT = Tooltip(symbolsAddButton, "Add to raw equation at index")

	# Variables
	ttk.Label(adder, text = "Variables: ") .grid(row = 2, column = 0, sticky = tk.W)
	VariableSelected = tk.StringVar()
	ttk.OptionMenu(adder, VariableSelected, variableOptions[0], *variableOptions) .grid(row = 3, column = 0, sticky = tk.NSEW)
	varAddButton = ttk.Button(adder, text = "Add", command = addVariableToEquation)
	varAddButton.grid(row = 3, column = 1, sticky = tk.NSEW, padx = PADDING)
	varAddButtonTT = Tooltip(varAddButton, "Add to raw equation at index")

	# Misc
	ttk.Label(adder, text = "Misc: ") .grid(row = 2, column = 2, sticky = tk.W)
	MiscSelected = tk.StringVar()
	ttk.OptionMenu(adder, MiscSelected, miscOptions[0], *miscOptions) .grid(row = 3, column = 2, sticky = tk.NSEW)
	miscAddButton = ttk.Button(adder, text = "Add", command = addMiscToEquation)
	miscAddButton.grid(row = 3, column = 3, sticky = tk.NSEW, padx = PADDING)
	miscAddButtonTT = Tooltip(miscAddButton, "Add to raw equation at index")

	# Number
	ttk.Label(adder, text = "Number: ") .grid(row = 2, column = 4, sticky = tk.W)
	NumberSelected = ttk.Entry(adder, width = 16)
	NumberSelected.grid(row = 3, column = 4, sticky = tk.NSEW)
	numAddButton = ttk.Button(adder, text = "Add", command = addNumberToEquation)
	numAddButton.grid(row = 3, column = 5, sticky = tk.NSEW, padx = PADDING)
	numAddButtonTT = Tooltip(numAddButton, "Add to raw equation at index")

	ttk.Label(adder, text = "Resolution: ") .grid(row = 4, column = 0, sticky = tk.E)
	resolutionSlider = ttk.Scale(adder,from_ = 4, to = 100, orient = 'horizontal', variable = state.resolution, value = 10, command = handleResolutionChanged)
	resolutionSlider.grid(row = 4, column = 1, columnspan = 4, sticky = tk.NSEW, pady = PADDING, padx = PADDING)
	ttk.Label(adder, textvariable = state.resolution) .grid(row = 4, column = 5, sticky = tk.W)

	ttk.Label(adder, text = "x Start: ") .grid(row = 5, column = 0, sticky = tk.E)
	ttk.Label(adder, text = "x End: ") .grid(row = 5, column = 2, sticky = tk.E)
	xStartTextField = ttk.Entry(adder, width = 10, textvariable=state.xStart)
	xStartTextField.grid(row = 5, column = 1, sticky = tk.W)

	xEndTextField = ttk.Entry(adder, width = 10, textvariable=state.xEnd)
	xEndTextField.grid(row = 5, column = 3, sticky = tk.W)

	ttk.Label(adder, text = "y Start: ") .grid(row = 6, column = 0, sticky = tk.E)
	ttk.Label(adder, text = "y End: ") .grid(row = 6, column = 2, sticky = tk.E)
	yStartTextField = ttk.Entry(adder, width = 10, textvariable=state.yStart)
	yStartTextField.grid(row = 6, column = 1, sticky = tk.W)
	yEndTextField = ttk.Entry(adder, width = 10, textvariable=state.yEnd)
	yEndTextField.grid(row = 6, column = 3, sticky = tk.W)

	xStartTextField.config(validate="key", validatecommand=(reg, '%P'))
	xEndTextField.config(validate="key", validatecommand=(reg, '%P'))
	yStartTextField.config(validate="key", validatecommand=(reg, '%P'))
	yEndTextField.config(validate="key", validatecommand=(reg, '%P'))

	ttk.Label(adder, text = "x Phase Offset:" ) .grid(row = 7, column = 0, sticky = tk.E)

	xPhase = ttk.Scale(adder, from_ = -1, to = 1, orient = 'horizontal', variable = state.phase, value = 0, command = handlePhaseChanged)
	xPhase.grid(row = 7, column = 1, columnspan = 4, sticky = tk.NSEW, pady = PADDING, padx = PADDING)
	xPhase.bind('<Double-1>', lambda event: xPhase.set(0))
	ttk.Label(adder, textvariable = state.phase) .grid(row = 7, column = 5, sticky = tk.W)

	ttk.Label(adder, text="z Position").grid(row=8, column=0, sticky = tk.E)
	zScale = ttk.Scale(adder, from_ = 0, to = 1, orient = 'horizontal', variable = state.z, value = 0, command = handleZPositionChanged)
	zScale.grid(row = 8, column = 1, columnspan = 4, sticky = tk.NSEW, pady = PADDING, padx = PADDING)
	zScale.bind('<Double-1>', lambda event: zScale.set(0))
	ttk.Label(adder, textvariable = state.z) .grid(row = 8, column = 5, sticky = tk.W)

	ttk.Label(adder, text="Num Z Frames").grid(row=9, column=0, sticky = tk.E)
	numFramesScale = ttk.Scale(adder, from_ = 1, to = 256, orient = 'horizontal', variable = state.numFrames, value = 0, command = handleNumFramesChanged)
	numFramesScale.grid(row = 9, column = 1, columnspan = 4, sticky = tk.NSEW, pady = PADDING, padx = PADDING)
	numFramesScale.bind('<Double-1>', lambda event: numFramesScale.set(256))
	ttk.Label(adder, textvariable = state.numFrames) .grid(row = 9, column = 5, sticky = tk.W)

	# ttk.Separator(main, orient = 'horizontal') .grid(row = 3, column = 0, sticky = tk.NSEW, pady = 10)

	# Equater
	equater = ttk.Frame(main)
	equater.grid(row = 4, column = 0)

	ttk.Label(equater, text = "Raw Equation: ") .grid(row = 0, column = 0, sticky = tk.NSEW)

	equationTextInput = ttk.Entry(equater, width = 95, textvariable = state.equation)
	equationTextInput.grid(row = 1, column = 0, sticky = tk.W, ipady = 5)

	state.equation.trace_add('write', handleEquationUpdated)

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

	# ttk.Separator(main, orient = 'horizontal') .grid(row = 5, column = 0, sticky = tk.NSEW, pady = PADDING)

	# Previewer
	previewer = ttk.Frame(main)
	previewer.grid(row = 6, column = 0, sticky = tk.N)
	previewer.columnconfigure(0, weight = 2)

	prettyEquationString = tk.StringVar()


	prettyEquation = ttk.Entry(previewer, textvariable=prettyEquationString, state='readonly', width=108)
	prettyEquation.grid(row = 0, column = 0, sticky = tk.N, columnspan=8)

	prettyEqScroll = ttk.Scrollbar(previewer, orient='horizontal', command=prettyEquation.xview)
	prettyEquation.config(xscrollcommand=prettyEqScroll.set)
	prettyEqScroll.grid(row=1,column=0,sticky=tk.NSEW,columnspan=2)

	xyPlot = tk.Canvas(previewer, width = canvasWidth, height = canvasHeight, bg = 'white')
	xyPlot.grid(row = 2, column = 0, sticky = tk.N)

	XYPlotOptions = ttk.Frame(previewer)
	XYPlotOptions.grid(row=2,column=1,sticky=tk.NSEW)

	updatePlotButton = ttk.Button(XYPlotOptions, text = "Regenerate Plot", command = updateXYPlot)
	updatePlotButton.grid(row = 0, column = 0, sticky = tk.NSEW, pady = (0,PADDING),columnspan=2)
	updatePlotButtonTT = Tooltip(updatePlotButton, "Force updates the x/y plot")

	ttk.Button(XYPlotOptions, text = "Copy Vital LFO", command = copyLFOPresetToClipboard) .grid(row = 1, column = 0, sticky = tk.NSEW, pady = (0,PADDING),columnspan=2)
	ttk.Button(XYPlotOptions, text = "Export LFO File", command = exportAsLFOPreset) .grid(row = 3, column = 0, sticky = tk.NSEW, pady = (0,PADDING),columnspan=2)
	ttk.Button(XYPlotOptions, text = "Export Waveform", command = exportAsWavetable) .grid(row = 4, column = 0, sticky = tk.NSEW, pady = (0,PADDING),columnspan=2)

	ttk.Label(XYPlotOptions, text = "View Points: ") .grid(row = 5, column = 0, sticky = tk.E)
	viewPoints = tk.BooleanVar()
	viewPoints.set(True)
	ttk.Checkbutton(XYPlotOptions, var = viewPoints) .grid(row = 5, column = 1, sticky = tk.W)

	ttk.Label(XYPlotOptions, text = "View Unsmoothed: ") .grid(row = 6, column = 0, sticky = tk.E)
	viewUnsmoothedVal = tk.BooleanVar()
	viewUnsmoothedVal.set(True)
	ttk.Checkbutton(XYPlotOptions, var = viewUnsmoothedVal) .grid(row = 6, column = 1, sticky = tk.W)

	ttk.Label(XYPlotOptions, text = "Smooth: ") .grid(row = 7, column = 0, sticky = tk.E)
	ttk.Checkbutton(XYPlotOptions, var = state.smooth) .grid(row = 7, column = 1, sticky = tk.W)

	# StatusBar
	# status = ttk.Label(root2, text = 'Welcome to EquaFO!', borderwidth = 1, relief = "sunken")
	# status.grid(row = 1, column = 0, sticky = tk.NSEW, ipady = 3)

	def setFocus(event):
		equationTextInput.focus_set()
	def endFocus(event):
		root.focus_set()
	# KEYBINDINGS
	# root.bind("<Return>", updateEvent)
	root.bind("<ButtonRelease-1>", lambda e: updateXYPlot())
	adder.bind("<Enter>", setFocus)
	equationTextInput.bind("<Enter>",setFocus)
	eqButtons.bind("<Enter>",setFocus)
	adder.bind("<Leave>", endFocus)

	initPreset()
	root.mainloop()

if __name__ == '__main__':
	main()
