import subprocess

from itertools import cycle

from lxml import objectify

from eagleeye import RedisWorker

class NmapWorker(RedisWorker):
    qoutput = 'image:http'

    def add_job(self, hosts, port_set):
        queue = self.queue('verify:port:%s' % port_set)
        self.redis.sadd('verify:port:set', port_set)
        for host in hosts:
            queue.send(host)

    def jobs(self):
        while True:
            key_set = self.redis.smembers('verify:port:set')
            for key in key_set:
                yield key
            else:
                # don't busy loop while we wait for initial set members
                yield

    def run(self, ports):
        hosts = self.finite_queue(job)[:1000]

        for host in basic_nmap(hosts, ports):
            # XXX better output queue selection
            yield host


def basic_nmap(hosts, ports):
    command = ['nmap', '-T5', '--no-stylesheet', '-Pn', '-sT',
               '--min-rate', '500', '--host-timeout', '15s',
               '-n', # No DNS resolution
               '-oX', '-',  # output XML to stdout
               '-p', ports] + host_list
    # This could be more efficient by not waiting for nmap to finish
    # before starting XML parsing
    nmap_xml_output = subprocess.check_output(command)
    nmaprun = objectify.fromstring(nmap_xml_output)
    for host in nmaprun.host:
        for port in host.ports.port:
            if port.state.get('state') == 'open':
                yield dict(host=host.address.get('addr'),
                           port=port.get('portid'))


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


