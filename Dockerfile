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
# add docker.io if using podman-compose
FROM docker.io/trfore/docker-debian12-systemd:latest AS base
# SHELL [ "/bin/bash", "-c" ]
# get dependencies
RUN apt update
RUN apt -fy install wget unzip iputils-ping dbus python3
# setup slurm
RUN apt install -y build-essential slurm-client
## setup munge
# get munge by apt
RUN apt -fy install munge
RUN mkdir /var/run/slurm && \
    mkdir /var/spool/slurm && \
    mkdir /var/log/slurm
# copy slurm.conf | adapt to config
COPY slurm-resources/slurm_gang.conf /etc/slurm/slurm.conf
COPY slurm-resources/cgroup.conf /etc/slurm/
COPY slurm-resources/check_alloc_node.py /etc/slurm/check_alloc_node.py
COPY slurm-resources/prolog.sh /etc/slurm/
COPY slurm-resources/epilog.sh /etc/slurm/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home /home/controller \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    controller
    #--no-create-home \

FROM base AS computer
# get and setup deno
RUN wget -O /var/tmp/deno-2-2-11.zip https://github.com/denoland/deno/releases/download/v2.2.11/deno-x86_64-unknown-linux-gnu.zip && \
    unzip -d /bin /var/tmp/deno-2-2-11.zip && \
    chmod +x /bin/deno
# copy wasimoff denoprovider
RUN mkdir /bin/wasimoff_provider && ln -s /bin/wasimoff_provider /wasimoff_system
COPY prototype/denoprovider /bin/wasimoff_provider/denoprovider/
COPY prototype/webprovider /bin/wasimoff_provider/webprovider/
COPY slurm-resources/wasimoff_provider_container.service /etc/systemd/system/wasimoff_provider.service
RUN systemctl enable wasimoff_provider.service
# setup slurm for compute node
RUN apt install -fy slurmd
RUN touch /var/slurmd.pid && \
    > /var/spool/slurm/slurmd && \
    > /var/log/slurm/slurmd.log
RUN chown -R slurm: /etc/slurm/ /var/run/slurm/ /var/spool/slurm/ /var/log/slurm/ && \
    sudo -u slurm chmod -R 0755 /etc/slurm/ /var/run/slurm/ /var/spool/slurm/ /var/log/slurm/ /var/spool/slurm/slurmd
# RUN sudo -u slurm mkdir /var/spool/slurm/slurmd
# RUN systemctl enable slurmd
# copy startup script for slurmd
# chmod 100 /bin/start_compute_node.sh
RUN apt-get clean
# ENTRYPOINT ["/bin/start_compute_node.sh"]


FROM base AS controller
# copy wasimoff broker
COPY slurm-resources/wasimoff_broker.service /etc/systemd/system/
RUN systemctl enable wasimoff_broker.service
COPY prototype/broker/broker /usr/bin/wasimoff_system/broker/
RUN ln -s /usr/bin/wasimoff_system/ /wasimoff_system
# setup slurm for controller node
RUN apt install -fy slurmctld
RUN touch /var/slurmctld.pid && \
    > /var/spool/slurm/slurmctld && \
    > /var/log/slurm/slurmctld.log
RUN chown -R slurm: /etc/slurm/ /var/run/slurm/ /var/spool/slurm/ /var/log/slurm/ && \
    sudo -u slurm chmod -R 0755 /etc/slurm/ /var/run/slurm/ /var/spool/slurm/ /var/log/slurm/ /var/spool/slurm/slurmctld
# copy programs and files for slurm execution to NON root directory
COPY Proxels/proxels /bin/
COPY prototype/wasi-apps/travelling_salesman/tsp /bin/
COPY CloverLeaf_Serial/clover_leaf /bin/
COPY CloverLeaf_Serial/InputDecks/clover_bm.in /bin/
COPY CloverLeaf_Serial/InputDecks/clover_bm2.in /bin/
COPY CloverLeaf_Serial/InputDecks/clover_bm4.in /bin/
RUN apt-get clean
# ENTRYPOINT ["/bin/start_controller_node.sh"]