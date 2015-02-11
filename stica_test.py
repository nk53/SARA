#!/usr/bin/env python

import sima
import sima.segment

video = "original.tif"
analysis_dir = "stica_test.sima"

print "[Creating SIMA analysis directory: %s]" % analysis_dir
seq = sima.Sequence.create('TIFF', video)
dataset = sima.ImagingDataset([seq], analysis_dir)

print "[Finding ROIs using stICA method (this could take a while . . .)]"
stica = sima.segment.STICA(components=5)
rois = dataset.segment(stica, label="stICA ROIs")
print dataset.ROIs.keys()

print "[Done]"
