from colorama import init
from termcolor import colored
from src import __version__, __author__
from src.service import ServiceApp

init()

if __name__ == '__main__':
    print(colored(open("src/draw/logo.txt", "r").read().replace("v?", __version__).replace("a?", __author__), "green"))
    ServiceApp()
