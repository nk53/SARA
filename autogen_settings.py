#!/opt/python/bin/python2.7
from os import listdir
# Where to put the new settings
outdir = "settings"
# Exit if there's anything in the settings folder
if len(listdir(outdir)) > 0:
  exit("Please empty %s before continuing" % outdir)

print "Please wait . . ."
import csv
from warnings import simplefilter
from os.path import join
from numpy import arange, array
from pandas import Series
# User doesn't need to know about deprecated stuff
simplefilter("ignore")
from sklearn.utils.extmath import cartesian
from sara import CommandLineInterface as CLI

def build_names(setting, range_params):
  '''Returns the names of settings in param_file'''
  return ['_'.join([setting, rp]) for rp in range_params]

def build_filename(abbrs, *args):
  '''Builds a filename based on abbreviations'''
  assert len(abbrs) >= len(args), "Abbreviations list is too small"
  assert len(abbrs) <= len(args), "Abbreviations list is too large"
  filename = ''
  for index, abbr in enumerate(abbrs):
    value = args[index]
    if abbr != 'c':
      value *= 100
    filename += '%s%.0f' % (abbr, value)
  return filename

# File specifying which parameters to run
param_file = "param_settings.csv"
# File with default parameters
settings_file = "settings.csv"
# Settings to iterate over
it_set = ['mu', 'overlap_per', 'components']
# Abbreviations for settings file; must match order of it_set
abbr_set = ['mu', 'op', 'c']

# Range parameters
r_params = ['start', 'stop', 'step']


params = Series.from_csv(param_file)
settings = Series.from_csv(settings_file)

# Names of all the settings in param_file
all_names = array([build_names(name, r_params) for name in it_set])
# Values to use in arange
rvals = [[params[name] for name in names] for names in all_names]
# The actual ranges
ranges = [arange(*rv) for rv in rvals]

# All parameter combinations based on the ranges in rvals
param_space = cartesian(ranges)

# Give user an opportunity to stop if there's too many parameters
size = 0.004 * len(param_space) # in megabytes
warning = "Will create %d settings (%.2f MB) files in settings/, proceed (y/n)? " \
             % (len(param_space), size)
if not CLI().getBoolean(warning):
  exit("Skipping file creation")

# Create settings files for each combination
for customs in param_space:
  for index, setting in enumerate(it_set):
    settings[setting] = customs[index]
  filename = join(outdir, build_filename(abbr_set, *customs))
  settings.to_csv(filename)

print "Done"
