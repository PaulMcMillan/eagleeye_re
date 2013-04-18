import os

from shodan import WebAPI

from eagleeye import RedisWorker


class ShodanWorker(RedisWorker):
    qinput = 'search:shodan'
    qoutput = 'verify'

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
        for host in res:
            yield host

    def query(self, query, page=1):
        self.write('search:shodan', [query, page])

    def count(self, query):
        return self.api.count(query)
