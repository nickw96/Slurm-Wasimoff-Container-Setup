#!/bin/sh
munge
systemctl enable slurmd
/bin/deno run --allow-read=./ --allow-net /bin/denoprovider/main.ts --workers 2