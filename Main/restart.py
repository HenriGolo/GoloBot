#!/usr/bin/env python3
from subprocess import Popen, DEVNULL
from infos import bot, stdout, stderr

Popen([bot],
		stdin=DEVNULL,
		stdout=open(infos.stdout, 'a'),
		stderr=open(infos.stderr, 'a'),
		start_new_session=True,
		shell=True)
