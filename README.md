EagleEye (Redis Edition)
========================

This is yet another reimplementation of the eagleeye concept. This one
directly uses a redis backend for queues, forgoing the unnecessary
complexity of rabbitmq and celery. It should have similar or greater
performance, but does not offer the same message integrity promises
(which don't matter so much to this tool in any case).

Rather than offering a threaded, unified worker model, each kind of
worker handles one specific task. This makes it easy to adjust the
ratios of these workers to fit your particular hardware and
performance needs.

For now, worker input and output types are encoded in the worker
definitions. If you need to change the task flow, this is as simple as
changing your worker definitions.

Task Flow
---------

Queues
------

Search queues are high-level abstrations of search tasks
 * search:shodan - (query, page) for a task. Each page individual search task.

Verify queues take a string of the form "address:port". The
protcol-specific queues will eventually perform some validation.

 * verify:port:# - verifies that a port is open at all with nmap
 * verify:port:set - set of all verify:port:# keys
 * verify:http
 * verify:https
 * verify:vnc

The image queues have protocol-specific workers which take snapshots
 * image:http
 * image:https
 * image:vnc

The result processing queue is generally the last step.
 * result:save_image


Security
--------

Use redis passwords so random people on the internet can't connect to
your instance. If you need more security than that, use ssh port
forwards or stunnel with client-certs to validate your
communications. It is generally assumed that shared-secret security is
good enough for a tool like this, so extreme care has not been taken
to prevent one part of the system from misusing another if it has
authentication information.
