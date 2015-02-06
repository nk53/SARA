#!/usr/bin/env python

import sima
from sima.motion import HiddenMarkov2D

video = "image.tif"
analysis_dir = "hmm_test.sima"

seq = sima.Sequence.create('TIFF', 'original.tif')
ds = HiddenMarkov2D(max_displacement=[50, 50], n_processes=2).correct([seq], 'test-sima-1.0.sima')
ds.export_frames([[['corrected.tif']]])
