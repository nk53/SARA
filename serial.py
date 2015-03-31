#!/usr/bin/env python
# Execute SARA analysis in series (as opposed to parallel) on one machine
from os import mkdir, walk
from os.path import abspath, join, isdir
from shutil import rmtree
from sara import SaraUI

def run_sara(dirpath, recording, settings_file, analysis_dir, mc_dir,
               plots_dir, signals_outdir):
  """Use settings from previous run to analyze a new directory"""
  # remove .tif extension
  no_ex = recording[:recording.find('.tif')]
  # output locations
  sima_dir = join(analysis_dir, no_ex + '.sima')
  mc_infile = join(dirpath, recording)
  mc_outfile = join(mc_dir, recording)
  plot_out = join(plots_dir, recording)
  signal_out = join(signals_outdir, no_ex + '.csv')
  
  # run analysis
  print "Analyzing", recording
  ui = SaraUI(sima_dir, settings_file)
  ui.motionCorrect(mc_infile, mc_outfile, use_settings=True)
  ui.segment(use_settings=True)
  ui.visualize(plot_out, use_settings=True)
  ui.exportSignal(signal_out, use_settings=True)

# Set up output directories for motion-corrected images, plots showing
# segmentation results, and signals
# MAKE SURE THESE NAMES ARE CORRECT OR ELSE ALL YOUR DATA WILL BE DELETED
mc_dir = "corrected"
plots_dir = "plots"
signals_dir = "signals"
analysis_dir = "analysis"
for d in [mc_dir, plots_dir, signals_dir, analysis_dir]:
  if isdir(d):
    print "Cleaning", abspath(d)
    rmtree(d)
  mkdir(d)

# File containing the settings we want use on all directories
settings_file = "settings.csv"

# Find all of the .tif files
data_dir = '/Users/nathan/work/sean/data'
visited_dirs = []
for dirpath, dirnames, filenames in walk(data_dir):
  for filename in filenames:
    # Run SARA, but only use original Control recordings
    if not dirpath in visited_dirs \
    and 'Control' in dirpath \
    and filename.endswith('.tif'):
      visited_dirs.append(dirpath)
      run_sara(dirpath, filename, settings_file, analysis_dir, mc_dir,
                 plots_dir, signals_dir)
print "Analysis done"
