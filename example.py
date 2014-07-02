from process_parallel import TaskChain

if __name__ == '__main__':

    texts = [
        'this is an example text',
        'another text with no meaning',
        'some more text here'
    ]

    def work_generator():
        for text in texts:
            yield text

    def w1(line):
        return line.split()

    def w2(tokens):
        return tokens*10

    def result_consumer(tokens):
        print tokens

    task_chain = TaskChain(work_generator(), result_consumer)
    task_chain.add_task(w1)
    task_chain.add_task(w2)
    task_chain.work()
