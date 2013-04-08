import shodan

from eagleeye import RedisWorker

class ShodanSearch(RedisWorker):
    qoutput = 'verify'

    def get_shodan_result(query, page=1):
        logger.info("Fetching shodan results query: %s page: %s", query, page)
        api = shodan.WebAPI(API_KEY)
        results = api.search(query, page=page)['matches']
        for result in results:
            self.write('verify', results)
        return results
