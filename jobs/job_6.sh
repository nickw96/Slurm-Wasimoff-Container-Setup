#!/bin/sh
srun -N1 date +'%Y-%m-%d %H:%M:%S'
srun -l -D Slurm-Wasimoff-Container-Setup/prototype/wasi-apps/travelling_salesman ./tsp rand 14
srun -N1 date +'%Y-%m-%d %H:%M:%S'