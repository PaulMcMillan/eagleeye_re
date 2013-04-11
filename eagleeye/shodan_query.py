import os

from shodan import WebAPI

from eagleeye import RedisWorker


class ShodanWorker(RedisWorker):
    qinput = 'search:shodan'
    qoutput = 'verify'
    # This queuing system will work, but we eventually need something
    # more complex that passes or recognizes intended protocols

    def __init__(self, shodan_api_key=None, *args, **kwargs):
        super(ShodanWorker, self).__init__(*args, **kwargs)
        if not shodan_api_key:
            # We should do more to find this key
            shodan_api_key = os.environ.get('SHODAN_API_KEY')
        if not shodan_api_key:
            raise Exception('Shodan API key required')  # FIXME
        self.api = WebAPI(shodan_api_key)

    def run(self, job):
        query, page = job
        res = self.api.search(query, page=page)['matches']
        print len(res)
        return res

    def insert_query(self, query):
        self.write('search:shodan', [query, 1])

    def count(self, query):
        return self.api.count(query)
