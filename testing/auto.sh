#!/bin/bash
# make sure, the binaries exist! Or translate it all to a py script (would be easier and keep things more module)
# setup wasimoff broker environment; upload necessary binaries
RANDOM=1

# müssen in client verzeichnis aufgerufen werden
cd Slurm-Wasimoff-Container-Setup/prototype/client
./client -upload examples/tsp/tsp.wasm
./client -upload ../../Proxels/proxels.wasm
cd ../../..

# start program in background to randomly generate wasimoff tasks
python3 Slurm-Wasimoff-Container-Setup/testing/wasimoff_automation.py &
WASI_SPAWN=$!

date_of_start=$(date +"%Y-%m-%d_%H-%M-%S")
echo "$(date +"%Y-%m-%d %H:%M:%S")" >> server/log_$date_of_start.txt

# sbatch -N(#nodes) -w (specific nodes) -D (path to working dir) -o (output if desired) script.sh
num=1
until [ $num = 51 ]; do
    i=$(($RANDOM % 3 + 1))
    j=$(($RANDOM % 9 + 1))
    if [ "$1" = 'preempt' ]; then
        k=$(($RANDOM % 2))
        if [ k > 0 ]; then
            sbatch -N$i -p highPrio -o /media/server/job_$num.txt Slurm-Wasimoff-Container-Setup/jobs/job_$j.sh
        else
            sbatch -N$i -o /media/server/job_$num.txt Slurm-Wasimoff-Container-Setup/jobs/job_$j.sh
        fi
    else
        sbatch -N$i -o /media/server/job_$num.txt Slurm-Wasimoff-Container-Setup/jobs/job_$j.sh
    fi
    num=$(($num + 1))
    sleep $(($RANDOM % 5 + 1))
done
# Delete lines starting with JOBID;concatenate all lines (a is label for a goto), continue loop until last line ($);replace all newlines with ':';remove all whitespaces
jobs=$(squeue -O jobid | sed -e '/^JOBID/d;:a;N;$!ba;s/\n/:/g;s/ //g')
# get end of observation
srun -N3 -d afterany:$jobs date +'%Y-%m-%d %H:%M:%S' | sed -e '1!d' >> server/log_$date_of_start.txt
kill $WASI_SPAWN