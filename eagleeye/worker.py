import itertools
import json

import redis

from eagleeye.utils import iterit
from eagleeye.utils import start_gen

# RPOP, LPUSH
# NO!
# LPOP RPush

class BaseWorker(object):
    # workers are by default persistent
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
        """ Iterate through available jobs, handling each one.  Note
        that this construction leaves the blocking/non-blocking
        decision up to the job itself:
         - if jobs is finite, this handles each item once
         - if jobs is infinite, this yields None when the job is not true
        This works because None is never a valid job.
        """
        for job in self.jobs(*args, **kwargs):
            if job:
                yield self.handle(job)
            else:
                yield None

class RedisWorker(BaseWorker):
    qinput = None
    qoutput = None

    def __init__(self, qinput=None, qoutput=None, *args, **kwargs):
        self.qinput = self.queue(qinput or self.qinput)
        self.qoutput = self.queue(qoutput or self.qoutput)
        # This should become a shared pool once we have worker management
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        return super(RedisWorker, self).__init__(*args, **kwargs)

    def serialize(self, value):
        """ A default data serializer """
        return json.dumps(value)

    def deserialize(self, value):
        """ A default data deserializer.

        Doesn't attempt to deserialize None.
        """
        if value:
            return json.loads(value)

    @start_gen
    def queue(self, queue_name):
        """ Create a queue object. Treat this like any other iterator,
        except that it also supports the send(value) method in
        addition to the standard next().

        Note that queues continue to return None objects when they're
        empty, so you can iterate forever over them.
        """
        result = yield
        while True:
            while result:
                result = (self.serialize(v) for v in result)
                result = yield self.redis.rpush(queue_name, *result)
            result = yield self.deserialize(self.redis.lpop(queue_name))

    def finite_queue(self, queue_name):
        """ Use this for a queue that stops when there are no more
        items rather than returning None forever.
        """
        return itertools.takewhile(bool, self.queue(queue_name))

    def jobs(self):
        """ Iterator that produces jobs to run in this worker.

        This returns None (a non-job) when there is nothing in the queue.
        """
        return queue(self.qinput)

    def handle(self, job):
        result = self.run(job)
        if result:
            self.qoutput.send(result)

    def run(self, job):
        """ The actual work of the class.

        To take advantage of the result queuing, yield values rather
        than returning them.
        """
        raise NotImplementedError
