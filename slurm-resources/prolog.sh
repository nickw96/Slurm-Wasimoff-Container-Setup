#!/bin/bash
# based on https://stackoverflow.com/questions/17440585/how-to-get-pid-of-process-by-specifying-process-name-and-store-it-in-a-variable
# ps axf | grep deno | grep -v grep | awk '{print "kill " $1}' | sh
systemctl stop wasimoff_provider.service
systemctl disable wasimoff_provider.service