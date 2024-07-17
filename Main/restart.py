#!/usr/bin/env python3
import os
import subprocess
from GoloBot.Auxilliaire import GBpath

# kill ancien bot, si existant
with open(GBpath + os.environ['pidfile'], 'r') as pid, open(GBpath + os.environ['stderr'], 'a') as stderr:
    subprocess.Popen(f'kill {pid.read()}', shell=True, stderr=subprocess.DEVNULL)
    # lancement du bot
    subprocess.Popen([GBpath + os.environ['bot_path']],
                     stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL,
                     stderr=stderr,
                     start_new_session=True,
                     shell=True)
