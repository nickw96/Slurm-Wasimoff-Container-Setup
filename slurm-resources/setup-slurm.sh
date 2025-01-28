mkdir /slurm-packages
wget -O /slurm-packages/slurm-24.11.1.tar.bz2 https://download.schedmd.com/slurm/slurm-24.11.1.tar.bz2
tar -C /slurm-packages -xaf /slurm-packages/slurm-24.11.1.tar.bz2
cd /slurm-packages/slurm-24.11.1
mk-build-deps -i -t 'apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends --yes' debian/control
debuild -b -uc -us
cd ../..
apt install -fy /slurm-packages/slurm-smd_24.11.1-1_amd64.deb
apt install -fy /slurm-packages/slurm-smd-client_24.11.1-1_amd64.deb
if [$1 = 'controller']; then
    apt install -fy /slurm-packages/slurm-smd-slurmctld_24.11.1-1_amd64.deb
elif [$1 = 'compute']; then
    apt install -fy /slurm-packages/slurm-smd-slurmd_24.11.1-1_amd64.deb
fi
rm -rf /slurm-packages