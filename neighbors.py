#!/usr/bin/env python
from os.path import join as path_join
from pandas import DataFrame
from sima.ROI import ROIList

analysis_dir = "stica_test.sima"
outfile = "neighbors.csv"
out_headers = ["roi", "neighbor", "distance"]

# neighbors cannot be farther than this distance (in pixels)
max_dist = 10.0

rois = ROIList.load(path_join(analysis_dir, "rois.pkl"))

# get distance of every object to every other object, record ones
# less than max_dist away from each other
neighbors = []
for index, roi in enumerate(rois):
  for other in rois[index+1:]:
    this_obj = roi.polygons.geoms[0]
    other_obj = other.polygons.geoms[0]
    dist = this_obj.distance(other_obj)
    if dist <= max_dist:
      neighbors.append([roi.id, other.id, dist])

output = DataFrame(neighbors, columns=out_headers)
output.to_csv(outfile)
