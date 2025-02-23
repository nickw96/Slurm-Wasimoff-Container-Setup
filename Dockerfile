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
RUN apt -fy install munge
RUN systemctl disable munge
# get munge by src
# RUN mkdir /munge-src
# RUN wget -O /munge-src/munge-0.5.16.tar.xz https://github.com/dun/munge/releases/download/munge-0.5.16/munge-0.5.16.tar.xz
# WORKDIR /munge-src
# RUN tar xJf munge-0.5.16.tar.xz
# RUN cd munge-0.5.16
# RUN ./configure \
#     --prefix=/usr \
#     --sysconfdir=/etc \
#     --localstatedir=/var \
#     --runstatedir=/run
# RUN make
# RUN make check
# RUN sudo make install
# WORKDIR /
# ARG UID=10000
# RUN adduser \
#     -c "MUNGE identifier"\
#     -d /var/lib/munge\
#     --disabled-password \
#     --gecos "" \
#     --shell "/sbin/nologin" \
#     --no-create-home \
#     --uid "${UID}" \
#     munge
# RUN chown -R munge: /etc/munge /var/lib/munge /var/log/munge /run/munge
# RUN sudo -u munge chmod -R 0755 /run/munge
# RUN sudo -u munge chmod -R 0700 /etc/munge
# RUN sudo -u munge chmod -R 0700 /var/lib/munge
# RUN sudo -u munge chmod -R 0711 /var/lib/munge
# RUN sudo -u munge /usr/sbin/mungekey --verbose
# RUN sudo -u munge chmod -R 0600 /etc/munge/munge.key
# # RUN systemctl enable munge.service
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
    -c "SLURM Workload Manager"\
    -d /var/lib/slurm\
    --disabled-password \
    --gecos "" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    slurm
# transfer ownership to slurm user
RUN chown -R slurm: /etc/slurm/ /var/run/slurm/ /var/spool/slurm/ /var/log/slurm/
RUN sudo -u slurm chmod -R 0755 /etc/slurm/ /var/run/slurm/ /var/spool/slurm/ /var/log/slurm/ /var/spool/slurm/slurmd

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
# create missing, daemon specific directories
RUN sudo -u slurm /var/spool/slurm/slurmd
# RUN systemctl enable --now slurmd
RUN rm -rf /slurm-packages
# copy startup script for slurmd
RUN echo -e '#!/bin/sh\n\
sleep 90\n\
/bin/deno run --allow-read=./ --allow-net /bin/wasimoff_provider/denoprovider/main.ts --workers 2 --url http://controller:4080' > /bin/start_compute_node.sh
# RUN echo "echo hello" > /bin/start_compute_node.sh
RUN chmod 100 /bin/start_compute_node.sh
RUN apt-get clean
# ENTRYPOINT ["/bin/start_compute_node.sh"]


FROM base AS controller
# get and setup go
RUN wget -O /var/tmp/go1.23.5.linux-amd64.tar.gz https://go.dev/dl/go1.23.3.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf /var/tmp/go1.23.5.linux-amd64.tar.gz
# copy wasimoff broker
COPY prototype/broker /bin/broker/
# setup slurm for controller node
RUN apt install -fy /slurm-packages/slurm-smd-slurmctld_24.11.1-1_amd64.deb
# create missing, daemon specific directories
RUN sudo -u slurm /var/spool/slurm/slurmctld
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
cd /bin/broker\n\
WASIMOFF_ALLOWED_ORIGINS="*" WASIMOFF_HTTP_LISTEN=controller:4080 go run ./'\
> /bin/start_controller_node.sh
RUN chmod 100 /bin/start_controller_node.sh
RUN apt-get clean
# ENTRYPOINT ["/bin/start_controller_node.sh"]