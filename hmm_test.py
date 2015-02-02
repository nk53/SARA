#!/usr/bin/env python

import sima
import sima.motion
from sima.iterables import MultiPageTIFF

video = "image.tif"
analysis_dir = "hmm_test.sima"

print "[Creating SIMA analysis directory: %s]" % analysis_dir
iterables = [[MultiPageTIFF(video)]]

print "[Applying hidden Markov model]"
dataset = sima.motion.hmm(iterables, analysis_dir, channel_names=['hmm_test'], max_displacement=[10, 10])
