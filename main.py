import asyncio
import json
import os
import traceback
from sys import platform

import pyfiglet
import requests
from colorama import init
from termcolor import colored

from src.utils import logger, file_logger
from src.service import ServiceApp


async def main():
    if platform != "linux":
        from ctypes import windll
        windll.kernel32.SetConsoleTitleW("Amino Service")
    os.system('cls' if os.name == 'nt' else 'clear')
    init()

    __info__ = json.loads(requests.get("https://github.com/LynxN1/amino_service/raw/master/version.json").text)

    __version__ = __info__["version"]
    __author__ = __info__["author"]
    __github__ = __info__["github"]
    __telegram__ = __info__["telegram"]
    try:
        __current__ = json.loads(open("version.json").read())["version"]
    except:
        __current__ = None

    if __version__ != __current__:
        logger.warning(f"New version of Amino Service available! ({__version__})\n")

    logger.info(colored(pyfiglet.figlet_format("Amino Service", font="big"), "green"))
    logger.info(colored(f"Author     {__author__}\n"
                        f"Version    {__current__}\n"
                        f"Github     {__github__}\n"
                        f"Telegram   {__telegram__}\n", "green"))

    try:
        await ServiceApp().start()
    except Exception as e:
        logger.error(e)
        file_logger.debug(traceback.format_exc())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
