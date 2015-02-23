#!/usr/bin/env python
from os.path import join as path_join
from sima.ROI import ROIList
from PIL import Image
import matplotlib.pyplot as plt

# SIMA anlaysis directory
analysis_dir = "stica_test.sima"

# change default line colors and line width
#plt.rc('axes', color_cycle = ['b', 'r', 'm', 'brown', 'k', 'grey'])
cc = ['blue', 'red', 'magenta', 'brown', 'cyan', 'orange',
      'yellow', 'green']
plt.rc('axes', color_cycle = cc) 
plt.rc('lines', linewidth=2)

# prepare background image
im = Image.open("rgb.png")
im_width, im_height = im.size
plt.xlim(xmin=0, xmax=im_width)
plt.ylim(ymin=0, ymax=im_height)
plt.imshow(im)

# get list of ROIs from SIMA analysis directory
rois = ROIList.load(path_join(analysis_dir, "rois.pkl"))

# plot all of the ROIs, warn if an ROI has more than one coordinate set
for roi in rois:
  coords = roi.coords
  if len(coords) > 1:
    print "Warning: Roi%s has >1 coordinate set" % roi.id
  x = coords[0][:,0]
  y = coords[0][:,1]
  plt.plot(x, y)

plt.show()
