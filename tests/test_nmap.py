import socket

from eagleeye import nmap
from eagleeye import RedisWorker

def test_nmap():
    worker = nmap.NmapWorker(blocking=False)
    worker.write('verify', [dict(ip=socket.gethostbyname('google.com'),
                                 port=80),
                            dict(ip='1.2.3.4', port=443)])
    for result in worker():
        print 'NMAP: ', result
