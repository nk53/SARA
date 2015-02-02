#!/usr/bin/env python

import sima
import sima.segment
#import sima.motion
#from sima.iterables import MultiPageTIFF

video = "image.tif"
analysis_dir = "stica_test.sima"

print "[Creating SIMA analysis directory: %s]" % analysis_dir
#iterables = [[MultiPageTIFF(video)]]
#dataset = sima.ImagingDataset(iterables, analysis_dir)
seq = sima.Sequence.create('TIFF', 'original.tif')
dataset = sima.ImagingDataset([seq], analysis_dir)

print "[Finding ROIs using stICA method (this could take a while . . .)]"
stica = sima.segment.STICA(components=5)
rois = dataset.segment(stica, label="stICA ROIs")
import pdb; pdb.set_trace()
print dataset.ROIs.keys()

print "[Done]"
