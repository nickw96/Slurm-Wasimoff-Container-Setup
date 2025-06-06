#!/bin/sh
srun -l date -Ins
srun -l hostname
srun -l -D Slurm-Wasimoff-Container-Setup/prototype/wasi-apps/travelling_salesman ./tsp rand 13
srun -l date -Ins