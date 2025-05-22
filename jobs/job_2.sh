#!/bin/sh
srun hostname
srun -N1 date +'%Y-%m-%d %H:%M:%S'
srun -l -D Slurm-Wasimoff-Container-Setup/prototype/wasi-apps/travelling_salesman ./tsp rand 13
srun -N1 date +'%Y-%m-%d %H:%M:%S'