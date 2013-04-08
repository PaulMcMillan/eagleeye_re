from eagleeye import RedisWorker

class RedisTestWorker(RedisWorker):
    qinput = 'testin'
    qoutput = 'testout'

    def jobs(self):
        return range(10)

    def run(self, job):
        return "Processed: %s" % job

class RedisReader(RedisWorker):
    qinput = 'testout'

    def jobs(self):
        res = True
        while res:
            res = self.read(blocking=False)
            yield res

    def run(self, job):
        return 'ReaderProcessed: %s' % job

def test_redisworker():
    w = RedisTestWorker()
    for r in w():
        print r
    # Consume all the things
    w2 = RedisReader()
    for r in w2():
        print r
