#!/bin/bash
export WASI_OS=linux
export WASI_ARCH=x86_64
export WASI_VERSION=25
export WASI_VERSION_FULL=${WASI_VERSION}
wget https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-${WASI_VERSION}/wasi-sdk-${WASI_VERSION_FULL}-${WASI_ARCH}-${WASI_OS}.tar.gz
tar xvf wasi-sdk-${WASI_VERSION_FULL}-${WASI_ARCH}-${WASI_OS}.tar.gz
