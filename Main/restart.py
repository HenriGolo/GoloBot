#!/usr/bin/env python3
from os import environ
from subprocess import Popen, DEVNULL

with open(environ['pidfile'], 'r') as file:
      try:
            Popen(["kill", file.read()])
      finally:
            Popen([environ['bot_path']],
                  stdin=DEVNULL,
                  stdout=open(environ['stdout'], 'a'),
                  stderr=open(environ['stderr'], 'a'),
                  start_new_session=True,
                  shell=True)
