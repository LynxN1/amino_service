from colorama import init
from termcolor import colored
from src import __version__, __author__
from src.service import ServiceApp
import os

init()

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    logo = open("src/draw/logo.txt", "r").read().replace("v?", __version__).replace("a?", __author__)
    print(colored(logo, "green"))
    ServiceApp().run()
