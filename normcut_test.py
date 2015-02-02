#!/usr/bin/env python

import sima
import sima.motion
from sima.iterables import MultiPageTIFF

video = "image.tif"
analysis_dir = "normcut_test.sima"

print "[Creating SIMA analysis directory: %s]" % analysis_dir
iterables = [[MultiPageTIFF(video)]]

dataset = sima.ImagingDataset(iterables, analysis_dir)

print "[Finding ROIs using normcut method (this could take a while . . .)]"
rois = dataset.segment(method='normcut', label="Normcut ROIs", num_pcs=5)
dataset.ROIs.keys()
print "[Done]"
