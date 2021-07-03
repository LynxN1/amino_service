import asyncio
import os
import time
import traceback

from termcolor import colored

import amino_async
from src.utils.chat import get_chat_id
from src.utils.logger import logger, file_logger
from src.utils.configs import CHAT_SETTINGS_PATH, CHAT_MODERATION_MENU, CATEGORY_NAMES, CHOICE_ACTION_TEXT
from src.utils.table import create_table


class ChatModeration:
    def __init__(self, sub_client: amino_async.SubClient):
        self.sub_client = sub_client

    async def start(self):
        while True:
            try:
                logger.info(colored(create_table(CATEGORY_NAMES[2], CHAT_MODERATION_MENU), "cyan"))
                choice = input(CHOICE_ACTION_TEXT)
                if choice == "1":
                    await self.clear_chat(await get_chat_id(self.sub_client))
                if choice == "2":
                    await self.save_chat_settings(await get_chat_id(self.sub_client))
                if choice == "3":
                    await self.set_view_mode(await get_chat_id(self.sub_client))
                if choice == "4":
                    await self.set_view_mode_timer(await get_chat_id(self.sub_client))
                if choice == "b":
                    break
            except Exception as e:
                logger.error(str(e))
                file_logger.debug(traceback.format_exc())

    async def clear_chat(self, chatid: str):
        count = int(input("Количество сообщений: "))
        deleted = 0
        next_page = None
        chat = await self.sub_client.get_chat_thread(chatId=chatid)
        if chat.coHosts is not None:
            co_hosts = chat.coHosts
        else:
            co_hosts = []
        admins = [*co_hosts, chat.author.userId]
        if self.sub_client.client.userId not in admins:
            logger.error("У вас нет прав помощника")
            return
        while True:
            messages = await self.sub_client.get_chat_messages(chatId=chatid, size=100, pageToken=next_page)
            if not messages.messageId:
                break
            next_page = messages.nextPageToken
            if deleted >= count:
                break
            await asyncio.gather(*[asyncio.create_task(self.sub_client.delete_message(chatid, i)) for i in messages.messageId])
            deleted += 100
            logger.info(f"Удалено {deleted} сообщений")

    async def save_chat_settings(self, chatid: str):
        if not os.path.exists(CHAT_SETTINGS_PATH):
            os.mkdir(CHAT_SETTINGS_PATH)
        with open(os.path.join(CHAT_SETTINGS_PATH, f"{chatid}.txt"), "w", encoding="utf-8") as settings_file:
            chat = await self.sub_client.get_chat_thread(chatId=chatid)
            data = "====================Title====================\n" \
                   f"{chat.title}\n\n" \
                   "===================Content===================\n" \
                   f"{chat.content}\n\n" \
                   "====================Icon====================\n" \
                   f"{chat.icon}\n\n" \
                   "=================Background=================\n" \
                   f"{chat.backgroundImage}\n\n"
            if chat.announcement:
                data += "================Announcement================\n"
                data += f"{chat.announcement}\n"
            if chat.userAddedTopicList:
                data += "================Tags================\n"
                for i in chat.userAddedTopicList:
                    data += f"{i.get('name')}\nColor: {i.get('style').get('backgroundColor')}\n"
            settings_file.write(data)
        logger.info(f"Настройки сохранены по этому пути: {os.path.join(CHAT_SETTINGS_PATH, f'{chatid}.txt')}")

    async def set_view_mode(self, chatid: str):
        chat = await self.sub_client.get_chat_thread(chatId=chatid)
        admins = [*chat.coHosts, chat.author.userId]
        if self.sub_client.client.userId in admins:
            await self.sub_client.edit_chat(chatId=chatid, viewOnly=True)
            logger.info("Чат переведён в режим просмотра")
        else:
            logger.error("У вас нет прав помощника")

    async def set_view_mode_timer(self, chatid: str):
        duration = int(input("Длительность в секундах: "))
        chat = await self.sub_client.get_chat_thread(chatId=chatid)
        admins = [*chat.coHosts, chat.author.userId]
        if self.sub_client.client.userId in admins:
            await self.sub_client.edit_chat(chatId=chatid, viewOnly=True)
            logger.info("Чат переведён в режим просмотра")
            while duration > 0:
                logger.info(f"Осталось {duration} секунд")
                duration -= 1
                time.sleep(1)
            await self.sub_client.edit_chat(chatId=chatid, viewOnly=False)
            logger.info("Режим просмотра отключён")
        else:
            logger.error("У вас нет прав помощника")
