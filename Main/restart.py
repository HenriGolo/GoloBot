#!/usr/bin/env python3
import secrets
import subprocess
from GoloBot.Auxilliaire import GBpath

# kill ancien bot, si existant
with open(secrets.pidfile, 'r') as pid, open(secrets.stderr, 'a') as stderr:
    subprocess.Popen(f'kill {pid.read()}', shell=True, stderr=subprocess.DEVNULL)
    # lancement du bot
    subprocess.Popen([secrets.bot_path],
                     stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL,
                     stderr=stderr,
                     start_new_session=True,
                     shell=True)
