import socket
from eagleeye import selchrome

def test_imager():
    worker = selchrome.SeleniumWorker(socket_timeout=10, blocking=False)
    worker.write('image:http', 'http://google.com:80')
    worker.write('image:http', 'http://localhost:8981')
    sock = socket.socket()
    sock.bind(('localhost', 8981))
    sock.listen(0)
    for r in worker():
        print type(r)
    sock.close()

    worker = selchrome.WriteScreenshot(blocking=False)
    for r in worker():
        print type(r)
