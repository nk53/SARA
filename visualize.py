#!/usr/bin/env python

import sima
import matplotlib.pyplot as plt
from pandas import DataFrame

def show_rois(roi_xy, image, size=6):
  '''
  Shows an ROI centroid location scatter plot overlaid an image
  
  roi_xy  DataFrame containing X,Y centroid locations indexed by ROI id
  image   relative path to image for ROI overlay
  size    size (in points) of circles to use for ROI overlay
  '''
  
  fig, ax = plt.subplots()
  

video = "image.tif"
analysis_dir = "stica_test.sima"

print "[Loading SIMA analysis directory: %s]" % analysis_dir
dataset = sima.ImagingDataset.load(analysis_dir)


import pdb; pdb.set_trace()
#dataset.ROIs

print "[Plotting ROIs]"
stica = sima.segment.STICA(components=5)
rois = dataset.segment(stica, label="stICA ROIs")
print dataset.ROIs.keys()

print "[Done]"
