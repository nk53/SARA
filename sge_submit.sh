#!/bin/bash
#$ -S /bin/bash              # execution shell
#$ -N SARA                   # name of job
#$ -o /home/nkern/out/sara.o # output file
#$ -e /home/nkern/out/sara.e # errors file
#$ -M natek5309@gmail.com    # who to mail
#$ -m e                      # mailing options
#$ -t 1-12                   # array options

# To see what commands would look like instead of running them, (useful
#   for testing before you use qsub) run like this:
#     ./sge_submit.sh test
# (Technically, any command line option will do the same thing)
# Run without command line options to actually execute analysis commands

SARADIR=$HOME/SARA

if [ ! -z $1 ]; then
  SGE_TASK_ID=1 # for debugging only
fi

# Make sure this line is set according to your job array settings
while [ $SGE_TASK_ID -le 432 ]; do
  settings=( mu01o02c50 mu01o2c50 mu01o5c50 mu5o02c50 mu5o2c50 mu5o5c50 mu9o02c50 mu9o2c50 mu9o5c50 )
  # every 48 tasks, we want to go to the next setting file and redo analysis
  taskm1=$(($SGE_TASK_ID - 1))
  setting_i=$(($taskm1 / 48))
  task_i=$(($taskm1 % 48 + 1))
  
  settings_name=${settings[$setting_i]}
  settings_file=$SARADIR/settings/${settings_name}
  outdir=$SARADIR/out/${settings_name}
  
  cmd="./run_single.py $SGE_TASK_ID ${settings_file} $outdir"
  
  if [ -z $1 ]; then
    cd $SARADIR/out
    # create a directory with the same name as the settings file
    if [ ! -d ${settings_name} ]; then
      mkdir ${settings_name}
      cd ${settings_name}
      mkdir corrected plots signals analysis
    fi
    cd $SARADIR
    # Run command here
    $cmd > $HOME/out/sara.o$SGE_TASK_ID 2>$HOME/out/sara.e$SGE_TASK_ID
    exit 0
  else
    # Debugging mode
    echo $cmd
    ((SGE_TASK_ID++))
  fi
done
