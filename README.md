# EquoFO

An equation based LFO generator for the GHOST and Vital synthesizers

## Dependencies

Install them all using `pip install numpy scipy soundfile`

# Advanced

## The Header

![image](https://user-images.githubusercontent.com/71950453/220758147-e1c1dbee-1a4a-48ec-ae82-1fb1480b161e.png)

-   Can be used to define the LFO Name and manage LFO presets
-   Hover on buttons to see their function

## The Equation Generator

![image](https://user-images.githubusercontent.com/71950453/220758868-79a7b69b-3dcc-4a39-83dc-6fde47a47846.png)

-   Expand drop-down menues to select a different function to use, press **Add** to insert it into the **Raw Equation** Box
-   The **Raw Equation** box is able to be typed to manually and supports all functions from python, numpy (np), and random
-   **Resolution** controls how many points will be sampled for the plot
-   **xStart** and **xEnd** control which x-values will be sampled
-   **yStart** and **yEnd** control which y-values will be used
-   **xPhase** nudges the sampled points in either direction

## The Equation Viewer

![image](https://user-images.githubusercontent.com/71950453/220760142-b99a4a1d-f0a7-460d-86a9-d4ba30485eb8.png)

-   The Equation Viewer plots the **Raw Equation** given the bounds put out in xStart/End and yStart/End
    -   If **Scale Y to fit** is checked, y-bounds will automatically be set
-   **View Points** toggles point displays on the plot
-   **View Unsmoothed** displays the unsmoothed lines
-   **Smooth** displays a smoothed curve, an exported smooth LFO will look slightly different
-   **Regenerate Plot** replots the equation, usefull for rerolling things involving random numbers
-   **Copy Vital LFO** copies the currently ploted points into a Vital LFO format allowing it to be directly pasted into Vital
-   **Export LFO File** exports the currently ploted points to either a GHOST or Vital LFO file
-   **Export Waveform** renders the equation to a 2048 point resolution and exports it to a file. Supports `.flac`, `.aiff` and `.wav`
