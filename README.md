SARA: SIMA And RAIN Analysis
============================

Demonstrates use of SIMA to analyze a TIFF stack of a confocal microscopy imaging session.

The following files make for a complete example: `sara.py`, `SARA.ipynb`, `original.tif`, and `rgb.png`

# Limitations
 
Currently I only support single-channel imaging.

# Prerequisites: What you need to use SARA

1. A solid understanding of programming with Python (especially if you will be using `serial.py`)
2. The [SIMA 1.0](http://www.losonczylab.org/sima/1.0/index.html) module must be installed on your computer
3. One or more single-channel confocal microscopy video recordings stored as TIFF stacks.

# Analyzing multiple recordings

`serial.py` is an example showing how to run several analysis jobs automatically. It is NOT intended to be used without first understanding it and modifying it to work with your own system (e.g. if you use a computing cluster).
