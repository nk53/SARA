#!/opt/python/bin/python2.7
# Reads a text file where lines separate command line options
# Output is the single-line concatenated option list
import csv
from sys import argv

if not len(argv) == 2:
  die("Usage: %s file_to_read" % argv[0])

filename = argv[1]

with open(filename) as fh:
  reader = csv.reader(fh)
  options = [i[0] for i in list(reader)]
  output = ' '.join(options)
  print output
