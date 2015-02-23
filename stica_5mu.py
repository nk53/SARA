#!/usr/bin/env python

import sima
from sima.segment import STICA
from post_process_rois import IdROIs

video = "corrected_pt2.tif"
analysis_dir = "stica_5mu.sima"

print "[Creating SIMA analysis directory: %s]" % analysis_dir
seq = sima.Sequence.create('TIFF', video)
dataset = sima.ImagingDataset([seq], analysis_dir)

print "[Finding ROIs using stICA method (this could take a while . . .)]"
stica = STICA(components=20, mu=0.5, overlap_per=0.2)
stica.append(IdROIs())
rois = dataset.segment(stica, label="stICA ROIs")
print dataset.ROIs.keys()
print len(dataset.ROIs['stICA ROIs']), "ROIs found"

print "[Done]"
