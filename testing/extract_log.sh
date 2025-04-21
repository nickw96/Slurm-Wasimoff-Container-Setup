#!/bin/bash
# needs to be executed with 'sudo'
START=$(sed -e '1!d' $1)
STOP=$(sed -e '2!d' $1)
journalctl -u $2 --since $START --until $STOP >> broker_$1