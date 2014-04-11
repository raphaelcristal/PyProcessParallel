PyProcessParallel
=================

PyProcessParallel is a little library which helps with writing parallel and memory controlled python code. It was manly used for preprocessing tasks, where the dataset was to large to load into memory.

## Data flow
PyProcessParallel expects you to write three functions:
* the work_generator, which will generate data for the workers, e.g. reading lines from a file
* the work_processor, which will take the output from the work_generator and will produce a result
* the result_consumer, which will take the output from the work_processor and e.g. writes it to a file or database

Each one of these components is connected via a queue, whose size can be controlled and therefore the memory consumption of your program.

## How to use

For a simpe example we will write a script which will tokenize some strings and write them to a file. You can find this example in example.py. First we will write the work_generator. The work_generator can either by a function with uses the keyword yield or an class which implements \__iter\__:

```python
texts = [
  'this is an example text',
  'another text with no meaning',
  'some more text here'
]
def work_generator():
  for text in texts:
    yield text
```
Now lets implement the work_processor, he will consume the lines yielded by the work_generator and transform them into tokens. This will be done in parallel!
```python
def work_processor(line):
  return line.split()
```

In the last step the results will be writen as one token per line.
```python
out = open('tokens.txt', 'w')
  def result_consumer(tokens):
    for token in tokens:
      out.write('%s\n' % token)
```

Now we can call the library and process our data. After the call has finished you can still make some cleanup calls like write some data or close file handles.
```python
process_parallel(work_generator, work_processor, result_consumer)
#do your clean up here
out.close()
```

## Memory Consumption
If your memory consumption you can limit the size of the queues. If your workers are not fast enough you should lower the maxsize_jobs paremeter. If your result_consumer is too slow the you should lower the maxsize_results parameter.
```python
process_parallel(work_generator, work_processor, result_consumer, maxsize_jobsize=100, maxsize_results=100)
```

## Workers
By default PyProcessParallel uses as many workers as you have cores. You can change this behaviour by calling the library like this:
```python
process_parallel(work_generator, work_processor, result_consumer, workers=2)
```

