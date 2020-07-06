#!/usr/bin/python3
import logging
import sys

logger = logging.getLogger(__name__)


def add(*vargs):
    logger.debug('Calculating the sum of %s', vargs)
    res = sum(vargs)
    logger.debug('Result is %d', res)
    return res


if __name__ == '__main__':
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    a = add(*[int(i) for i in sys.argv[1:]])
    logger.info('%d', a)
