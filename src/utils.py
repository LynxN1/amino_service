import logging
import os
import random
import sys

import coloredlogs

from src import configs, database, amino_async

logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
file_logger = logging.getLogger('file_logger')
file_logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_formatter = coloredlogs.ColoredFormatter(fmt="%(message)s")
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler('log.log', encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(fmt='[%(asctime)s][%(filename)s:%(lineno)d]: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)
file_logger.addHandler(file_handler)


if database.get_bots():
    spaces = max([len(i[0]) for i in database.get_bots()])
else:
    spaces = 25


def service_align(email: str, action: str, level: str = None):
    if level is None:
        logger.info("[" + email + " " * spaces + "]: " + action)
    elif level == "debug":
        logger.debug("[" + email + " " * spaces + "]: " + action)
    elif level == "warning":
        logger.warning("[" + email + " " * spaces + "]: " + action)
    elif level == "error":
        logger.error("[" + email + " " * spaces + "]: " + action)


async def link_identify(sub_client, input_text: str = "Ссылка: "):
    link = input(input_text)
    from_code = await sub_client.client.get_from_code(link.split('/')[-1])
    return from_code.objectId


async def get_chat_id(sub_client: amino_async.SubClient):
    logger.info("1 - Выбрать чат из списка")
    logger.info("2 - Выбрать чат по ссылке")
    choice = int(input(">>> "))
    if choice == 1:
        chats = await sub_client.get_chat_threads(start=0, size=100)
        if not chats.chatId:
            raise Exception("Список чатов пуст")
        for x, title in enumerate(chats.title, 1):
            logger.info(f"{x}. {title}")
        index = input("Выберите чат: ")
        if int(index) <= 0 or int(index) > len(chats.chatId):
            raise Exception("Invalid chat number")
        return chats.chatId[int(choice)-1]
    if choice == 2:
        object_id = await link_identify(sub_client)
        return object_id


def convert_from_txt():
    if not os.path.exists(os.path.join(configs.BOTS_TXT_PATH)):
        logger.error("Файл bots.txt не найден")
        return
    bots = open(configs.BOTS_TXT_PATH, "r").readlines()
    accounts = []
    if bots:
        for i in bots:
            split = i.replace(" ", "").replace("\n", "").split(":")
            try:
                accounts.append({"email": split[0], "password": split[1]})
            except IndexError:
                pass
        database.set_bots(accounts)
    else:
        logger.warning("Файл пустой")


class UsernameGenerator:
    def __init__(self, min_length: int = 0, max_length: int = 0):
        # command feedback for various arguments
        self.min_length, self.max_length = min_length, max_length  # quells PyCharm "might be referenced before assignment" warnings

        # initialize tuples

        self.consonants = ('b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n',
                           'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z')

        self.vowels = ('a', 'e', 'i', 'o', 'u')

        self.cons_weighted = (("t", "n"), ("r", "s", "h", "d"), ("l", "f", "c", "m"), ("g", "y", "p", "w", "b"),
                              ("v", "b", "j", "x", "q"), "z")
        self.vow_weighted = (("e", "a", "o"), ("i", "u"))
        self.double_cons = ("he", "re", "ti", "ti", "hi", "to", "ll", "tt", "nn", "pp", "th", "nd", "st", "qu")
        self.double_vow = ("ee", "oo", "ei", "ou", "ai", "ea", "an", "er", "in",
                           "on", "at", "es", "en", "of", "ed", "or", "as")

    def generate(self):
        username, is_double, num_length = "", False, 0  # reset variables
        if random.randrange(10) > 0:
            is_consonant = True
        else:
            is_consonant = False

        length = random.randrange(self.min_length, self.max_length)

        if random.randrange(5) == 0:  # decide if there will be numbers after the name
            num_length = random.randrange(3) + 1
            if length - num_length < 2:  # we don't want the username to be too short
                num_length = 0

        for j in range(length - num_length):  # we leave room for the numbers after the name here
            if len(username) > 0:
                if username[-1] in self.consonants:
                    is_consonant = False
                elif username[-1] in self.consonants:
                    is_consonant = True
            if not is_double:  # if the last character was a double, skip a letter
                # 1 in 8 chance of doubling if username is still short enough
                if random.randrange(8) == 0 and len(username) < int(length - num_length) - 1:
                    is_double = True  # this character will be doubled
                if is_consonant:
                    username += self.get_consonant(is_double)  # add consonant to username
                else:
                    username += self.get_vowel(is_double)  # add vowel to username
                is_consonant = not is_consonant  # swap consonant/vowel value for next time
            else:
                is_double = False  # reset double status so the next letter won't be skipped
        if random.randrange(2) == 0:
            # this was the best method I could find to only capitalize the first letter in Python 3
            username = username[:1].upper() + username[1:]
        if num_length > 0:
            for j in range(num_length):  # loop 1 - 3 times
                username += str(random.randrange(10))  # append a random number, 0 - 9
        return username

    def get_consonant(self, is_double):
        if is_double:
            return random.choice(self.double_cons)  # add two consonants from our pre-defined tuple
        else:
            # we're just guessing at some good weights here. This is how more common letters get used more
            i = random.randrange(100)
            if i < 40:
                weight = 0
            elif 65 > i >= 40:
                weight = 1
            elif 80 > i >= 65:
                weight = 2
            elif 90 > i >= 80:
                weight = 3
            elif 97 > i >= 90:
                weight = 4
            else:
                # the last group is Z by itself. No point in going through extra code when we can finish it here
                return self.cons_weighted[5]
            # return a random consonant based on the weight
            return self.cons_weighted[weight][random.randrange(len(self.cons_weighted[weight]))]

    def get_vowel(self, is_double):
        if is_double:
            return random.choice(self.double_vow)  # add two vowels from our pre-defined tuple
        else:
            i = random.randrange(100)
            if i < 70:
                weight = 0
            else:
                weight = 1
            # return a random vowel based on the weight
            return self.vow_weighted[weight][random.randrange(len(self.vow_weighted[weight]))]
