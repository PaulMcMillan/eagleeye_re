from eagleeye.shodan_query import ShodanWorker


query = raw_input('Shodan Query: ')
worker = ShodanWorker(blocking=False)
print worker.count(query)
worker.insert_query(query)

for result in worker():
    pass
