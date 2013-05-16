import json

import redis

# LPOP RPush

from eagleeye import get_redis

class Queue(object):
    def __init__(self, queue_name, *args, **kwargs):
        # This should become a shared pool once we have worker management
        self.queue_name = queue_name
        self.redis = get_redis()
        self.is_finite = False
        return super(Queue, self).__init__(*args, **kwargs)

    def __iter__(self):
        return self

    def finite(self):
        self.is_finite = True
        return self

    def infinite(self):
        self.is_finite = False
        return self

    def next(self):
        res = self.redis.lpop(self.queue_name)
        if not res and self.is_finite:
            raise StopIteration
        return self.deserialize(res)


    def send(self, value):
        return self.redis.rpush(self.queue_name, self.serialize(value))

    def serialize(self, value):
        """ A default data serializer """
        return json.dumps(value)

    def deserialize(self, value):
        """ A default data deserializer.

        Doesn't attempt to deserialize None.
        """
        if value:
            return json.loads(value)

    def clear(self):
        return self.redis.delete(self.queue_name)
