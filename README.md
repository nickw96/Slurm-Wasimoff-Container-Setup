# Slurm-Wasimoff-Container-Setup
The experimental setup

## TODO
1. Create /etc/hosts file; Add defined nodes
2. Add Prolog and Epilog scripts to repo
3. Check compose.yaml
4. Bash scripts
5. Make important files to non root user accessible

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