from process_parallel import process_parallel

if __name__ == '__main__':

    texts = [
        'this is an example text',
        'another text with no meaning',
        'some more text here'
    ]

    def work_generator():
        for text in texts:
            yield text

    def work_processor(line):
        return line.split()

    out = open('tokens.txt', 'w')

    def result_consumer(tokens):
        for token in tokens:
            out.write('%s\n' % token)

    process_parallel(work_generator(), work_processor, result_consumer)

    out.close()
