from eagleeye.worker import BaseWorker

class TestWorker(BaseWorker):
    loopcount = 10
    def jobs(self):
        return range(10)

    def handle(self, job, *args, **kwargs):
        return 'well done: %s %s %s' % (job, args, kwargs)


def test_base():
    worker = TestWorker()
    assert worker
    for result in worker():
        print result

def test_extra_args():
    worker = TestWorker()
    for result in worker():
        print result

