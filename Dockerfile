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
FROM trfore/docker-ubuntu2404-systemd:latest AS base
SHELL [ "/bin/bash", "-c" ]
# get dependencies
RUN apt update
RUN apt -fy install wget unzip iputils-ping dbus
# setup slurm
RUN apt-get install -y build-essential fakeroot devscripts equivs
## setup munge
# get munge by apt
RUN apt -fy install munge && \
    systemctl disable munge && \
    mkdir /run/munge && \
    chown munge: /run/munge && \
    sudo -u munge chmod 0755 /run/munge
# get munge by src
# RUN mkdir /munge-src && \
# wget -O /munge-src/munge-0.5.16.tar.xz https://github.com/dun/munge/releases/download/munge-0.5.16/munge-0.5.16.tar.xz
# WORKDIR /munge-src
# RUN tar xJf munge-0.5.16.tar.xz && \
#   cd munge-0.5.16 && \
#   ./configure \
#     --prefix=/usr \
#     --sysconfdir=/etc \
#     --localstatedir=/var \
#     --runstatedir=/run && \
#   make && \
#   make check && \
#   sudo make install
# WORKDIR /
# ARG UID=10000
# RUN adduser \
#     -c "MUNGE identifier"\
#     #--home-dir /var/lib/munge\
#     --disabled-password \
#     --gecos "" \
#     --shell "/sbin/nologin" \
#     --no-create-home \
#     --uid "${UID}" \
#     munge
# RUN chown munge: /etc/munge /var/lib/munge /var/log/munge /run/munge && \
# sudo -u munge chmod 0755 /run/munge && \
# sudo -u munge chmod 0700 /etc/munge && \
# sudo -u munge chmod 0700 /var/lib/munge && \
# sudo -u munge chmod 0711 /var/lib/munge && \
# sudo -u munge /usr/sbin/mungekey --verbose && \
# sudo -u munge chmod 0600 /etc/munge/munge.key \
# # RUN systemctl enable munge.service
# copy slurm.conf
COPY slurm-resources/slurm.conf /etc/slurm/
# create slurm directories and files
RUN mkdir /var/run/slurm && \
    mkdir /var/spool/slurm && \
    mkdir /var/log/slurm && \
    > /var/run/slurm/slurmd.pid && \
    > /var/spool/slurm/slurmd && \
    > /var/log/slurm/slurmd.log
# general slurm stuff
RUN mkdir /slurm-packages && \
    wget -O /slurm-packages/slurm-24.11.1.tar.bz2 https://download.schedmd.com/slurm/slurm-24.11.1.tar.bz2 && \
    tar -C /slurm-packages -xaf /slurm-packages/slurm-24.11.1.tar.bz2
WORKDIR /slurm-packages/slurm-24.11.1
RUN mk-build-deps -i -t 'apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends --yes' debian/control && \
    debuild -b -uc -us
WORKDIR /
RUN apt install -fy /slurm-packages/slurm-smd_24.11.1-1_amd64.deb /slurm-packages/slurm-smd-client_24.11.1-1_amd64.deb
#create slurm user
ARG UID=10001
RUN adduser \
    -c "SLURM Workload Manager"\
    # --home-dir /var/lib/slurm\
    --disabled-password \
    --gecos "" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    slurm
# transfer ownership to slurm user
RUN chown -R slurm: /etc/slurm/ /var/run/slurm/ /var/spool/slurm/ /var/log/slurm/ && \
    sudo -u slurm chmod -R 0755 /etc/slurm/ /var/run/slurm/ /var/spool/slurm/ /var/log/slurm/ /var/spool/slurm/slurmd

FROM base AS computer
# get and setup deno
RUN wget -O /var/tmp/deno-2-1-6.zip https://github.com/denoland/deno/releases/download/v2.1.6/deno-x86_64-unknown-linux-gnu.zip && \
    unzip -d /bin /var/tmp/deno-2-1-6.zip && \
    chmod +x /bin/deno
# copy wasimoff denoprovider
COPY  prototype/denoprovider /bin/wasimoff_provider/denoprovider/
COPY  prototype/webprovider /bin/wasimoff_provider/webprovider/
# setup slurm for compute node
RUN apt install -fy /slurm-packages/slurm-smd-slurmd_24.11.1-1_amd64.deb
# create missing, daemon specific directories
# RUN sudo -u slurm mkdir /var/spool/slurm/slurmd
# RUN systemctl enable slurmd
RUN rm -rf /slurm-packages
# copy startup script for slurmd
RUN echo -e '#!/bin/sh\n\
sleep 90\n\
/bin/deno run --allow-read=./ --allow-net /bin/wasimoff_provider/denoprovider/main.ts --workers 2 --url http://controller:4080' > /bin/start_compute_node.sh && \
    chmod 100 /bin/start_compute_node.sh
RUN apt-get clean
# ENTRYPOINT ["/bin/start_compute_node.sh"]


FROM base AS controller
# get and setup go
RUN wget -O /var/tmp/go1.23.5.linux-amd64.tar.gz https://go.dev/dl/go1.23.3.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf /var/tmp/go1.23.5.linux-amd64.tar.gz
# copy wasimoff broker
COPY prototype/broker /bin/broker/
# setup slurm for controller node
RUN apt install -fy /slurm-packages/slurm-smd-slurmctld_24.11.1-1_amd64.deb
# create missing, daemon specific directories
# RUN sudo -u slurm mkdir /var/spool/slurm/slurmctld
# RUN systemctl enable slurmctld
RUN rm -rf /slurm-packages
# copy startup script for slurmd
RUN echo -e '#!/bin/sh\n\
export PATH=$PATH:/usr/local/go/bin \n\
cd /bin/broker\n\
WASIMOFF_ALLOWED_ORIGINS="*" WASIMOFF_HTTP_LISTEN=controller:4080 go run ./'\
> /bin/start_controller_node.sh && \
    chmod 100 /bin/start_controller_node.sh
RUN apt-get clean
# ENTRYPOINT ["/bin/start_controller_node.sh"]