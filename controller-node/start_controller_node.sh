#!/bin/sh
export PATH=$PATH:/usr/local/go/bin
munge
systemctl enable slurmctld
WASIMOFF_ALLOWED_ORIGINS="*" go run /bin/broker &