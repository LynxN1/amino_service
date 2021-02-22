import os
import json
import requests

from ctypes import windll
from colorama import init
from termcolor import colored
from src.service import ServiceApp

os.system('cls' if os.name == 'nt' else 'clear')
windll.kernel32.SetConsoleTitleW("Amino Service")
init()

with open("version.json") as info_file:
    info = json.load(info_file)

__version__ = info["version"]
__author__ = info["author"]
__github__ = info["github"]
__newest__ = json.loads(requests.get("https://github.com/LynxN1/amino_service/raw/master/version.json").text)["version"]


if __version__ != __newest__:
    print(f"\nNew version of Amino Service available! ({__newest__})\n")


if __name__ == '__main__':
    print(colored(open("src/draw/logo.txt", "r").read().replace("v?", __version__).replace("a?", __author__).replace("g?", __github__).replace("_", " "), "green"))
    ServiceApp()
