import itertools

from eagleeye.shodan_query import ShodanWorker
from eagleeye.nmap import NmapWorker
from eagleeye.selchrome import SeleniumWorker, WriteScreenshot

#query = raw_input('Shodan Query: ')
query = 'org:amazon port:80'
worker = ShodanWorker()
print worker.count(query)
worker.query(query)

print "shodan worker:"
for result in itertools.takewhile(bool, worker()):
    print result

print "nmap worker:"
worker = NmapWorker()

for result in itertools.takewhile(bool, worker()):
    print 'nmap result: ', result

print "selenium worker:"
worker = SeleniumWorker(blocking=False)

for result in worker():
    print type(result)

print "output writer:"
worker = WriteScreenshot(blocking=False)

for result in worker():
    print result
