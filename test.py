from __future__ import (absolute_import, division, print_function, unicode_literals)
import src.tradovate as td

if __name__ == "__main__":
    client = td.Client()
    trading = td.Accounting(client.session)

    a = trading.account_list()

    print(a)
