#!/bin/bash
# EXECUTE ONLY IN REPO
if [ "$2" = 'first']; then
    echo "192.168.2.98       controller" >> /etc/hosts
    echo "192.168.2.97       computer" >> /etc/hosts
fi
apt install -fy unzip munge slurm-client
if [ "$1" = 'controller' ]; then
    apt install -fy slurmctld
    touch /var/slurmctld.pid
    wget -O /var/tmp/go1.23.5.linux-amd64.tar.gz https://go.dev/dl/go1.23.3.linux-amd64.tar.gz
    tar -C /usr/local -xzf /var/tmp/go1.23.5.linux-amd64.tar.gz
    cp -r prototype/broker /bin/broker/
elif [ "$1" = 'compute' ]; then
    apt install -fy slurmd
    touch /var/slurmd.pid
    wget -O /var/tmp/deno-2-1-6.zip https://github.com/denoland/deno/releases/download/v2.1.6/deno-x86_64-unknown-linux-gnu.zip
    unzip -d /bin /var/tmp/deno-2-1-6.zip
    chmod +x /bin/deno
    mkdir /bin/wasimoff_provider
    cp -r  prototype/denoprovider /bin/wasimoff_provider/denoprovider/
    cp -r  prototype/webprovider /bin/wasimoff_provider/webprovider/
fi
mkdir /run/slurm/
mkdir /var/spool/slurm
cp slurm-resources/slurm.conf /etc/slurm/slurm.conf
cp slurm-resources/cgroup.conf /etc/slurm/cgroup.conf
cp slurm-resources/prolog.sh /etc/slurm/prolog.sh
cp slurm-resources/epilog.sh /etc/slurm/epilog.sh
chown -R slurm: /etc/slurm/ /run/slurm/ /var/spool/slurm/
sudo -u slurm chmod -R 0755 /etc/slurm/ /run/slurm/ /var/spool/slurm/
# adduser \
#     -c "SLURM Workload Manager"\
#     # --home-dir /var/lib/slurm\
#     --disabled-password \
#     --gecos "" \
#     --shell "/sbin/nologin" \
#     --no-create-home \
#     --uid 100 \
#     slurm
apt-get clean
