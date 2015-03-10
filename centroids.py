#!/usr/bin/env python
from os.path import join as path_join
from sima.ROI import ROIList
from PIL import Image
from pandas import DataFrame
import matplotlib.pyplot as plt

analysis_dir = "stica_test.sima"
outfile = "centroids.csv"

# get list of ROIs from SIMA analysis directory
rois = ROIList.load(path_join(analysis_dir, "rois.pkl"))

# get list of all objects' centroids
centroids = []
indices = []
for roi in rois:
  coords = roi.coords
  rid = roi.id
  if len(coords) > 1:
    print "Warning: Roi%s has >1 coordinate set" % rid
  centroid = roi.polygons.geoms[0].centroid
  xy = [centroid.x, centroid.y]
  centroids.append(xy)
  indices.append(rid)

# export to CSV file
data = DataFrame(centroids, index=indices, columns=['x', 'y'])
data.index.name = 'RoiID'
data.to_csv(outfile)
