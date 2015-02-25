#!/usr/bin/env python
from pandas import read_csv, Index, Series

# both input and output
datafile = "all.csv"

# conversion factor, MUST BE FLOAT!
frames_to_time = 1.28

# read in tab-separated data
data = read_csv(datafile, sep='\t')

# change name of 'frames' col to 'time'
old_cols = data.columns.tolist()
new_cols = [old_cols[0], 'time'] + old_cols[2:]
# preserve useless labels/tags in case they are useful someday
lab_tag = data['frame'].tolist()[:2]

# cast frames from str to float so we can do math
times = map(float, data['frame'].tolist()[2:])
# convert frame number to time
times = map(lambda item: item*frames_to_time, times)

# prepare new data for output
times = Series(lab_tag + times)
data['frame'] = times
data.columns = new_cols

# export to CSV
data.to_csv(datafile, sep='\t')
