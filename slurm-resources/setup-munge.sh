#!/bin/bash
mkdir /munge-setup
wget -O /munge-setup/munge-0.5.16.tar.xz https://github.com/dun/munge/releases/download/munge-0.5.16/munge-0.5.16.tar.xz
tar -C /munge-setup -xJf munge-0.5.16.tar.xz
cd munge-0.5.16
./configure \
    --prefix=/usr \
    --sysconfdir=/etc \
    --localstatedir=/var \
    --runstatedir=/run
make
make check
make install
rm -rf /munge-setup