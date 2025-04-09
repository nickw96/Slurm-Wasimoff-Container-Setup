#!/bin/bash

# setup wasimoff broker environment; upload necessary binaries

# müssen in client verzeichnis aufgerufen werden
cd Slurm-Wasimoff-Container-Setup/prototype/client
go run client.go -upload examples/tsp/tsp.wasm
go run client.go -upload ../../slurm-resources/proxel.wasm

date_of_start=$(date +"%Y-%m-%d_%H-%M-%S")
echo "Reihe gestart: $(date +"%Y-%m-%d %H-%M-%S")" >> log_$date_of_start.txt

# start program in background to randomly generate wasimoff tasks

# sbatch -N(#Knoten) -w (für spezielle Knoten, eigentlich unwichtig) -o (Ausgabe falls erwünscht) script.sh
# go run client.go -broker http://controller:4080 -exec binary-name and arguments

jobs=$(squeue -O jobid | sed -e '/^JOBID/d;s/ //g;:a;N;$!ba;s/\n/:/g;s/ //g')
srun -N3 -d afterany:$jobs date +"%Y-%m-%d %H-%M-%S" | sed -e '1!d' >> log_$date_of_start.txt

# Hinweis: Potentiell alle Pfade absolut angeben; Anwendungen müssen auf das Netzlaufwerk kopiert werden bzw. Symlinks in /bin/ (?)