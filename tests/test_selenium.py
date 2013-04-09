from eagleeye import selworker

def test_imager():
    worker = selworker.SeleniumWorker(blocking=False)
    worker.write('image:http', 'http://google.com:80')
#    worker.write('image:http', 'http://localhost:8000')
    for r in worker():
        print r

    worker = selworker.WriteScreenshot(blocking=False)
    for r in worker():
        print r

# def test_writer():
#     worker = selworker.WriteScreenshot(blocking=False)
#     worker.write('result:save_image', ['somedata', 'test_url'])
#     for r in worker():
#         print r

