#!/bin/bash
# EXECUTE ONLY IN REPO
controllerip=$4
com0ip=$5
com1ip=$6
com2ip=$7
apt update
apt install -fy slurm-client build-essential gfortran python3 curl binaryen
if [ "$2" = 'first' ]; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
fi
if [ "$1" = 'controller' ]; then
    if [ "$2" = 'first' ]; then
        apt install -fy slurmctld
        touch /var/slurmctld.pid
        # wget -O /var/tmp/go1.24.0.linux-amd64.tar.gz https://go.dev/dl/go1.24.0.linux-amd64.tar.gz
        # tar -C /usr/local -xzf /var/tmp/go1.24.0.linux-amd64.tar.gz
        echo "export PATH=$PATH:/usr/local/go/bin" >> /etc/profile
    fi
    # export PATH=$PATH:/usr/local/go/bin
    # cd prototype/broker
    # go build -buildvcs=false ./
    # cd ../..
    # cp -f prototype/broker/broker /bin/
    cp -f slurm-resources/wasimoff_broker.service /etc/systemd/system/wasimoff_broker.service
    if [[ $3 == *"_pure"* ]]; then
        systemctl disable wasimoff_broker.service
    else
        systemctl enable wasimoff_broker.service
    fi
elif [ "$1" = 'compute' ]; then
    if [ "$2" = 'first' ]; then
        apt install -fy slurmd unzip
        touch /var/slurmd.pid
        mkdir /bin/wasimoff_provider
        wget -O /var/tmp/deno-2-2-11.zip https://github.com/denoland/deno/releases/download/v2.2.11/deno-x86_64-unknown-linux-gnu.zip
        unzip -d /bin /var/tmp/deno-2-2-11.zip
        chmod +x /bin/deno
    fi
    #cp -fr  prototype/denoprovider /bin/wasimoff_provider/denoprovider/
    #cp -fr  prototype/webprovider /bin/wasimoff_provider/webprovider/
    cp -f slurm-resources/wasimoff_provider.service /etc/systemd/system/wasimoff_provider.service
    if [[ $3 == *"_pure"* ]]; then
        systemctl disable wasimoff_provider.service
    else
        systemctl enable wasimoff_provider.service
    fi
fi
if [ "$2" = 'first' ]; then
    echo "$controllerip      controller" >> /etc/hosts
    echo "$com0ip            com0" >> /etc/hosts
    echo "$com1ip            com1" >> /etc/hosts
    echo "$com2ip            com2" >> /etc/hosts
    mkdir /run/slurm/
    mkdir /var/spool/slurm
    chown -R slurm: /etc/slurm/ /run/slurm/ /var/spool/slurm/
    sudo -u slurm chmod -R 0755 /etc/slurm/ /run/slurm/ /var/spool/slurm/
    ln -s $(pwd)/prototype /wasimoff_system
fi
case $3 in
    builtin)
        cp -f slurm-resources/slurm_builtin.conf /etc/slurm/slurm.conf
        ;;
    backfill)
        cp -f slurm-resources/slurm_backfill.conf /etc/slurm/slurm.conf
        ;;
    gang)
        cp -f slurm-resources/slurm_gang.conf /etc/slurm/slurm.conf
        ;;
    preempt)
        cp -f slurm-resources/slurm_preempt.conf /etc/slurm/slurm.conf
        ;;
    gang-preempt)
        cp -f slurm-resources/slurm_gang_preempt.conf /etc/slurm/slurm.conf
        ;;
    builtin_pure)
        cp -f slurm-resources/slurm_builtin_pure.conf /etc/slurm/slurm.conf
        ;;
    backfill_pure)
        cp -f slurm-resources/slurm_backfill_pure.conf /etc/slurm/slurm.conf
        ;;
    gang_pure)
        cp -f slurm-resources/slurm_gang_pure.conf /etc/slurm/slurm.conf
        ;;
    preempt_pure)
        cp -f slurm-resources/slurm_preempt_pure.conf /etc/slurm/slurm.conf
        ;;
    gang-preempt_pure)
        cp -f slurm-resources/slurm_gang_preempt_pure.conf /etc/slurm/slurm.conf
        ;;
esac
cp -f slurm-resources/cgroup.conf /etc/slurm/cgroup.conf
cp -f slurm-resources/prolog.sh /etc/slurm/prolog.sh
cp -f slurm-resources/epilog.sh /etc/slurm/epilog.sh
systemctl daemon-reload
apt-get clean