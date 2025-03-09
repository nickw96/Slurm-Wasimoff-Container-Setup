#!/bin/bash
# create neccessary directories with correct ownership
# mkdir /run/munge
# chown -R munge: /run/munge
# sudo -u munge chmod -R 0755 /run/munge
# mkdir /var/run/slurm
# mkdir /var/spool/slurm
# mkdir /var/log/slurm
# > /var/run/slurm/slurmctld.pid
# > /var/spool/slurm/slurmctld
# > /var/log/slurm/slurmctld.log
# chown -R slurm: /etc/slurm/ /var/run/slurm/ /var/spool/slurm/ /var/log/slurm/
# sudo -u slurm chmod -R 0755 /etc/slurm/ /var/run/slurm/ /var/spool/slurm/ /var/log/slurm/ /var/spool/slurm/slurmctld
# sudo -u munge /usr/sbin/munged &
# sleep 10
# slurmctld &
# export PATH=$PATH:/usr/local/go/bin
cd /bin/broker
# get the ipv4 address of controller
WASIMOFF_ALLOWED_ORIGINS="*" WASIMOFF_HTTP_LISTEN=$(getent ahostsv4 controller | grep STREAM | sed -n '2p' | awk '{print $1}'):4080 go run ./