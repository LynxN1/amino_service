import asyncio
import traceback

from tabulate import tabulate
from termcolor import colored

from src.utils import get_chat_id, logger, file_logger
from src import configs, amino_async


class Badass:
    def __init__(self, sub_client: amino_async.SubClient):
        self.sub_client = sub_client

    async def start(self):
        while True:
            try:
                logger.info(colored(tabulate(
                    configs.BADASS_MENU,
                    headers=[configs.CATEGORY_NAMES[3]],
                    tablefmt="fancy_grid"
                ), "cyan"))
                choice = input(configs.CHOICE_ACTION_TEXT)
                if choice == "1":
                    await self.send_system_message(await get_chat_id(self.sub_client))
                if choice == "2":
                    await self.spam_system_message(await get_chat_id(self.sub_client))
                if choice == "3":
                    await self.invite_all_users(await get_chat_id(self.sub_client))
                if choice == "4":
                    await self.spam_public_chats()
                if choice == "5":
                    await self.crush_all_public_chats()
                if choice == "b":
                    break
            except Exception as e:
                logger.error(str(e))
                file_logger.debug(traceback.format_exc())

    async def send_system_message(self, chatid: str):
        await self.sub_client.join_chat(chatid)
        while True:
            message_type = int(input("Тип сообщения: "))
            message = input("Текст: ")
            await self.sub_client.send_message(chatId=chatid, messageType=message_type, message=message)
            logger.info("Сообщение отправлено")
            choice = input("Повторить?(д/н): ")
            if choice.lower() == "н":
                break

    async def spam_system_message(self, chatid: str):
        message_type = int(input("Тип сообщения: "))
        message = input("Текст: ")
        await self.sub_client.join_chat(chatid)
        logger.info("Спам начался...")
        while True:
            await asyncio.gather(*[asyncio.create_task(self.sub_client.send_message(message, message_type, chatid)) for _ in range(100)])

    async def invite_all_users(self, chatid: str):
        admins, admins2 = await self.sub_client.get_all_users(type="leaders", start=0, size=100), await self.sub_client.get_all_users(type="curators", start=0, size=100)

        async def start_invite(user_id):
            if user_id not in [*admins.profile.userId, *admins2.profile.userId]:
                try:
                    await self.sub_client.invite_to_chat(user_id, chatid)
                    logger.info(f"{user_id} приглашен в чат")
                except:
                    pass
            else:
                logger.info(f"{user_id} лидер или куратор")
        for i in range(0, 10000, 100):
            users = await self.sub_client.get_online_users(start=i, size=100)
            if not users.profile.userId:
                break
            await asyncio.gather(*[asyncio.create_task(start_invite(i)) for i in users.profile.userId])
        logger.info("Все пользователи приглашены в чат")

    async def spam_public_chats(self):
        async def start_spam(chat_id):
            try:
                await self.sub_client.join_chat(chat_id)
                await self.sub_client.send_message(message, message_type, chat_id)
                logger.info(f"Сообщение отправлено {chat_id}")
            except:
                return
        message_type = int(input("Тип сообщения: "))
        message = input("Текст: ")
        logger.info("Спам начался...")
        for i in range(0, 5000, 100):
            chats = await self.sub_client.get_public_chat_threads(start=i, size=100)
            if not chats.chatId:
                break
            await asyncio.gather(*[asyncio.create_task(start_spam(i)) for i in chats.chatId])

    async def crush_all_public_chats(self):
        async def start_crush(chat_id):
            try:
                await self.sub_client.join_chat(chat_id)
                while True:
                    await asyncio.gather(*[asyncio.create_task(self.sub_client.send_message(message, message_type, chat_id)) for _ in range(100)])
            except:
                return
        message_type = int(input("Тип сообщения: "))
        message = input("Текст: ")
        chats = await self.sub_client.get_public_chat_threads(start=0, size=100)
        await asyncio.gather(*[asyncio.create_task(start_crush(i)) for i in chats.chatId])
