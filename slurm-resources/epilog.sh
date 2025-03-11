#!/bin/bash
# nohup /bin/deno run --allow-env --allow-read= --allow-net /bin/wasimoff_provider/denoprovider/main.ts --workers 2 --url http://controller:4080 &
# pid2disown=$(ps aux | grep deno | grep -v grep | awk 'print $2')
# disown $pid2disown
systemctl enable --now wasimoff_provider.service