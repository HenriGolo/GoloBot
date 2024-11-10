#!/bin/bash

cd $(dirname $0)/..

# kill l'ancien bot
kill $(cat $pidfile)

# (re)lancer le bot
Main/main.py </dev/null 1>/dev/null 2>&stderr

