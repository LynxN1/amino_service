import asyncio
import os
import pathlib
import random
import traceback

from prettytable import from_db_cursor
from termcolor import colored

import amino_async
from src.utils import configs, database
from src.utils.configs import ICONS_PATH, BOTS_MANAGEMENT_MENU, CATEGORY_NAMES, CHOICE_ACTION_TEXT
from src.utils.logger import service_align, logger, file_logger
from src.utils.login import login_sid, check_accounts
from src.utils.nick_gen import UsernameGenerator
from src.utils.table import create_table


class TaskManager:
    async def play_lottery_task(self, account: tuple, com_id: str):
        email = account[0]
        client = await login_sid(account)
        if not client:
            return 0
        try:
            sub_client = amino_async.SubClient(comId=com_id, client=client)
            play = await sub_client.lottery()
            award = play.awardValue if play.awardValue else 0
            service_align(email, f"+{award} АМ")
            return int(award)
        except Exception as e:
            service_align(email, e.args[0]["api:message"], level="error")
            return 0
        finally:
            await client.session.close()

    async def send_coins_task(self, account: tuple, object_id: str, com_id: str):
        email = account[0]
        client = await login_sid(account)
        if not client:
            return 0
        try:
            sub_client = amino_async.SubClient(comId=com_id, client=client)
            wallet_info = await client.get_wallet_info()
            coins = int(wallet_info.totalCoins)
            if coins != 0:
                await sub_client.send_coins(coins=coins, blogId=object_id)
                service_align(email, f"+{coins} АМ")
                return coins
            else:
                service_align(email, f"NotEnoughCoins")
        except Exception as e:
            service_align(email, e.args[0]["api:message"], level="error")
            return 0
        finally:
            await client.session.close()

    async def like_blog_task(self, account: tuple, object_id: str, com_id: str):
        email = account[0]
        client = await login_sid(account)
        if not client:
            return
        try:
            sub_client = amino_async.SubClient(comId=com_id, client=client)
            await sub_client.like_blog(blogId=object_id)
            service_align(email, "Лайк")
        except Exception as e:
            service_align(email, e.args[0]["api:message"], level="error")
            return
        finally:
            await client.session.close()

    async def join_bots_to_chat_task(self, account: tuple, object_id: str, com_id: str):
        email = account[0]
        client = await login_sid(account)
        if not client:
            return
        try:
            sub_client = amino_async.SubClient(comId=com_id, client=client)
            await sub_client.join_chat(chatId=object_id)
            service_align(email, "Зашел в чат")
        except Exception as e:
            service_align(email, e.args[0]["api:message"], level="error")
            return
        finally:
            await client.session.close()

    async def leave_bots_from_chat_task(self, account: tuple, object_id: str, com_id: str):
        email = account[0]
        client = await login_sid(account)
        if not client:
            return
        try:
            sub_client = amino_async.SubClient(comId=com_id, client=client)
            await sub_client.leave_chat(chatId=object_id)
            service_align(email, "Вышел из чата")
        except Exception as e:
            service_align(email, e.args[0]["api:message"], level="error")
            return
        finally:
            await client.session.close()

    async def join_bots_to_community_task(self, account: tuple, com_id: str, inv_id: str = None):
        email = account[0]
        client = await login_sid(account)
        if not client:
            return
        try:
            if inv_id:
                await client.join_community(comId=com_id, invitationId=inv_id)
                service_align(email, "Зашел в сообщество")
            if inv_id is None:
                await client.join_community(comId=com_id)
                service_align(email, "Зашел в сообщество")
        except Exception as e:
            service_align(email, e.args[0]["api:message"], level="error")
            return
        finally:
            await client.session.close()

    async def send_message_task(self, account: tuple, object_id: str, text: str, com_id: str):
        email = account[0]
        client = await login_sid(account)
        if not client:
            return
        try:
            sub_client = amino_async.SubClient(comId=com_id, client=client)
            await sub_client.send_message(chatId=object_id, message=text)
            service_align(email, "Отправил сообщение")
        except Exception as e:
            service_align(email, e.args[0]["api:message"], level="error")
            return
        finally:
            await client.session.close()

    async def follow_task(self, account: tuple, object_id: str, com_id: str):
        email = account[0]
        client = await login_sid(account)
        if not client:
            return
        try:
            sub_client = amino_async.SubClient(comId=com_id, client=client)
            await sub_client.follow(userId=object_id)
            service_align(email, "Подписался")
        except Exception as e:
            service_align(email, e.args[0]["api:message"], level="error")
            return
        finally:
            await client.session.close()

    async def unfollow_task(self, account: tuple, object_id: str, com_id: str):
        email = account[0]
        client = await login_sid(account)
        if not client:
            return
        try:
            sub_client = amino_async.SubClient(comId=com_id, client=client)
            await sub_client.unfollow(userId=object_id)
            service_align(email, "Отписался")
        except Exception as e:
            service_align(email, e.args[0]["api:message"], level="error")
            return
        finally:
            await client.session.close()

    async def start_chat_task(self, account: tuple, object_id: str, com_id: str):
        email = account[0]
        client = await login_sid(account)
        if not client:
            return
        try:
            sub_client = amino_async.SubClient(comId=com_id, client=client)
            await sub_client.start_chat(userId=object_id, message="")
            service_align(email, "Начал чат")
        except Exception as e:
            service_align(email, e.args[0]["api:message"], level="error")
            return
        finally:
            await client.session.close()

    async def change_nick_random_task(self, account: tuple, max_length, nick, com_id: str):
        email = account[0]
        client = await login_sid(account)
        if not client:
            return
        try:
            sub_client = amino_async.SubClient(comId=com_id, client=client)
            if nick is None:
                nick = UsernameGenerator(2, max_length).generate()
            await sub_client.edit_profile(nickname=nick)
            service_align(email, f"Ник изменён на {nick}")
        except Exception as e:
            service_align(email, e.args[0]["api:message"], level="error")
            return
        finally:
            await client.session.close()

    async def change_icon_random_task(self, account: tuple, images: list, com_id: str):
        email = account[0]
        client = await login_sid(account)
        if not client:
            return
        try:
            sub_client = amino_async.SubClient(comId=com_id, client=client)
            icon = client.upload_media(open(os.path.join(ICONS_PATH, f"{random.choice(images)}"), "rb"), "image")
            await sub_client.edit_profile(icon=icon)
            service_align(email, "Аватарка изменена")
        except Exception as e:
            service_align(email, e.args[0]["api:message"], level="error")
            return
        finally:
            await client.session.close()

    async def wall_comment_task(self, account: tuple, text: str, userid: str, com_id: str):
        email = account[0]
        client = await login_sid(account)
        if not client:
            return
        try:
            sub_client = amino_async.SubClient(comId=com_id, client=client)
            await sub_client.comment(message=text, userId=userid)
            service_align(email, "Комментарий отправлен")
        except Exception as e:
            service_align(email, e.args[0]["api:message"], level="error")
            return
        finally:
            await client.session.close()


class BotManagement(TaskManager):
    def __init__(self, sub_client: amino_async.SubClient):
        self.sub_client = sub_client
        self.com_id = self.sub_client.comId

    async def start(self):
        await check_accounts()
        bots = database.get_bots_cursor()
        if bots.rowcount <= 0:
            raise Exception("Не найдено ботов в базе данных")
        while True:
            try:
                logger.info(colored(create_table(CATEGORY_NAMES[1], BOTS_MANAGEMENT_MENU), "cyan"))
                choice = input(CHOICE_ACTION_TEXT)
                if choice == "s":
                    logger.info(from_db_cursor(bots))
                if choice == "d":
                    email = input("Почта бота: ")
                    database.remove_bot(email)
                    logger.info(f"{email} удален из базы данных")
                if choice == "1":
                    await self.play_lottery()
                if choice == "2":
                    await self.send_coins()
                if choice == "3":
                    await self.like_blog()
                if choice == "4":
                    await self.join_bots_to_chat()
                if choice == "5":
                    await self.leave_bots_from_chat()
                if choice == "6":
                    await self.join_bots_to_community()
                if choice == "7":
                    await self.send_message()
                if choice == "8":
                    await self.follow()
                if choice == "9":
                    await self.unfollow()
                if choice == "10":
                    await self.change_nick_random()
                if choice == "11":
                    await self.wall_comment()
                if choice == "12":
                    await self.change_icon_random()
                if choice == "13":
                    await self.start_chat()
                if choice == "b":
                    break
            except Exception as e:
                logger.error(str(e))
                file_logger.debug(traceback.format_exc())

    async def play_lottery(self):
        result = await asyncio.gather(*[asyncio.create_task(self.play_lottery_task(i, self.com_id)) for i in database.get_bots()])
        logger.info(f"Аккаунты: {len(result)}\nРезультат: +{sum(result)} АМ")

    async def send_coins(self):
        blog_link = input("Ссылка на пост: ")
        from_code = await self.sub_client.client.get_from_code(str(blog_link.split('/')[-1]))
        result = await asyncio.gather(*[asyncio.create_task(self.send_coins_task(i, from_code.objectId, self.com_id)) for i in database.get_bots()])
        logger.info(f"Аккаунты: {len(result)}\nРезультат: +{sum(result)} АМ")

    async def like_blog(self):
        blog_link = input("Ссылка на пост: ")
        from_code = await self.sub_client.client.get_from_code(str(blog_link.split('/')[-1]))
        await asyncio.gather(*[asyncio.create_task(self.like_blog_task(i, from_code.objectId, self.com_id)) for i in database.get_bots()])

    async def join_bots_to_chat(self):
        object_link = input("Ссылка: ")
        from_code = await self.sub_client.client.get_from_code(str(object_link.split('/')[-1]))
        await asyncio.gather(*[asyncio.create_task(self.join_bots_to_chat_task(i, from_code.objectId, self.com_id)) for i in database.get_bots()])

    async def leave_bots_from_chat(self):
        object_link = input("Ссылка: ")
        from_code = await self.sub_client.client.get_from_code(str(object_link.split('/')[-1]))
        await asyncio.gather(*[asyncio.create_task(self.leave_bots_from_chat_task(i, from_code.objectId, self.com_id)) for i in database.get_bots()])

    async def join_bots_to_community(self):
        subs = await self.sub_client.client.sub_clients(start=0, size=100)
        for x, com_name in enumerate(subs.name, 1):
            logger.info(f"{x}. {com_name}")
        object_id = subs.comId[int(input("Введите номер сообщества: ")) - 1]
        from_code = await self.sub_client.client.get_community_info(object_id)
        if from_code.joinType == 2:
            invite_link = input("Введите код/ссылка приглашения: ")
            inv_from_code = await self.sub_client.client.link_identify(code=str(invite_link.split("/")[-1]))
        else:
            inv_from_code = None
        await asyncio.gather(*[asyncio.create_task(self.join_bots_to_community_task(i, from_code.comId, inv_from_code.get("invitationId"))) for i in database.get_bots()])

    async def send_message(self):
        object_link = input("Ссылка: ")
        from_code = await self.sub_client.client.get_from_code(str(object_link.split('/')[-1]))
        text = input("Текст: ")
        await asyncio.gather(*[asyncio.create_task(self.send_message_task(i, from_code.objectId, text, self.com_id)) for i in database.get_bots()])

    async def follow(self):
        user_link = input("Ссылка на пользователя: ")
        from_code = await self.sub_client.client.get_from_code(str(user_link.split('/')[-1]))
        await asyncio.gather(*[asyncio.create_task(self.follow_task(i, from_code.objectId, self.com_id)) for i in database.get_bots()])

    async def unfollow(self):
        user_link = input("Ссылка на пользователя: ")
        from_code = await self.sub_client.client.get_from_code(str(user_link.split('/')[-1]))
        await asyncio.gather(*[asyncio.create_task(self.unfollow_task(i, from_code.objectId, self.com_id)) for i in database.get_bots()])

    async def start_chat(self):
        object_link = input("Ссылка на пользователя: ")
        from_code = await self.sub_client.client.get_from_code(str(object_link.split('/')[-1]))
        await asyncio.gather(*[asyncio.create_task(self.start_chat_task(i, from_code.objectId, self.com_id)) for i in database.get_bots()])

    async def change_nick_random(self):
        logger.info("1 - Рандомный ник")
        logger.info("2 - Ввести свой никнейм")
        mode = input("Select mode: ")
        if mode == "1":
            max_length = int(input("Максимальная длина ника: "))
            await asyncio.gather(*[asyncio.create_task(self.change_nick_random_task(i, max_length, None, self.com_id)) for i in database.get_bots()])
        else:
            nick = input("Введите ник: ")
            await asyncio.gather(*[asyncio.create_task(self.change_nick_random_task(i, None, nick, self.com_id)) for i in database.get_bots()])

    async def change_icon_random(self):
        current_directory = pathlib.Path(configs.ICONS_PATH)
        images = [x.name for x in current_directory.iterdir()]
        if images:
            await asyncio.gather(*[asyncio.create_task(self.change_icon_random_task(i, images, self.com_id)) for i in database.get_bots()])
        else:
            logger.error("icons пустой")

    async def wall_comment(self):
        user_link = input("Ссылка на пользователя: ")
        from_code = await self.sub_client.client.get_from_code(str(user_link.split('/')[-1]))
        text = input("Текст: ")
        await asyncio.gather(*[asyncio.create_task(self.wall_comment_task(i, text, from_code.objectId, self.com_id)) for i in database.get_bots()])
