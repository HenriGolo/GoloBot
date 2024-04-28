#!/usr/bin/env python3
from os import environ
from subprocess import Popen, DEVNULL
from GoloBot.Auxilliaire import path

# kill ancien bot, si existant
with open(path + environ['pidfile'], 'r') as pid:
    try:
        Popen(["kill", pid.read()])
    except:
        pass
    finally:
        # lancement du bot
        Popen([path + environ['bot_path']],
              stdin=DEVNULL,
              stdout=DEVNULL,
              stderr=open(path + environ['stderr'], 'a'),
              start_new_session=True,
              shell=True)
