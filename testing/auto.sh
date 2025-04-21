#!/bin/bash
# make sure, the binaries exist! Or translate it all to a py script (would be easier and keep things more module)
# setup wasimoff broker environment; upload necessary binaries
RANDOM=1

# müssen in client verzeichnis aufgerufen werden
cd Slurm-Wasimoff-Container-Setup/prototype/client
./client -upload examples/tsp/tsp.wasm
./client -upload ../../Proxels/proxels.wasm
cd ../../..

date_of_start=$(date +"%Y-%m-%d_%H-%M-%S")
# echo "Reihe gestart: $(date +"%Y-%m-%d %H-%M-%S")" >> log_$date_of_start.txt
echo "$(date +"%Y-%m-%d %H:%M:%S")" >> server/log_$date_of_start.txt

# start program in background to randomly generate wasimoff tasks
python3 Slurm-Wasimoff-Container-Setup/testing/wasimoff_automation.py &
WASI_SPAWN=$!

# sbatch -N(#Knoten) -w (für spezielle Knoten, eigentlich unwichtig) -D (Pfad zum Ausführungsverzeichnis) -o (Ausgabe falls erwünscht) script.sh
num=1
until [ $num == 11 ]; do
    i=$(($RANDOM % 3 + 1))
    j=$(($RANDOM % 3 + 1))
    sbatch -N$i -o /media/server/job_$num.txt Slurm-Wasimoff-Container-Setup/jobs/job_$j.sh
    num=$(($num + 1))
    sleep $(($RANDOM % 5 + 1))
done

jobs=$(squeue -O jobid | sed -e '/^JOBID/d;s/ //g;:a;N;$!ba;s/\n/:/g;s/ //g')
# srun -N3 -d afterany:$jobs echo "Reihe beendet: $(date +'%Y-%m-%d %H-%M-%S')" | sed -e '1!d' >> log_$date_of_start.txt
srun -N3 -d afterany:$jobs echo "$(date +'%Y-%m-%d %H:%M:%S')" | sed -e '1!d' >> server/log_$date_of_start.txt
kill $WASI_SPAWN