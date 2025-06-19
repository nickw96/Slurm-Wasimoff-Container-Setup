#!/bin/bash
echo "$(date -Ins)" >> /media/server/prolog_$(hostname)_$($SLURM_JOBID).txt
systemctl stop wasimoff_provider.service
systemctl disable wasimoff_provider.service
echo "$(date -Ins)" >> /media/server/prolog_$(hostname)_$($SLURM_JOBID).txt