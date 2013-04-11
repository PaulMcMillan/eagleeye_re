from shodan import WebAPI

from eagleeye import RedisWorker


class ShodanWorker(RedisWorker):
    qinput = 'search:shodan'
    qoutput = 'verify'
    # This queuing system will work, but we eventually need
    # something more complex that passes intended protocols

    def __init__(self, shodan_api_key=None):
        if not shodan_api_key:
            # do magic here
            pass
        self.api = WebAPI(shodan_api_key)

    def run(self):
        pass
