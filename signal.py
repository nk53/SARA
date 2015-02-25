#!/usr/bin/env python

from sima.imaging import ImagingDataset

video = "image.tif"
analysis_dir = "stica_test.sima"
outfile = "all.csv"

print "[Loading SIMA analysis directory: %s]" % analysis_dir
dataset = ImagingDataset.load(analysis_dir)

signal = dataset.signals()['signal']
dataset.export_signals(outfile)

print "[Done]"
