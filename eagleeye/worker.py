import json

import redis

from eagleeye.utils import iterit

# RPOP, LPUSH

class BaseWorker(object):
    # workers are by default persistent and blocking
    def jobs(self):
        """ Jobs generator must be implemented by subclass. """
        raise NotImplementedError

    def handle(self, job):
        """ Handle method must be implemented by subclasses.

        Most framework subclasses will provide a handle() which makes a
        call to an user-implemented run.
        """
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        for job in self.jobs(*args, **kwargs):
            yield self.handle(job)


class RedisWorker(BaseWorker):
    qinput = None
    qoutput = None
    blocking = True

    def __init__(self, blocking=None, *args, **kwargs):
        if blocking is not None:
            self.blocking = blocking
        # This should become a shared pool once we have worker management
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        return super(RedisWorker, self).__init__(*args, **kwargs)

    def serialize(self, value):
        """ A default data serializer """
        return json.dumps(value)

    def deserialize(self, value):
        """ A default data deserializer """
        return json.loads(value)

    def read(self, queue=None, timeout=0, blocking=True):
        if not queue:
            queue = self.qinput

        if blocking:
            res = self.redis.brpop(queue, timeout)
            if res:
                res = res[1]
        else:
            res = self.redis.rpop(queue)

        if res:
            return self.deserialize(res)

    def write(self, queue, *values):
        values = iterit(values, cast=self.serialize)
        return self.redis.lpush(queue, *values)

    def jobs(self):
        """ Iterator that produces jobs to run in this worker.

        By default, this will read forever, blocking when there's no
        task. Don't subclass this and put something heavy here,
        instead make a new worker for that task.
        """
        while True:
            result = self.read(blocking=self.blocking)
            if result is None:  # our (non-blocking) read found no result
                return  # so finish this generator
            yield result

    def handle(self, job):
        result = self.run(job)
        if self.qoutput:
            self.write(self.qoutput, result)
        return result

    def run(self, job):
        """ The actual work of the class """
        raise NotImplementedError
