#!/opt/python/bin/python2.7
# Execute SARA analysis in series (as opposed to parallel) on one machine
from os import environ, mkdir, walk
from os.path import abspath, join, isdir
from sys import argv
from shutil import rmtree
from sara import SaraUI

if len(argv) != 4:
  if len(argv) == 2 and argv[1] == '-1':
    argv.append('')
    argv.append('')
  else:
    program_name = argv[0]
    print "Usage: %s job_id settings_file out_dir" % program_name
    print "  'job_id' is the nth image file to analyze"
    print "  'settings_file' is the settings file to use for analysis"
    print "  'out_dir' is the directory where output will go"
    print ""
    print "  If job_id is -1, then no SIMA analysis will be done; instead,"
    print "  the number of image files found in the data dir will be output"
    exit()

# Nth image file to analyze
job_id = int(argv[1])
# File containing the settings we want use on all directories
settings_file = argv[2]
# Output directory
outdir = argv[3]

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
if job_id != -1:
  job_dir = "%s" % outdir
  mc_dir = "%s/corrected" % outdir
  plots_dir = "%s/plots" % outdir
  signals_dir = "%s/signals" % outdir
  analysis_dir = "%s/analysis" % outdir
  #for d in [mc_dir, plots_dir, signals_dir, analysis_dir]:
  #  if isdir(d):
  #    print "Cleaning", abspath(d)
  #    rmtree(d)
  #  mkdir(d)

# Find all of the image files
home = environ['HOME']
data_dir = join(home, 'data')
visited_dirs = []
nimages = 0
images = []
for dirpath, dirnames, filenames in walk(data_dir):
  for filename in filenames:
    # Run SARA, but only use original Control recordings
    if filename.endswith('.tif'):
      visited_dirs.append(dirpath)
      images.append(join(dirpath, filename))
      nimages += 1
      # run analysis on the nth image only
      if job_id == nimages:
        run_sara(dirpath, filename, settings_file, analysis_dir, mc_dir,
                   plots_dir, signals_dir)

if job_id == -1:
  for image_name in images:
    print image_name
  print nimages, "images found"
else:
  print "Analysis done"
