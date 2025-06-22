# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

################################################################################
# Pick a base image to serve as the foundation for the other build stages in
# this file.
#
# For illustrative purposes, the following FROM command
# is using the alpine image (see https://hub.docker.com/_/alpine).
# By specifying the "latest" tag, it will also use whatever happens to be the
# most recent version of that image when you build your Dockerfile.
# If reproducibility is important, consider using a versioned tag
# (e.g., alpine:3.17.2) or SHA (e.g., alpine@sha256:c41ab5c992deb4fe7e5da09f67a8804a46bd0592bfdf0b1847dde0e0889d2bff).
FROM trfore/docker-debian12-systemd:latest AS base
# SHELL [ "/bin/bash", "-c" ]
# get dependencies
RUN apt update
RUN apt -fy install wget unzip iputils-ping dbus python3
# setup slurm
RUN apt install -y build-essential slurm-client
## setup munge
# get munge by apt
RUN apt -fy install munge
# copy slurm.conf
COPY slurm-resources/slurm.conf /etc/slurm/
COPY slurm-resources/cgroup.conf /etc/slurm/
COPY slurm-resources/prolog.sh /etc/slurm/
COPY slurm-resources/epilog.sh /etc/slurm/

FROM base AS computer
# get and setup deno
RUN wget -O /var/tmp/deno-2-2-11.zip https://github.com/denoland/deno/releases/download/v2.2.11/deno-x86_64-unknown-linux-gnu.zip && \
    unzip -d /bin /var/tmp/deno-2-2-11.zip && \
    chmod +x /bin/deno
# copy wasimoff denoprovider
RUN mkdir /bin/wasimoff_provider && ln -s /bin/wasimoff_provider /wasimoff_system
COPY prototype/denoprovider /bin/wasimoff_provider/denoprovider/
COPY prototype/webprovider /bin/wasimoff_provider/webprovider/
COPY slurm-resources/wasimoff_provider.service /etc/systemd/system/
# setup slurm for compute node
RUN apt install -fy slurmd
RUN touch /var/slurmd.pid
# create missing, daemon specific directories
# RUN sudo -u slurm mkdir /var/spool/slurm/slurmd
# RUN systemctl enable slurmd
# copy startup script for slurmd
# chmod 100 /bin/start_compute_node.sh
RUN apt-get clean
# ENTRYPOINT ["/bin/start_compute_node.sh"]


FROM base AS controller
# copy wasimoff broker
COPY slurm-resources/wasimoff_broker.service /etc/systemd/system/
COPY prototype/broker/broker /usr/bin/broker/
# setup slurm for controller node
RUN apt install -fy slurmctld
RUN touch /var/slurmctld.pid
# copy programs and files for slurm execution to NON root directory
COPY Proxels/proxels /bin/
COPY prototype/wasi-apps/travelling_salesman/tsp /bin/
COPY CloverLeaf_Serial/clover_leaf /bin/
COPY CloverLeaf_Serial/InputDecks/clover_bm.in /bin/
COPY CloverLeaf_Serial/InputDecks/clover_bm2.in /bin/
COPY CloverLeaf_Serial/InputDecks/clover_bm4.in /bin/
RUN apt-get clean
# ENTRYPOINT ["/bin/start_controller_node.sh"]