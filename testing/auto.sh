#!/bin/bash
# make sure, the binaries exist! Or translate it all to a py script (would be easier and keep things more module)
# setup wasimoff broker environment; upload necessary binaries
RANDOM=1

# müssen in client verzeichnis aufgerufen werden
cd Slurm-Wasimoff-Container-Setup/prototype/client
go run client.go -upload examples/tsp/tsp.wasm
go run client.go -upload ../../Proxels/proxels.wasm
cd ../..

date_of_start=$(date +"%Y-%m-%d_%H-%M-%S")
echo "Reihe gestart: $(date +"%Y-%m-%d %H-%M-%S")" >> ../log_$date_of_start.txt

# start program in background to randomly generate wasimoff tasks
python3 testing/wasimoff_automization.py &
WASI_SPAWN=$!

# sbatch -N(#Knoten) -w (für spezielle Knoten, eigentlich unwichtig) -D (Pfad zum Ausführungsverzeichnis) -o (Ausgabe falls erwünscht) script.sh
num=1
until [ $num == 21 ]; do
    i=$(($RANDOM % 3 + 1))
    j=$(($RANDOM % 3 + 1))
    sbatch -N$i -o job_$num.txt jobs/job_$j.sh
    num=$(($num + 1))
done

jobs=$(squeue -O jobid | sed -e '/^JOBID/d;s/ //g;:a;N;$!ba;s/\n/:/g;s/ //g')
srun -N3 -d afterany:$jobs echo "Reihe beendet: $(date +"%Y-%m-%d %H-%M-%S")" | sed -e '1!d' >> ../log_$date_of_start.txt
kill $WASI_SPAWN

# Hinweis: Potentiell alle Pfade absolut angeben; Anwendungen müssen auf das Netzlaufwerk kopiert werden bzw. Symlinks in /bin/ (?)