# Example code for testing Python log output

This is example code that shows how you can capture log messages using
the Python [`logging`
module](https://docs.python.org/3/library/logging.html) for tests (or
other purposes). I wrote this code for [a blog
post](https://airtower.wordpress.com/2020/07/07/testing-python-log-output/),
which you can also read below.

## Testing Python log output

Imagine you have a module and want to make sure everything’s working,
so you test. For functions the idea is usually pretty simple: Provide
some inputs, see if the output looks as expected. But what the
function is also supposed to write some log messages and you want to
check if they look the way they should? I was asking myself that
question on the weekend and found a solution that I think is fun:
Adding a custom log handler!

Maybe you’ve already used the
[`logging`](https://docs.python.org/3/library/logging.html) module?
Logging messages is pretty simple, for example:

```python
import logging
logger = logging.getLogger(__name__)

def add(*vargs):
    logger.debug('Calculating the sum of %s', vargs)
    res = sum(vargs)
    logger.debug('Result is %d', res)
    return res
```

Let’s assume you have that in a file `add.py`, and are going to write
tests in a separate file. A simple
[`unittest`](https://docs.python.org/3/library/unittest.html)-based
functionality test might look like this:

```python
import add
import unittest

class AddTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add.add(1, 2, 3), 6)
```

But what if you want to check if the debug messages are logged as
expected? I realized you can tap into the logging framework for that!
The logging module uses _handlers_ to send log messages wherever they
are supposed to go, and you can add as many as you want, so why not
add one that sends output to the test?

First you’re going to need a logger for the target module:

```python
        logger = logging.getLogger('add')
        logger.setLevel(logging.DEBUG)
```

Setting the level of the logger is necessary to ensure you really get
all messages (unless that has been set elsewhere already), but keep in
mind that that’s a process-wide setting. In a simple unit test like
here that’s not going to cause trouble. Now that we have the logger we
need to add a handler.

Also I want to have the input parameters and expected result in
variables, so I can use them later for comparing with the log
messages:

```python
        params = (1, 2, 3)
        expected_sum = 6
```

### Option one: A temporary log file

```python
        with tempfile.SpooledTemporaryFile(mode='w+') as log:
            handler = logging.StreamHandler(stream=log)
            logger.addHandler(handler)
            try:
                self.assertEqual(add.add(*params), expected_sum)
            finally:
                logger.removeHandler(handler)
            log.seek(0)
            logdata = log.read()
```

The
[`logging.StreamHandler`](https://docs.python.org/3/library/logging.handlers.html#logging.StreamHandler)
can write to all sorts of streams, its default is `sys.stderr`. I’m
using a
[`tempfile.SpooledTemporaryFile`](https://docs.python.org/3/library/tempfile.html#tempfile.SpooledTemporaryFile)
as the target because it is automatically cleaned up as soon as it is
closed, and the amount of log data will be small, so it makes sense to
keep it in memory.

The try/finally block around the function I’m testing ensures the
handler is always removed after the function call, even in case of an
exception (including those from failed assertions).

In the end you just have to read the file and check if the output looks like it should.

```python
        lines = logdata.splitlines()
        self.assertEqual(lines[0], f'Calculating the sum of {params!s}')
        self.assertEqual(lines[1], f'Result is {expected_sum}')
```

This also shows the disadvantages of this method: You end up with a
wall of text that you have to parse. With two lines it’s not too bad,
but with a lot of output it may get messy.

You can remedy that somewhat by [attaching a
`Formatter`](https://docs.python.org/3/library/logging.html#logging.Handler.setFormatter)
to the handler, which as the name indicates lets you format the log
messages, including adding some metadata.

### Option two: A message queue

```python
        q = queue.SimpleQueue()
        handler = logging.handlers.QueueHandler(q)
        logger.addHandler(handler)
        try:
            self.assertEqual(add.add(*params), expected_sum)
        finally:
            logger.removeHandler(handler)
```

This code is a bit shorter, because there’s no file to open. Instead
the log messages are added to the
[`queue`](https://docs.python.org/3/library/queue.html), and I can
retrieve them message by message:

```python
        self.assertEqual(q.get_nowait().getMessage(),
                         f'Calculating the sum of {params!s}')
        self.assertEqual(q.get_nowait().getMessage(),
                         f'Result is {expected_sum}')
```
This has two advantages:

1. I always get complete messages, no need to worry about splitting
   lines and newlines in messages.
2. The objects in the queue are not strings, they are
   [`LogRecord`](https://docs.python.org/3/library/logging.html#logging.LogRecord)
   objects, which hold all the metadata of the log message. Though in
   this example I’m just like “give me the message” and that’s it.

### Conclusion

Turns out the Python `logging` module is easier to use than I had
thought when I started figuring this out, and is fun to play with. Of
course with more complex tests this kind of analysis might get more
complex, too: You might not want to look at every message (maybe a
Filter helps?), or you might not be sure which order they arrive in.

Have fun coding!
