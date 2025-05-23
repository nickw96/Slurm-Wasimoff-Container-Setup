#!/bin/sh
# srun -N1 -l -D ./Slurm-Wasimoff-Container-Setup/Proxels/ ./proxels -dt 0.5 -endtime 50000
srun -l hostname
srun -l date +'%Y-%m-%d %H:%M:%S'
srun -l -D Slurm-Wasimoff-Container-Setup/Proxels/ ./proxels -dt 0.5 -endtime 100000
srun -l date +'%Y-%m-%d %H:%M:%S'