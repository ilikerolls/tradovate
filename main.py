from __future__ import (absolute_import, division, print_function, unicode_literals)
import src.tradovate as td
import asyncio
from src.tradovate.config import CONFIG, logger
import src.webhooks.webhook_listener_lite as wl


async def main() -> None:
    logger.info(f'Configuration:\n{CONFIG}')
    print('***************Before await')
    # await task
    await asyncio.sleep(15)
    print("*************After await")
    print('Done!')


if __name__ == "__main__":
    wh_server = wl.WHListener(port=8000, auto_start=True)
    # Run Main Asynchronous Code
    asyncio.run(main())
    wh_server.stop()
