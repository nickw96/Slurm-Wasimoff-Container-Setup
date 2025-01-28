# Slurm-Wasimoff-Container-Setup
The experimental setup

## TODO
- Add Prolog and Epilog scripts to repo
- Check compose.yaml
- Bash scripts
- Make files to non root user accessible

## HOW TO BUILD
- use tags via -t (username/restofpath:tag)
- -f "path to Dockerfile"
- build at root of this project

### Building a controller image
`docker build -t un/controller:0.0.0 --build-context repo=/home/.../Slurm-Wasimoff-Container-Setup/ controller-node/.`
`docker build -t un/compute-node:0.0.0 --build-context repo=/home/.../Slurm-Wasimoff-Container-Setup/ compute-node/.`

## HOT TO RUN CONTAINERS
- always -ti for debug purposes
- use --name