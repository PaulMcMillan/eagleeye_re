import os

import redis

def get_redis():
    # ugh, fixme
    redis_address = os.environ.get('REDIS_ADDRESS')
    if redis_address:
        return redis.StrictRedis.from_url(redis_address)
    else:
        return redis.StrictRedis()

from eagleeye.queue import Queue

from eagleeye.worker import BaseWorker
from eagleeye.worker import RedisWorker

from eagleeye.nmap import NmapWorker
from eagleeye.shodan_query import ShodanWorker
