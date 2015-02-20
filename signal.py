#!/usr/bin/env python

from sima.imaging import ImagingDataset

video = "image.tif"
analysis_dir = "stica_test.sima"

print "[Loading SIMA analysis directory: %s]" % analysis_dir
dataset = ImagingDataset.load(analysis_dir)

signal = dataset.signals()['signal']
import pdb; pdb.set_trace()
dataset.save(analysis_dir)
dataset.export_signals('all.csv')

print "[Done]"
