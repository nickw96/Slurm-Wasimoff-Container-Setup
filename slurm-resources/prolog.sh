#!/bin/bash
echo "$(date -Ins)" >> /home/$(echo $SLURM_JOB_USER)/prolog_$(hostname)_$(echo $SLURM_JOBID).txt
systemctl stop wasimoff_provider.service
systemctl disable wasimoff_provider.service
echo "$(date -Ins)" >> /home/$(echo $SLURM_JOB_USER)/prolog_$(hostname)_$(echo $SLURM_JOBID).txt