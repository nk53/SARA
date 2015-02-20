#!/usr/bin/env python

import sima
import matplotlib.pyplot as plt
from pandas import DataFrame

video = "image.tif"
analysis_dir = "stica_test.sima"

print "[Loading SIMA analysis directory: %s]" % analysis_dir
dataset = sima.ImagingDataset.load(analysis_dir)

print "[Extracting signals from ROIs]"
rois = dataset.ROIs['stICA ROIs']
signals = dataset.extract(rois=rois, label='signal')

print "[Done]"
