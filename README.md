# EquoFO

An equation based LFO generator for the GHOST and Vital synthesizers

# Basic HowTo:

-   Create your equation by adding functions to the Raw Equation box
-   This can be done by pressing the 'Add' buttons next to the function dropdowns
-   Press Copy LFO to Clipboard, or Export LFO to file, to save your LFO

# Advanced

## The Header

-   The header is at the very top of the application and controls the name of the LFO, smoothing, and presets
-   The buttons to the left of smoothing are for preset manipulation, their function can be seen in the status bar while hovering

## The Equation Generator

-   The equation generator is directly beneath the header and makes equation writing fast, efficient, and user-friendly
-   Simply select from the dropdown menu the function you would like to add, and then press the 'Add' button next to it.
-   The 'Add' button will add the function to wherever the cursor is in the Equation Box

## Graph Settings

-   The graph settings below the Equation Generator are for selecting where and how the equation will render
-   Resolution controlls how many points will be sampled in the given x domain, defined by x Start and x End
-   x Start and x End control domain, while y Start and y End control the range of the function. These can be basic math functions such as "3+1" or "1218932657/329865"
-   x Phase is for making minor adjustments to the graph, nudging the x coords -1 to 1 units over

## Raw Equation

-   The Raw Equation is where the Equation Generator puts the functions
-   This can be typed directly into, if you know what your doing, or can be navigated with the buttons below
-   EquoFo supports most functions from the following python libraries: "math","numpy","random". If you have python knowledge, you can use almost any function in the equation generator.
-   Scale Y to Fit will set the y Start and y End to the min and max of the equation, keeping everything in range

## The Previewer

-   The previewer previews the Raw Equation
-   Above it is a formated version of the Raw Equation
-   Below are a few buttons:
-   Update - reloads the graph
-   Copy preset to Clipboard - copies the LFO to clipboard so you can paste it directly into Vital. GHOST not supported.
-   Export preset - Exports the points in either GHOST or Vital LFO preset formats
-   Export wavetable - Exports the wave as a 2048 point audio file. Supports `.flac`, `.aiff` and `.wav`
-   View Points - Toggles display of points of the graph. Smoothing not applied
-   View Unsmoothed - Toggles display of a second graph with the unsmoothed points

## Note

EquoFo was compiled with pyinstaller, so that means Windows Defender will detect it as a Trojan (thanks malware devs!). Run it if you like, or install python to run from source.
