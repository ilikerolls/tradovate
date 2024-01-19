from __future__ import (absolute_import, division, print_function, unicode_literals)
import src.tradovate as td
import asyncio
from src.tradovate.config import CONFIG


async def main() -> None:
    print(f'Printing Configuration:\n{CONFIG}')
    client = td.Client()
    trading = td.Accounting(client.session)
    # Create Session
    # account_list = asyncio.run(trading.account_list())
    account_list = trading.account_list()

    print(f"Printing Session:\n{account_list}")
    #asyncio.run(client.session.close())
    await client.session.close()
    print('Done!')


if __name__ == "__main__":
    # asyncio.get_event_loop().run_until_complete(main())
    # main()
    asyncio.run(main())
