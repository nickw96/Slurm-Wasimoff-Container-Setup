#!/bin/bash
# make sure, the binaries exist! Or translate it all to a py script (would be easier and keep things more module)
# setup wasimoff broker environment; upload necessary binaries
RANDOM=1

# muessen in client verzeichnis aufgerufen werden
cd Slurm-Wasimoff-Container-Setup/prototype/client
./client -upload examples/tsp/tsp.wasm
cd ../../..

# start program in background to randomly generate wasimoff tasks
python3 Slurm-Wasimoff-Container-Setup/testing/wasimoff_automation_ex2.py &
WASI_SPAWN=$!

date_of_start=$(date +"%Y-%m-%d_%H-%M-%S")
echo "$(date -Ins)" >> server/log_$date_of_start.txt

# sbatch -N(#nodes) -w (specific nodes) -D (path to working dir) -o (output if desired) script.sh
sbatch -N3 -o /media/server/job_sleep.txt Slurm-Wasimoff-Container-Setup/jobs/job_sleep.sh
sbatch -N2 -o /media/server/job_1.txt Slurm-Wasimoff-Container-Setup/jobs/job_1.sh

# Delete lines starting with JOBID;concatenate all lines (a is label for a goto), continue loop until last line ($);replace all newlines with ':';remove all whitespaces
jobs=$(squeue -O jobid | sed -e '/^JOBID/d;:a;N;$!ba;s/\n/:/g;s/ //g')
# get end of observation
srun -N3 -d afterany:$jobs date -Ins | sed -e '1!d' >> server/log_$date_of_start.txt
kill $WASI_SPAWN