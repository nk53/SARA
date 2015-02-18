#!/usr/bin/env python

import sima
import sima.segment

video = "corrected_pt2.tif"
analysis_dir = "stica_0ol.sima"

print "[Creating SIMA analysis directory: %s]" % analysis_dir
seq = sima.Sequence.create('TIFF', video)
dataset = sima.ImagingDataset([seq], analysis_dir)

print "[Finding ROIs using stICA method (this could take a while . . .)]"
stica = sima.segment.STICA(components=5)
rois = dataset.segment(stica, label="stICA ROIs")
# print out some stats
print dataset.ROIs.keys()
print len(dataset.ROIs['stICA ROIs']), "ROIs found"

print "[Done]"
