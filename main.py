import os
import json
import requests

from sys import platform
from colorama import init
from termcolor import colored
from src.service import ServiceApp


if __name__ == '__main__':
    if platform != "linux":
        from ctypes import windll
        windll.kernel32.SetConsoleTitleW("Amino Service")
    os.system('cls' if os.name == 'nt' else 'clear')
    init()

    with open("version.json") as info_file:
        info = json.load(info_file)

    __version__ = info["version"]
    __author__  = info["author"]
    __github__  = info["github"]
    __newest__  = json.loads(requests.get("https://github.com/LynxN1/amino_service/raw/master/version.json").text)["version"]

    if __version__ != __newest__:
        print(colored(f"New version of Amino Service available! ({__newest__})\n", "yellow"))

    print(colored(open("src/view/logo.txt", "r").read().replace("v?", __version__).replace("a?", __author__).replace("g?", __github__).replace("_", " "), "green"))

    ServiceApp().run()
