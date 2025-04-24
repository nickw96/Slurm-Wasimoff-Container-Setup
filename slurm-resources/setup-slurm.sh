#!/bin/bash
# EXECUTE ONLY IN REPO
controllerip=$3
computeraip=$4
computerbip=$5
computercip=$6
apt install -fy munge slurm-client build-essential gfortran python3 curl
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
if [ "$1" = 'controller' ]; then
    if [ "$2" = 'first' ]; then
        apt install -fy slurmctld
        touch /var/slurmctld.pid
        wget -O /var/tmp/go1.24.0.linux-amd64.tar.gz https://go.dev/dl/go1.24.0.linux-amd64.tar.gz
        tar -C /usr/local -xzf /var/tmp/go1.24.0.linux-amd64.tar.gz
        echo "export PATH=$PATH:/usr/local/go/bin" >> /etc/profile
        export PATH=$PATH:/usr/local/go/bin
    fi
    cd prototype/broker
    go build -buildvcs=false ./
    cd ../..
    cp prototype/broker/broker /bin/
    cp slurm-resources/wasimoff_broker.service /etc/systemd/system/wasimoff_broker.service
elif [ "$1" = 'compute' ]; then
    if [ "$2" = 'first' ]; then
        apt install -fy slurmd unzip
        touch /var/slurmd.pid
        mkdir /bin/wasimoff_provider
        wget -O /var/tmp/deno-2-2-11.zip https://github.com/denoland/deno/releases/download/v2.2.11/deno-x86_64-unknown-linux-gnu.zip
        unzip -d /bin /var/tmp/deno-2-2-11.zip
        chmod +x /bin/deno
    fi
    cp -r  prototype/denoprovider /bin/wasimoff_provider/denoprovider/
    cp -r  prototype/webprovider /bin/wasimoff_provider/webprovider/
    cp slurm-resources/wasimoff_provider.service /etc/systemd/system/wasimoff_provider.service
fi
systemctl daemon-reload
systemctl enable wasimoff_broker.service
if [ "$2" = 'first' ]; then
    echo "$controllerip      controller" >> /etc/hosts
    echo "$computeraip      computer-a" >> /etc/hosts
    echo "$computerbip      computer-b" >> /etc/hosts
    echo "$computercip      computer-c" >> /etc/hosts
    mkdir /run/slurm/
    mkdir /var/spool/slurm
    chown -R slurm: /etc/slurm/ /run/slurm/ /var/spool/slurm/
    sudo -u slurm chmod -R 0755 /etc/slurm/ /run/slurm/ /var/spool/slurm/
fi
if [ "$2" = 'first' ]; then
    cp slurm-resources/slurm.conf /etc/slurm/slurm.conf
    cp slurm-resources/cgroup.conf /etc/slurm/cgroup.conf
    cp slurm-resources/prolog.sh /etc/slurm/prolog.sh
    cp slurm-resources/epilog.sh /etc/slurm/epilog.sh
fi
apt-get clean