#!/bin/bash
# EXECUTE ONLY IN REPO
echo "\
192.168.2.105      controller\n\
192.168.2.96       compute-node\
" >> etc/hosts
mkdir /etc/slurm
cp slurm-resources/slurm.conf /etc/slurm/slurm.conf
cp slurm-resources/prolog.sh /etc/slurm/prolog.sh
cp slurm-resources/epilog.sh /etc/slurm/epilog.sh
apt install -y build-essential fakeroot devscripts equivs
mkdir slurm-packages
wget -O slurm-packages/slurm-24.11.1.tar.bz2 https://download.schedmd.com/slurm/slurm-24.11.1.tar.bz2
tar -C slurm-packages -xaf slurm-packages/slurm-24.11.1.tar.bz2
cd slurm-packages/slurm-24.11.1
mk-build-deps -i -t 'apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends --yes' debian/control
debuild -b -uc -us
cd ../..
apt install -fy /slurm-packages/slurm-smd_24.11.1-1_amd64.deb
apt install -fy /slurm-packages/slurm-smd-client_24.11.1-1_amd64.deb
if [ "$1" = 'controller' ]; then
    apt install -fy /slurm-packages/slurm-smd-slurmctld_24.11.1-1_amd64.deb
    systemctl enable --now slurmctld
    wget -O /var/tmp/go1.23.5.linux-amd64.tar.gz https://go.dev/dl/go1.23.3.linux-amd64.tar.gz
    tar -C /usr/local -xzf /var/tmp/go1.23.5.linux-amd64.tar.gz
    cp -r prototype/broker /bin/broker/
elif [ "$1" = 'compute' ]; then
    apt install -fy /slurm-packages/slurm-smd-slurmd_24.11.1-1_amd64.deb
    systemctl enable --now slurmd
    wget -O /var/tmp/deno-2-1-6.zip https://github.com/denoland/deno/releases/download/v2.1.6/deno-x86_64-unknown-linux-gnu.zip
    unzip -d /bin /var/tmp/deno-2-1-6.zip
    chmod +x /bin/deno
    cp -r  prototype/denoprovider /bin/wasimoff_provider/denoprovider/
    cp -r  prototype/webprovider /bin/wasimoff_provider/webprovider/
fi
rm -rf slurm-packages
adduser \
    -c "SLURM Workload Manager"\
    # --home-dir /var/lib/slurm\
    --disabled-password \
    --gecos "" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid 100 \
    slurm
apt-get clean
