#!/bin/bash
START=$(sed -e '1!d' $1)
STOP=$(sed -e '2!d' $1)
sudo journalctl -u $2 --since "$START" --until "$STOP" >> $3
