from eagleeye.shodan_query import ShodanWorker
from eagleeye.nmap import NmapWorker
from eagleeye.selchrome import SeleniumWorker, WriteScreenshot

#query = raw_input('Shodan Query: ')
query = 'org:amazon port:80'
worker = ShodanWorker(blocking=False)
print worker.count(query)
worker.insert_query(query)

print "shodan worker:"
for result in worker():
    pass

print "nmap worker:"
worker = NmapWorker(blocking=False)

for result in worker():
    print result

print "selenium worker:"
worker = SeleniumWorker(blocking=False)

for result in worker():
    print type(result)

print "output writer:"
worker = WriteScreenshot(blocking=False)

for result in worker():
    print result
