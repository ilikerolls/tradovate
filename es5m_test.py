from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from src.tradovate.stream.trade import subcribe
import setenv

if __name__ == '__main__':
    interval = 5
    subcribe('ESU2', interval)
