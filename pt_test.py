#!/usr/bin/env python

import sima
from sima.motion import PlaneTranslation2D

video = "image.tif"
analysis_dir = "hmm_test.sima"

seq = sima.Sequence.create('TIFF', 'original.tif')
ds = PlaneTranslation2D(max_displacement=[100, 100]).correct([seq], 'pt_test.sima')
ds.export_frames([[['corrected_pt.tif']]])
