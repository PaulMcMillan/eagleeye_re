#!/usr/bin/python
import sys

import netaddr

from eagleeye.raw_command import CommandWorker

SUBNET_PREFIXLEN = 24

ip = netaddr.IPNetwork(sys.argv[1])

worker = CommandWorker()

for sub in ip.subnet(SUBNET_PREFIXLEN):
    cmd = ['nmap',  '-T4',  '--open',  '-sV',  '-sT',  '-sC',
           '-A', '-O', '-n', '-Pn',  '--min-parallelism', '50',
           '--min-rate',  '100',  '-g',  '53',
           '--min-hostgroup', str(sub.prefixlen),
           '-oX', '-',
           str(sub)
           ]
    worker.qinput.send(['out/%s_%s_{timestamp}' % (sub.ip, sub.prefixlen),
                        cmd])
