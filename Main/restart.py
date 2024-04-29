#!/usr/bin/env python3
from os import environ
from subprocess import Popen, DEVNULL
from GoloBot.Auxilliaire import GBpath

# kill ancien bot, si existant
with open(GBpath + environ['pidfile'], 'r') as pid:
    try:
        Popen(["kill", pid.read()])
    except:
        pass
    finally:
        # lancement du bot
        Popen([GBpath + environ['bot_path']],
              stdin=DEVNULL,
              stdout=DEVNULL,
              stderr=open(GBpath + environ['stderr'], 'a'),
              start_new_session=True,
              shell=True)
