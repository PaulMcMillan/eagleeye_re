from eagleeye import chrome

def test_chrome():
    worker = chrome.ChromeWorker(blocking=False)
    worker.write('image:http', '"google.com"')
    for r in worker():
        print len(r)
