#!/bin/sh
# srun -N1 -l -D ./Slurm-Wasimoff-Container-Setup/CloverLeaf_Serial cp InputDecks/clover.in clover.in
srun -N1 date +'%Y-%m-%d %H:%M:%S'
srun -l -D Slurm-Wasimoff-Container-Setup/CloverLeaf_Serial cp -f InputDecks/clover_bm8.in clover.in
srun -l -D Slurm-Wasimoff-Container-Setup/CloverLeaf_Serial ./clover_leaf
srun -N1 date +'%Y-%m-%d %H:%M:%S'