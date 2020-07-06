#!/usr/bin/python3
import add
import logging
import logging.handlers
import queue
import tempfile
import unittest


class AddTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add.add(1, 2, 3), 6)

    def test_add_check_log_file(self):
        logger = logging.getLogger('add')
        logger.setLevel(logging.DEBUG)

        params = (1, 2, 3)
        expected_sum = 6

        with tempfile.SpooledTemporaryFile(mode='w+') as log:
            handler = logging.StreamHandler(stream=log)
            logger.addHandler(handler)
            try:
                self.assertEqual(add.add(*params), expected_sum)
            finally:
                logger.removeHandler(handler)
            log.seek(0)
            logdata = log.read()

        lines = logdata.splitlines()
        self.assertEqual(lines[0], f'Calculating the sum of {params!s}')
        self.assertEqual(lines[1], f'Result is {expected_sum}')

    def test_add_check_log_queue(self):
        logger = logging.getLogger('add')
        logger.setLevel(logging.DEBUG)

        params = (1, 2, 3)
        expected_sum = 6

        q = queue.SimpleQueue()
        handler = logging.handlers.QueueHandler(q)
        logger.addHandler(handler)
        try:
            self.assertEqual(add.add(*params), expected_sum)
        finally:
            logger.removeHandler(handler)

        self.assertEqual(q.get_nowait().getMessage(),
                         f'Calculating the sum of {params!s}')
        self.assertEqual(q.get_nowait().getMessage(),
                         f'Result is {expected_sum}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
