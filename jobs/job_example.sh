#!/bin/sh
srun -l date -Ins
srun -l hostname
# execute pwd with one node and log output
srun -N1 -l pwd
# switch to directory from option -D, execute pwd with one node and log output
srun -N1 -l -D ./Slurm-Wasimoff-Container-Setup pwd
srun -l date -Ins