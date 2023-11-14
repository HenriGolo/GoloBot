#!/usr/bin/env python3
from subprocess import Popen, DEVNULL
from os import environ

with open(environ['pidfile'], 'r') as file:
    Popen(["kill", file.read()])

Popen([environ['bot_path']],
      stdin=DEVNULL,
      stdout=open(environ['stdout'], 'a'),
      stderr=open(environ['stderr'], 'a'),
      start_new_session=True,
      shell=True)
