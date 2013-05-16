from eagleeye.raw_command import CommandWorker, CommandResultWorker

from eagleeye import get_redis
r = get_redis()
r.flushdb()

worker = CommandWorker()

worker.qinput.send(['out/ls{timestamp}.out', ['ls']])
worker.qinput.send(['out/whomai.out', ['whoami']])
worker.qinput.send(['out/pwd.out', ['pwd']])

worker.qinput.finite()

for result in worker():
    print result

resworker = CommandResultWorker()

resworker.qinput.finite()

for result in resworker():
    print result
