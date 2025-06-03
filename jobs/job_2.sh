#!/bin/sh
srun -l date +'%Y-%m-%d %H:%M:%S'
srun -l hostname
srun -l -D Slurm-Wasimoff-Container-Setup/prototype/wasi-apps/travelling_salesman ./tsp rand 13
srun -l date +'%Y-%m-%d %H:%M:%S'