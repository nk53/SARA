#!/usr/bin/env python

import sima
import sima.segment

video = "corrected_pt2.tif"
analysis_dir = "stica_long.sima"

print "[Creating SIMA analysis directory: %s]" % analysis_dir
seq = sima.Sequence.create('TIFF', video)
dataset = sima.ImagingDataset([seq], analysis_dir)

print "[Finding ROIs using stICA method (this could take a while . . .)]"
stica = sima.segment.STICA(components=50, overlap_per=0.2)
rois = dataset.segment(stica, label="stICA ROIs")
print dataset.ROIs.keys()
print len(dataset.ROIs['stICA ROIs']), "ROIs found"

print "[Done]"