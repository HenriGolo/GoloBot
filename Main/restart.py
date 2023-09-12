#!/usr/bin/env python3
from subprocess import Popen, DEVNULL
from infos import bot, stdout, stderr

Popen([bot],
		stdin=DEVNULL,
		stdout=open(stdout, 'a'),
		stderr=open(stderr, 'a'),
		start_new_session=True,
		shell=True)
