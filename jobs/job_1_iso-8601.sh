#!/bin/sh
# srun -N1 -l -D ./Slurm-Wasimoff-Container-Setup/CloverLeaf_Serial cp InputDecks/clover.in clover.in
srun -l date -Ins
srun -l hostname
srun -l -D Slurm-Wasimoff-Container-Setup/CloverLeaf_Serial cp InputDecks/clover_bm4.in clover.in
srun -l -D Slurm-Wasimoff-Container-Setup/CloverLeaf_Serial ./clover_leaf
srun -l date -Ins