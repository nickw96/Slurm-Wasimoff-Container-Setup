#!/bin/bash
echo "$(date -Ins)" >> /media/server/epilog_$(hostname)_$($SLURM_JOBID).txt
# get node number
host=$(hostname | sed -e 's/com//')
# avoid problems with history expansion character
delete='!d'
# check, if there is a suspended job on this node
job=$(squeue -O statecompact,nodelist | sed -e "/^S /$delete")
python3 /etc/slurm/check_alloc_node.py $host $job
echo "$(date -Ins)" >> /media/server/epilog_$(hostname)_$($SLURM_JOBID).txt