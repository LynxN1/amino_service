import traceback
from typing import Union

from termcolor import colored

import amino_async
from amino_async import Client, SubClient
from src.utils import database
from src.utils.converter import convert_from_txt
from src.utils.logger import logger, file_logger
from src.utils.login import login
from src.scripts.badass import Badass
from src.scripts.bot_management import BotManagement
from src.scripts.chat_moderation import ChatModeration
from src.scripts.single_management import SingleManagement
from src.utils.configs import MAIN_MENU, CHOICE_ACTION_TEXT
from src.utils.table import create_table


class ServiceApp:

    sub_client: SubClient
    client: Union[Client, bool]

    async def start(self):
        while True:
            accounts = database.get_auth_data()
            if accounts:
                logger.info("Аккаунты:")
                for x, account in enumerate(accounts, 1):
                    logger.info(f"{x}. {account[0]}")
                choice = input("\n" + "Введите \"+\" чтобы добавить новый аккаунт, или \"-\" для удаления " + "\n" + ">>> ")
                if choice == "+":
                    email = input("Почта: ")
                    password = input("Пароль: ")
                    database.set_auth_data(email, password)
                elif choice == "-":
                    delete_choice = input("Введите номер аккаунта: ")
                    index = int(delete_choice) - 1
                    email = accounts[index][0]
                    database.remove_account(email)
                else:
                    index = int(choice) - 1
                    email = accounts[index][0]
                    password = accounts[index][1]
                    break
            else:
                email = input("Почта: ")
                password = input("Пароль: ")
                database.set_auth_data(email, password)
                break

        self.client = await login((email, password))
        if not self.client:
            input()
            exit(0)
        logger.info("Авторизация прошла успешно!")

        subs = await self.client.sub_clients(start=0, size=100)
        if subs.comId:
            for x, com_name in enumerate(subs.name, 1):
                logger.info(f"{x}. {com_name}")
            com_index = int(input("Введите номер сообщества: "))
            self.sub_client = amino_async.SubClient(comId=subs.comId[com_index - 1], client=self.client)
            await self.run()
        else:
            logger.error("Сообществ не найдено")
            exit(0)

    async def run(self):
        while True:
            try:
                logger.info(colored(create_table("Меню", MAIN_MENU), "cyan"))
                management_choice = input(CHOICE_ACTION_TEXT)
                if management_choice == "1":
                    await SingleManagement(self.sub_client).start()
                if management_choice == "2":
                    await BotManagement(self.sub_client).start()
                if management_choice == "3":
                    await ChatModeration(self.sub_client).start()
                if management_choice == "4":
                    await Badass(self.sub_client).start()
                if management_choice == "0":
                    convert_from_txt()
            except Exception as e:
                logger.error(str(e))
                file_logger.debug(traceback.format_exc())
