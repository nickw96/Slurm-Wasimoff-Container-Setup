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
FROM ubuntu:24.04 AS base
# get dependencies
SHELL [ "/bin/bash", "-c" ]
RUN apt update
RUN apt -fy install munge=0.5.15-4build1 wget=1.21.4-1ubuntu4 unzip=6.0-28ubuntu4 sudo iputils-ping
# RUN systemctl enable --now munge
# setup munge
RUN mkdir /run/munge ; chown -R munge: /run/munge
RUN sudo -u munge chmod -R 0755 /run/munge
# setup slurm
RUN apt-get install -y build-essential fakeroot devscripts equivs
COPY --chmod=100 slurm-resources/setup-slurm.sh /bin/setup-slurm.sh
RUN apt-get clean
# copy slurm.conf
COPY slurm-resources/slurm.conf /etc/slurm/
# create slurm directories and files
RUN mkdir /var/run/slurm
RUN mkdir /var/spool/slurm
RUN mkdir /var/log/slurm
RUN > /var/run/slurm/slurmd.pid
RUN > /var/spool/slurm/slurmd
RUN > /var/log/slurm/slurmd.log
# general slurm stuff
RUN mkdir /slurm-packages
RUN wget -O /slurm-packages/slurm-24.11.1.tar.bz2 https://download.schedmd.com/slurm/slurm-24.11.1.tar.bz2
RUN tar -C /slurm-packages -xaf /slurm-packages/slurm-24.11.1.tar.bz2
WORKDIR /slurm-packages/slurm-24.11.1
RUN mk-build-deps -i -t 'apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends --yes' debian/control
RUN debuild -b -uc -us
WORKDIR /
RUN apt install -fy /slurm-packages/slurm-smd_24.11.1-1_amd64.deb
RUN apt install -fy /slurm-packages/slurm-smd-client_24.11.1-1_amd64.deb
#create slurm user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    slurm

# transfer ownership to slurm user
RUN chown -R slurm: /etc/slurm/ /var/run/slurm/ /var/spool/slurm/ /var/log/slurm/
USER slurm
RUN chmod -R 0755 /etc/slurm/ /var/run/slurm/ /var/spool/slurm/ /var/log/slurm/ /var/spool/slurm/slurmd
USER root

FROM base AS computer
# get and setup deno
RUN wget -O /var/tmp/deno-2-1-6.zip https://github.com/denoland/deno/releases/download/v2.1.6/deno-x86_64-unknown-linux-gnu.zip
RUN unzip -d /bin /var/tmp/deno-2-1-6.zip
RUN chmod +x /bin/deno
# copy wasimoff denoprovider
COPY  prototype/denoprovider /bin/wasimoff_provider/denoprovider/
COPY  prototype/webprovider /bin/wasimoff_provider/webprovider/
# setup slurm for compute node
RUN apt install -fy /slurm-packages/slurm-smd-slurmd_24.11.1-1_amd64.deb
# RUN systemctl enable --now slurmd
RUN rm -rf /slurm-packages
# copy startup script for slurmd
# COPY --chmod=100 compute-node/start_compute_node.sh /bin/start_compute_node.sh
RUN echo -e '#!/bin/sh\n\
sudo -u munge munged &\n\
sleep 150\n\
/bin/deno run --allow-read=./ --allow-net /bin/wasimoff_provider/denoprovider/main.ts --workers 2 --url http://controller:4080' > /bin/start_compute_node.sh
# RUN echo "echo hello" > /bin/start_compute_node.sh
RUN chmod 100 /bin/start_compute_node.sh
ENTRYPOINT ["/bin/start_compute_node.sh"]


FROM base AS controller
# get and setup go
RUN wget -O /var/tmp/go1.23.5.linux-amd64.tar.gz https://go.dev/dl/go1.23.3.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf /var/tmp/go1.23.5.linux-amd64.tar.gz
# copy wasimoff broker
COPY prototype/broker /bin/broker/
# setup slurm for controller node
RUN apt install -fy /slurm-packages/slurm-smd-slurmctld_24.11.1-1_amd64.deb
# RUN systemctl enable --now slurmctld
RUN rm -rf /slurm-packages
# copy startup script for slurmd
# COPY --chmod=100 controller-node/start_controller_node.sh /bin/start_controller_node.sh
# RUN echo -e '#!/bin/sh\
# export PATH=$PATH:/usr/local/go/bin\
# munge\
# systemctl enable slurmctld\
# WASIMOFF_ALLOWED_ORIGINS="*" go run /bin/broker &' > /bin/start_controller_node.sh
RUN echo -e '#!/bin/sh\n\
export PATH=$PATH:/usr/local/go/bin \n\
sudo -u munge munged &\n\
cd /bin/broker\n\
WASIMOFF_ALLOWED_ORIGINS="*" WASIMOFF_HTTP_LISTEN=controller:4080 go run ./'\
> /bin/start_controller_node.sh
RUN chmod 100 /bin/start_controller_node.sh
ENTRYPOINT ["/bin/start_controller_node.sh"]