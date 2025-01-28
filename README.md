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

e.g. docker build -t jondoe/head_node:test1 -f head-node/Dockerfile .
alternative: docker build -t jondoe/head_node:test1 --build-context repo=/home/jondoe/.../Slurm-Wasimoff-Container-Setup .

## HOT TO RUN CONTAINERS
- always -ti for debug purposes
- use --name