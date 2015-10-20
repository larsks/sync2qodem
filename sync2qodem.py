#!/usr/bin/python

# sync2qodem
# by Lars Kellogg-Stedman <lars@oddbit.com>
# Distributed under the terms of the Creative Comments CC0 1.0 Universal 
# license (http://creativecommons.org/publicdomain/zero/1.0/).

import os
import sys
import argparse
import logging
import six
import six.moves.configparser as configparser
import jinja2

LOG = logging.getLogger(__name__)

qodem_entry = (
'''
[entry]
name={{name}}
address={{address}}
port={{port}}
username=
password=
tagged=false
doorway=config
method={{connectiontype|upper}}
emulation=ANSI
codepage=CP437
quicklearn=false
use_modem_cfg=true
baud=115200
data_bits=8
parity=none
stop_bits=1
xonxoff=false
rtscts=true
lock_dte_baud=true
times_on=0
use_default_toggles=true
toggles=0
last_call=0
script_filename=
capture_filename=
keybindings_filename=

''')


class SyncReader(object):
    def __init__(self, fd):
        self.fd = fd

    def __iter__(self):
        cur_data = {}

        for line in self.fd:
            line = line.decode('cp437').strip()

            if line.startswith('['):
                if 'name' in cur_data:
                    yield cur_data

                name = line[1:-1]
                cur_data = {'name': name}
            elif '=' in line:
                k, v = line.split('=', 1)
                cur_data[k.strip().lower()] = v.strip()

class QodemWriter(object):
    def __init__(self, fd):
        self.fd = fd
        self.template = jinja2.Template(qodem_entry)

    def write(self, entry):
        if ':' in entry['address']:
            entry['address'], entry['port'] = entry['address'].split(':')

        self.fd.write(self.template.render(**entry).encode('utf8'))


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--verbose', '-v',
                   action='store_const',
                   const='INFO',
                   dest='loglevel')
    p.add_argument('--debug', '-d',
                   action='store_const',
                   const='DEBUG',
                   dest='loglevel')

    p.add_argument('--output', '-o')

    p.add_argument('input')

    p.set_defaults(loglevel='WARN')
    return p.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        level=args.loglevel)

    with open(args.input) as fdin, (
          open(args.output, 'w') if args.output else sys.stdout) as fdout:
        sync = SyncReader(fdin)
        qodem = QodemWriter(fdout)
        for entry in sync:
            qodem.write(entry)

if __name__ == '__main__':
    main()
