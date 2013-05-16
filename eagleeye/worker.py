import itertools
import json

from eagleeye.utils import iterit
from eagleeye.utils import start_gen
from eagleeye.queue import Queue

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
            # XXX not super happy with this yet, but it's a start
            if job is not None:
                res = self.handle(job)
                yield job, res
            else:
                yield job


class RedisWorker(BaseWorker):
    qinput = None
    qoutput = None

    def jobs(self):
        """ Iterator that produces jobs to run in this worker.

        This returns None (a non-job) when there is nothing in the queue.
        """
        return self.qinput

    def handle(self, job):
        result = self.run(job)
        if result:
            for r in result:
                self.qoutput.send(r)
        return result

    def run(self, job):
        """ The actual work of the class.

        To take advantage of the result queuing, yield values rather
        than returning them.
        """
        raise NotImplementedError
