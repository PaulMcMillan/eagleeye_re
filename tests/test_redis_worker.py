from eagleeye import RedisWorker, BaseWorker

class TestBaseWorker(BaseWorker):
    def jobs(self):
        return range(10)

    def handle(self, job):
        print "Handling job %s" % job
        return job

# def test_baseworker():
#     worker = TestBaseWorker()
#     print worker.jobs()
#     for x in worker():
#         print 'Result: ', x

import itertools

class RedisTestWorker(RedisWorker):
    qinput = 'testin'
    qoutput = 'testout'

    def jobs(self):
        return range(10)

    def run(self, job):
        yield "Processed: %s" % job

class RedisReader(RedisWorker):
    qinput = 'testout'

    def jobs(self):
        for res in itertools.takewhile(bool, self.qinput):
            yield res

    def run(self, job):
        print 'ReaderProcessed: %s' % job

def test_redisworker():
    w = RedisTestWorker()
    for r in w():
        print repr(r)
    # Consume all the things
    w2 = RedisReader()
    for r in w2():
        print repr(r)

