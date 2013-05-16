import subprocess
import time

from eagleeye import Queue
from eagleeye import RedisWorker

class CommandWorker(RedisWorker):
    qinput = Queue('job:raw')
    qoutput = Queue('result:raw')

    def run(self, job):
        outfile, command = job
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        yield [outfile, stdout]

class CommandResultWorker(RedisWorker):
    qinput = Queue('result:raw')

    def run(self, job):
        output_template, result = job
        output_filename = output_template.format(
            timestamp=time.time())
        with open(output_filename, 'w') as f:
            f.write(result)

