"""
process_parallel.py
~~~~~~~~~~~~~~~~~~~

A simple library whichs helps with parallel computing.
:copyright: (c) 2014 by Raphael Brand.
:license: MIT, see LICENSE for more details.
"""
from multiprocessing import Process, JoinableQueue, Queue, cpu_count
from threading import Thread


class StopSignal(object):
    pass


def work(jobs, results, job_consumer):
    while True:
        task = jobs.get()

        if task is StopSignal:
            results.put(StopSignal)
            break
        else:
            r = job_consumer(task)
            results.put(r)


def consume_result(results, result_consumer, num_workers):
    finished_workers = 0
    while True:
        r = results.get()

        if r is StopSignal:
            finished_workers += 1
        else:
            result_consumer(r)

        results.task_done()
        if finished_workers == num_workers:
            results.close()
            break


def process_parallel(work_generator, job_consumer, result_consumer,
                     workers=cpu_count(), maxsize_jobs=0, maxsize_results=0):
    jobs = Queue(maxsize=maxsize_jobs)
    results = JoinableQueue(maxsize_results)

    t = Thread(target=consume_result, args=(results, result_consumer,
                                            workers))
    t.daemon = True
    t.start()

    for _ in xrange(workers):
        Process(target=work, args=(jobs, results, job_consumer)).start()

    for w in work_generator():
        jobs.put(w)

    for _ in xrange(workers):
        jobs.put(StopSignal)

    results.join()
    jobs.close()
    t.join()
