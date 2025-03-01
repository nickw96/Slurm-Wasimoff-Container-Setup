#!/bin/bash
mkdir /run/munge 
chown -R munge: /run/munge 
sudo -u munge chmod -R 0755 /run/munge
mkdir /var/run/slurm 
mkdir /var/spool/slurm 
mkdir /var/log/slurm 
> /var/run/slurm/slurmd.pid 
> /var/spool/slurm/slurmd 
> /var/log/slurm/slurmd.log
chown -R slurm: /etc/slurm/ /var/run/slurm/ /var/spool/slurm/ /var/log/slurm/ 
sudo -u slurm chmod -R 0755 /etc/slurm/ /var/run/slurm/ /var/spool/slurm/ /var/log/slurm/ /var/spool/slurm/slurmd
sudo -u munge /usr/sbin/munged &
sleep 10
slurmd &
# sleep 60\n\
# /bin/deno run --allow-read=./ --allow-net /bin/wasimoff_provider/denoprovider/main.ts --workers 2 --url http://controller:4080'\