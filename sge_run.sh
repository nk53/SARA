#!/bin/bash
#$ -S /bin/bash              # execution shell
#$ -N SARA                   # name of job
#$ -o /home/nkern/out/sara.o # output file
#$ -e /home/nkern/out/sara.e # errors file
#$ -M natek5309@gmail.com    # who to mail
#$ -m e                      # mailing options
##$ -t 1-6                    # array options

# To see what commands would look like instead of running them, (useful
#   for testing before you use qsub) run like this:
#     ./sge_run.sh test
# (Technically, any command line option will do the same thing)
#
# Run without command line options to actually execute analysis commands

SARADIR=$HOME/sara
TASKOUT=$HOME/out/sara.o$SGE_TASK_ID
TASKERR=$HOME/out/sara.e$SGE_TASK_ID

SETTINGS_SINGLE=settings.csv

cd $SARADIR

if [ ! -z $1 ]; then
  SGE_TASK_ID=1 # for debugging only
fi

# Make sure this line is set according to your job array settings
while [ $SGE_TASK_ID -le $ni ]; do
  settings=()
  # wildcard expansion only works if the directory exists
  if [ -d settings ]; then
    settings=( settings/* )
  fi
  # every 48 tasks, go to next setting file and redo analysis
  taskm1=$(($SGE_TASK_ID - 1))
  setting_i=$(($taskm1 / $ni))
  task_i=$(($taskm1 % $ni + 1))
  
  settings_name=`basename ${settings[$setting_i]}`
  if [ $numset == "single" ]; then
    settings_file=$SARADIR/$SETTINGS_SINGLE
    outdir=$SARADIR/out
  else
    settings_file=$SARADIR/settings/${settings_name}
    outdir=$SARADIR/out/${settings_name}
  fi
  
  CMD="./run_single.py $task_i ${settings_file} $outdir"
  echo "(SGE_TASK_ID $SGE_TASK_ID): $CMD"
  
  if [ -z $1 ]; then
    cd $SARADIR/out
    if [ $numset == "multi" ]; then
      # create a directory with the same name as the settings file
      if [ ! -d ${settings_name} ]; then
        mkdir ${settings_name}
        cd ${settings_name}
      fi
    fi
    mkdir corrected plots signals analysis
    cd $SARADIR
    # Run command here
    $CMD > $TASKOUT 2> $TASKERR
    exit 0
  else
    # Debugging mode
    ((SGE_TASK_ID++))
  fi
done
