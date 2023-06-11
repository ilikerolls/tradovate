from __future__ import (absolute_import, division, print_function, unicode_literals)
import src.tradovate as td
import asyncio
import setenv


# Let's try this!
def main():
    client = td.Client()
    trading = td.Accounting(client.session)
    a = asyncio.run(trading.account_list())

    print(a)
    asyncio.run(client.session.close())
    print(f'Done!')


if __name__ == "__main__":
    # asyncio.get_event_loop().run_until_complete(main())
    main()
