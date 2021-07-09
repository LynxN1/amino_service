import asyncio
import datetime
import os
import time
import traceback
from collections import OrderedDict

from tabulate import tabulate
from termcolor import colored

from src.utils import get_chat_id, logger, file_logger
from src import configs, amino_async


class ChatModeration:
    def __init__(self, sub_client: amino_async.SubClient):
        self.sub_client = sub_client

    async def start(self):
        while True:
            try:
                logger.info(colored(tabulate(
                    configs.CHAT_MODERATION_MENU,
                    headers=[configs.CATEGORY_NAMES[2]],
                    tablefmt="fancy_grid"
                ), "cyan"))
                choice = input(configs.CHOICE_ACTION_TEXT)
                if choice == "1":
                    await self.clear_chat(await get_chat_id(self.sub_client))
                if choice == "2":
                    await self.save_chat_settings(await get_chat_id(self.sub_client))
                if choice == "3":
                    await self.set_view_mode(await get_chat_id(self.sub_client))
                if choice == "4":
                    await self.set_view_mode_timer(await get_chat_id(self.sub_client))
                if choice == "5":
                    await self.check_stats(await get_chat_id(self.sub_client))
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
        if not os.path.exists(configs.CHAT_SETTINGS_PATH):
            os.mkdir(configs.CHAT_SETTINGS_PATH)
        with open(os.path.join(configs.CHAT_SETTINGS_PATH, f"{chatid}.txt"), "w", encoding="utf-8") as settings_file:
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
        logger.info(f"Настройки сохранены по этому пути: {os.path.join(configs.CHAT_SETTINGS_PATH, f'{chatid}.txt')}")

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

    async def check_stats(self, chatid: str):
        days_count = int(input("Количество дней(1-30): "))
        if 1 <= days_count <= 30:
            days = datetime.timedelta(days_count)
            tokens = []
            stats = {}
            rows = []
            back = False
            page_token = None
            logger.info(f"Анализ активности чата за {days_count} дней...")
            while not back:
                messages = await self.sub_client.get_chat_messages(chatId=chatid, pageToken=page_token, size=100)
                page_token = messages.nextPageToken
                for message_id, created_time, nick, media_type, user_id in zip(messages.messageId, messages.createdTime,
                                                                               messages.author.nickname,
                                                                               messages.mediaType, messages.author.userId):
                    if datetime.datetime.strptime(created_time, "%Y-%m-%dT%H:%M:%SZ").date() <= datetime.date(
                            datetime.datetime.today().year, datetime.datetime.today().month,
                            datetime.datetime.today().day) - days or page_token in tokens:
                        back = True
                    else:
                        short_nick = nick[0:20]
                        if stats.get(short_nick) is None:
                            stats[short_nick] = {"messages": 1, "media": 0, "voices": 0, "stickers": 0}
                            if media_type == 113:
                                stats[short_nick]["stickers"] += 1
                            elif media_type == 110:
                                stats[short_nick]["voices"] += 1
                            elif media_type == 100:
                                stats[short_nick]["media"] += 1
                        else:
                            stats[short_nick]["messages"] += 1
                            if media_type == 113:
                                stats[short_nick]["stickers"] += 1
                            elif media_type == 110:
                                stats[short_nick]["voices"] += 1
                            elif media_type == 100:
                                stats[short_nick]["media"] += 1
                tokens.append(page_token)
            sorted_stats = OrderedDict(sorted(stats.items(), key=lambda z: z[1]["messages"], reverse=True))
            for x, i in enumerate(sorted_stats.items(), 1):
                messages = i[1].get("messages")
                media = i[1].get("media") / messages * 100
                stickers = i[1].get("stickers") / messages * 100
                voices = i[1].get("voices") / messages * 100
                rows.append([x, str(i[0]), int(messages), f"{media:.2f}%", f"{stickers:.2f}%", f"{voices:.2f}%"])
            from tabulate import tabulate
            logger.info(tabulate(rows, headers=["№", "Никнейм", "Кол-во сообщений", "Изображения", "Стикеры", "Голосовые"], tablefmt="fancy_grid"))
        else:
            logger.warning("Количество дней должно быть в пределах от 1 до 30")
