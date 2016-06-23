#!/bin/bash
# Handles submission of sge_run.sh

# Directory containing sara.py etc.
SARADIR=$HOME/sara
# Contains command line options for qsub
TASK_SETTINGS=task_settings.txt
# Build (most) qsub options
QSOPTS=`$SARADIR/scripts/parse_settings.py $TASK_SETTINGS`
# Script to submit to qsub
SCRIPT=sge_run.sh
# Settings file for running one set of settings
SINGLE_SETTINGS=settings.csv

# Also add custom variable for num of images found
NI=$(./run_single.py -1 2> /dev/null | tail -n1 | awk '{print $1}')
# Calculate how many tasks are needed
settings=()
if [ -d settings ]; then
  settings=( settings/* )
fi
numset=${#settings[@]}
if [ $numset -eq 0 ]; then
  numset=1
fi
NTASKS=$(($numset * $NI))

# Ensure out is empty
if [ ! -d $SARADIR/out ]; then
  echo "Creating $SARADIR/out"
  mkdir $SARADIR/out
elif [ "$(ls -A $SARADIR/out)" ]; then
  echo "Error: $SARADIR/out is not empty"
  exit
fi

# Set numset (whether to use single or multi settings)
if [ $numset -eq 0 ]; then
  if [ ! -e $SINGLE_SETTINGS ]; then
    echo "Error: $SINGLE_SETTINGS does not exist!"
    exit
  fi
  echo "Using $SINGLE_SETTINGS"
  numset=single
else
  numset=multi
fi

# Build command
QSOPTS="${QSOPTS} -t 1-$NTASKS -v ni=$NI,numset=$numset,ntasks=$NTASKS"
CMD="qsub $QSOPTS $SCRIPT"

# Run command
cd $SARADIR
echo "running $CMD"
$CMD
