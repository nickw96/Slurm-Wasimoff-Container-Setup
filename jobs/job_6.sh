#!/bin/sh
srun -l hostname
srun -l date +'%Y-%m-%d %H:%M:%S'
srun -l -D Slurm-Wasimoff-Container-Setup/prototype/wasi-apps/travelling_salesman ./tsp rand 14
srun -l date +'%Y-%m-%d %H:%M:%S'