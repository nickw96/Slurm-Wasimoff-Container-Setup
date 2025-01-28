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
RUN apt update
RUN apt -fy install munge=0.5.15-4build1 wget=1.21.4-1ubuntu4
RUN wget -O /var/tmp/go1.23.5.linux-amd64.tar.gz https://go.dev/dl/go1.23.3.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf /var/tmp/go1.23.5.linux-amd64.tar.gz
RUN export PATH=$PATH:/usr/local/go/bin
# copy wasimoff broker
COPY --from=repo prototype/broker /bin/broker/
# setup slurm
RUN apt-get install -y build-essential fakeroot devscripts equivs
COPY --from=repo --chmod=100 setup-slurm.sh /bin/setup-slurm.sh
RUN /bin/setup-slurm.sh
RUN apt-get clean
# copy slurm.conf; TODO: add chown option
COPY --from=repo slurm-configuration/slurm.conf /etc/slurm/
# startup script for async start of slurmctld and wasimoff broker
COPY start_head.sh /bin/start_head.sh
RUN chmod +x /bin/start_head.sh

################################################################################
# Create a stage for building/compiling the application.
#
# The following commands will leverage the "base" stage above to generate
# a "hello world" script and make it executable, but for a real application, you
# would issue a RUN command for your application's build process to generate the
# executable. For language-specific examples, take a look at the Dockerfiles in
# the Awesome Compose repository: https://github.com/docker/awesome-compose
# FROM base as build

#RUN echo -e '#!/bin/sh\n\
#echo Hello world from $(whoami)! In order to get your application running in a container, take a look at the comments in the Dockerfile to get started.'\
#> /bin/hello.sh
#RUN chmod +x /bin/hello.sh

################################################################################
# Create a final stage for running your application.
#
# The following commands copy the output from the "build" stage above and tell
# the container runtime to execute it when the image is run. Ideally this stage
# contains the minimal runtime dependencies for the application as to produce
# the smallest image possible. This often means using a different and smaller
# image than the one used for building the application, but for illustrative
# purposes the "base" image is used here.
FROM base AS final

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
# add slurm user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    slurm
USER slurm

# Copy the executable from the "build" stage.
#COPY --from=build /bin/hello.sh /bin/
# What the container should run when it is started.
# TODO: Set entrypoint
# ENTRYPOINT [ "/bin/start_head.sh" ]
ENTRYPOINT [ "/bin/bash" ]