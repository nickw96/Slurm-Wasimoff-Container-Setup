#!/bin/bash
# get node number
host=$(hostname | sed -e 's/com//')
# avoid problems with history expansion character
delete='!d'
# check, if there is a suspended job on this node
job=$(squeue -O statecompact,nodelist | sed -e "/^S /$delete;/com.*$host/$delete")
if [ $job != '' ]; then
    systemctl enable --now wasimoff_provider.service
fi