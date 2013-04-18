import subprocess

from itertools import cycle

from lxml import objectify

from eagleeye import RedisWorker

class NmapWorker(RedisWorker):
    def set_read(self, value):
        return self.redis.smembers(value)

    def jobs(self):
        while True:
            key_set = self.set_read('verify:port:set')
            for key in key_set:
                yield key

    def run(self, job):
        result = []
        for host in filter_open(job):
            self.write('image:http', host)
            result.append(host)


def filter_open(hosts):
    """ Basic quick nmap open port command. Filters a list of
    shodan-style hosts/port results to those that are open.

    This is inefficient, but n ~= 100 so it doesn't matter much.

    This checks in a batch and may scan more ports than input, but
    only returns ones from the original search. It works this way to
    take advantage of nmap's built-in parallelization.
    """
    host_list = list(set(h['ip'] for h in hosts))
    port_list = set(str(h['port']) for h in hosts)

    command = ['nmap', '-T5', '--no-stylesheet', '-Pn', '-sT',
               '--min-rate', '500', '--host-timeout', '15s',
               '-n', # No DNS resolution
               '-oX', '-',  # output XML to stdout
               '-p', ','.join(port_list)] + host_list
    nmap_xml_output = subprocess.check_output(command)
    nmaprun = objectify.fromstring(nmap_xml_output)

    checked = {}
    for host in nmaprun.host:
        for port in host.ports.port:
            state = port.state.get('state')
            checked[host.address.get('addr'), port.get('portid')] = state

    for host in hosts:
        if checked[host['ip'], str(host['port'])] == 'open':
            yield host


