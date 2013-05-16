import redis

# LPOP RPush


class Queue(object):
    def __init__(self, queue_name, *args, **kwargs):
        # This should become a shared pool once we have worker management
        self.queue_name = queue_name
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.is_finite = False
        return super(Queue, self).__init__(*args, **kwargs)

    def __iter__(self):
        return self

    def finite(self):
        self.is_finite = True
        return self

    def next(self):
        res = self.redis.lpop(self.queue_name)
        if res or not self.is_finite:
            return res
        else:
            self.is_finite = False
            raise StopIteration

    def send(self, value):
        return self.redis.rpush(self.queue_name, value)

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
