import itertools
import json

import redis

from eagleeye.utils import iterit
from eagleeye.utils import start_gen

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
            # XXX not happy with this yet, but it's a start
            if job is not None:
                res = self.handle(job)
            yield job


class RedisWorker(BaseWorker):
    qinput = None
    qoutput = None

    def __init__(self, qinput=None, qoutput=None, *args, **kwargs):
        self.qinput = self.queue(qinput or self.qinput)
        self.qoutput = self.queue(qoutput or self.qoutput)


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
                result = [self.serialize(r) for r in result]
                result = yield self.redis.rpush(queue_name, result)
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
        return self.qinput

    def handle(self, job):
        result = self.run(job)
        if result:
            self.qoutput.send(result)
        return result

    def run(self, job):
        """ The actual work of the class.

        To take advantage of the result queuing, yield values rather
        than returning them.
        """
        raise NotImplementedError
