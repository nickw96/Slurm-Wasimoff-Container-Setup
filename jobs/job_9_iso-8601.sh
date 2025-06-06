#!/bin/sh
# srun -N1 -l -D ./Slurm-Wasimoff-Container-Setup/Proxels/ ./proxels -dt 0.5 -endtime 50000
srun -l date -Ins
srun -l hostname
srun -l -D Slurm-Wasimoff-Container-Setup/Proxels/ ./proxels -dt 0.1 -endtime 100000
srun -l date -Ins