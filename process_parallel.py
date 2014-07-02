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


class Task(object):

    def __init__(self, work, workers):
        self.work = work
        self.workers = workers


class TaskChain(object):

    def __init__(self, producer, consumer):
        self.producer = producer
        self.consumer = consumer
        self.tasks = []

    def work(self, maxsize_jobs=0, maxsize_results=0):
        if not self.tasks:
            raise ValueError('You need at least one task, use add_task!')

        jobs_queue = Queue(maxsize=maxsize_jobs)
        results_queue = JoinableQueue(maxsize_results)
        #start the consumer
        #it will recieve as many StopSignals,
        #as there are workers in the last task
        last_task = self.tasks[-1]
        t = Thread(target=consume_result, args=(results_queue, self.consumer,
                                                last_task.workers))
        t.daemon = True
        t.start()

        first_task = self.tasks[0]
        for w in self.producer:
            jobs_queue.put(w)

        for _ in xrange(first_task.workers):
            jobs_queue.put(StopSignal)

        #collect all output queues, so we can call join later
        out_queues = []
        #the input from the previous worker,
        #will be the input to the next worker
        previous_output = None
        for i, task in enumerate(self.tasks):
            #if it is the first task, recieve input from the producer
            if i == 0:
                input_q = jobs_queue
            else:
                input_q = previous_output
            #if it is the last task, send output to consumer
            if i == len(self.tasks) - 1:
                output_q = results_queue
            else:
                output_q = JoinableQueue()
                out_queues.append(output_q)
                previous_output = output_q
            for _ in xrange(task.workers):
                Process(target=work,
                        args=(input_q, output_q, task.work)).start()

        results_queue.join()
        for out_queue in out_queues:
            out_queue.join()
        jobs_queue.close()
        t.join()

    def add_task(self, task, workers=1):
        ta = Task(task, workers)
        self.tasks.append(ta)
