# Slurm-Wasimoff-Container-Setup
The experimental setup

## TODO
1. Test current setup
2. Figure out server utilization measurement
3. Check if current vm setup can be translated to container setup

## HOW TO BUILD
- use tags via -t (username/restofpath:tag)
- -f "path to Dockerfile"
- build at root of this project

### Building a controller image
`docker build -t un/controller:0.0.0 --build-context repo=/home/.../Slurm-Wasimoff-Container-Setup/ controller-node/.`
`docker build -t un/compute-node:0.0.0 --build-context repo=/home/.../Slurm-Wasimoff-Container-Setup/ compute-node/.`

## HOT TO RUN/CREATE CONTAINERS
- always -ti for debug purposes
- use --name with (controller-*) and (compute-node-*)
- -h or --hostname string, for host name (import for /etc/)

## SETUP VMs
- Create VMs via VM tool, e.g. *virtualbox* or *vmware*
- Get git on nodes and setup ssh for git
- Run setup-slurm.sh with arguments `sudo setup-slurm.sh <controller|compute> <first|> <builtin|backfill|gang|preempt> <controller-ip> <controller-ip> <com0-ip> <com1-ip> <com2-ip>`