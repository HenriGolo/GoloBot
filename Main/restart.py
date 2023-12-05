#!/usr/bin/env python3
from os import environ
from subprocess import Popen, DEVNULL

# kill ancien bot, si existant
with open(environ['pidfile'], 'r') as pid:
    try:
        Popen(["kill", pid.read()])
    finally:
        # lancement du bot
        Popen([environ['bot_path']],
              stdin=DEVNULL,
              stdout=DEVNULL,
              stderr=open(environ['stderr'], 'a'),
              start_new_session=True,
              shell=True)
