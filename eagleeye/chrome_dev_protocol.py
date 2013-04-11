# unfinished and not working at present. Probably lower overhead than
# chromedriver though, if it is made to work.
import base64

import json

import websocket
import requests
from pyvirtualdisplay.smartdisplay import SmartDisplay

from eagleeye import RedisWorker

from easyprocess import EasyProcess

class ChromeWorker(RedisWorker):
    qinput = 'image:http'
    qoutput = 'result:save_image'

    def run(self, job):
        with SmartDisplay(visible=0) as disp:
            print "starting process"
            with EasyProcess(
                'sensible-browser --user-data-dir=/tmp/ http://%s:80/' % job):
                print "grabbing image"
                img = disp.waitgrab()
                print "am here"
                imgstr = img.tostring()
        print "got here"
        return imgstr

    def serialize(self, data):
        # This is just binary data, so...
        return data

    def unserialize(self, data):
        return data


def get_screenshot():
    ws = websocket.create_connection("ws://localhost:9222/devtools/page/36E158D3-2D52-B115-339F-28D02350A3DC")
    rq = dict(id=123, method="Page.captureScreenshot")
    ws.send(json.dumps(rq))
    result = json.loads(ws.recv())
    with open('out.png', 'w') as f:
        f.write(base64.b64decode(result['result']['data']))


#get_screenshot()
