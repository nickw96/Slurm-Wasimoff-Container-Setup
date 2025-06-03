#!/bin/sh
# srun -N1 -l -D ./Slurm-Wasimoff-Container-Setup/CloverLeaf_Serial cp InputDecks/clover.in clover.in
srun -l date +'%Y-%m-%d %H:%M:%S'
srun -l hostname
srun -l -D Slurm-Wasimoff-Container-Setup/CloverLeaf_Serial cp InputDecks/clover_bm4.in clover.in
srun -l -D Slurm-Wasimoff-Container-Setup/CloverLeaf_Serial ./clover_leaf
srun -l date +'%Y-%m-%d %H:%M:%S'