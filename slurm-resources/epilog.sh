#!/bin/bash
echo "$(date -Ins)" >> /home/$(echo $SLURM_JOB_USER)/epilog_$(hostname)_$(echo $SLURM_JOBID).txt
# get node number
host=$(hostname | sed -e 's/com//')
# avoid problems with history expansion character
delete='!d'
# check, if there is a suspended job on this node
job=$(squeue -O statecompact,nodelist | sed -e "/^S /$delete")
python3 /etc/slurm/check_alloc_node.py $host $job
echo "$(date -Ins)" >> /home/$(echo $SLURM_JOB_USER)/epilog_$(hostname)_$(echo $SLURM_JOBID).txt