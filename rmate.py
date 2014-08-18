#!/usr/bin/env python

import socket
import argparse

import os.path
from tempfile import NamedTemporaryFile
from os import remove
from shutil import copy

hostname = socket.gethostname()

host = 'localhost'
port = 52698

parser = argparse.ArgumentParser(
	description='this is a python script implementing remote textmate functionality')
parser.add_argument('file', type=argparse.FileType('r'))

args = parser.parse_args()

realpath = os.path.realpath(args.file.name)
displayname = ':'.join((hostname,args.file.name))

c = socket.create_connection((host, port))
s = c.makefile()

print s.readline(), # server_info

s.write('open\n')
s.write('display-name: {}\n'.format(displayname))
s.write('real-path: {}\n'.format(realpath))
s.write('data-on-save: yes\n')
s.write('re-activate: yes\n')
s.write('token: {}\n'.format(args.file.name))
s.flush()

s.write('data: {}\n'.format(os.path.getsize(realpath)))
s.write(args.file.read()) # send file across socket
args.file.close()
s.flush()

s.write('\n')
s.write('.\n')
s.flush()

while 1:
	line = s.readline()

	cmd = line.strip()

	token = ''
	tmp = None

	while 1:
		line = s.readline()

		line = line.strip()

		if not line:
			break

		name, value = line.split(': ')

		if name == 'token':
			token = value
		elif name == 'data':
			tmp = NamedTemporaryFile(delete=False)

			tmp.write(s.read(int(value))) # read value bytes into tmp

			tmp.close()

	if cmd == 'close':
		print 'closing', token
		break
	elif cmd == 'save':
		print 'saving', token

		copy(tmp.name, token)
		remove(tmp.name)

s.close()
c.close()