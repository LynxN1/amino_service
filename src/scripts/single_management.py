import asyncio
import random
import traceback

from termcolor import colored

import amino_async
from src.utils.configs import MAIN_ACCOUNT_MENU, CATEGORY_NAMES, CHOICE_ACTION_TEXT
from src.utils.logger import logger, file_logger
from src.utils.table import create_table


class SingleManagement:
    def __init__(self, sub_client: amino_async.SubClient):
        self.sub_client = sub_client

    async def start(self):
        while True:
            try:
                logger.info(colored(create_table(CATEGORY_NAMES[0], MAIN_ACCOUNT_MENU), "cyan"))
                choice = input(CHOICE_ACTION_TEXT)
                if choice == "1":
                    await self.play_quiz()
                if choice == "2":
                    await self.like_recent_blogs()
                if choice == "3":
                    await self.follow_all()
                if choice == "4":
                    await self.unfollow_all()
                if choice == "5":
                    await self.get_blocker_users()
                if choice == "6":
                    await self.send_coins()
                if choice == "b":
                    break
            except Exception as e:
                logger.error(str(e))
                file_logger.debug(traceback.format_exc())

    async def play_quiz(self):
        quiz_link = input("Ссылка на викторину: ")
        from_code = await self.sub_client.client.get_from_code(str(quiz_link.split('/')[-1]))
        object_id = from_code.objectId

        questions_list = []
        answers_list = []

        try:
            quiz_info = await self.sub_client.get_blog_info(quizId=object_id)
            questions = quiz_info.json["blog"]["quizQuestionList"]
            total_questions = quiz_info.json["blog"]["extensions"]["quizTotalQuestionCount"]

            for x, question in enumerate(questions, 1):
                logger.info(f"[{x}/{total_questions}]: Поиск ответа...")
                question_id = question["quizQuestionId"]
                answers = question["extensions"]["quizQuestionOptList"]
                for answer in answers:
                    answer_id = answer["optId"]
                    await self.sub_client.play_quiz(quizId=object_id, questionIdsList=[question_id], answerIdsList=[answer_id])
                    latest_score = await self.sub_client.get_quiz_rankings(quizId=object_id)
                    if latest_score.profile.latestScore > 0:
                        logger.info(f"[{x}/{total_questions}]: Ответ найден")
                        questions_list.append(question_id)
                        answers_list.append(answer_id)
            for i in range(2):
                try:
                    await self.sub_client.play_quiz(quizId=object_id, questionIdsList=questions_list, answerIdsList=answers_list, quizMode=i)
                except:
                    pass
            logger.info(f"[quiz]: Викторина пройдена!")
            final_score = await self.sub_client.get_quiz_rankings(quizId=object_id)
            logger.info(f"[quiz]: Счёт: {final_score.profile.highestScore}")
        except Exception as e:
            logger.error(e.args[0]["api:message"])
            return

    async def unfollow_all(self):
        try:
            for x in range(0, 100000, 100):
                followings = await self.sub_client.get_user_following(userId=self.sub_client.client.userId, start=x, size=100)
                if not followings.userId:
                    break
                await asyncio.gather(*[asyncio.create_task(self.sub_client.unfollow(i)) for i in followings.userId])
        except Exception as e:
            logger.error(e.args[0]["api:message"])
            return

    async def like_recent_blogs(self):
        comments = []
        x = 0
        try:
            while True:
                x += 1
                comment = input(f"[{x}]Введите текст комментария (нажмите ENTER чтобы пропустить): ")
                if comment:
                    comments.append(comment)
                if not comment:
                    break
            count = 0
            old = []
            token = None
            for x in range(0, 100000, 100):
                blogs = await self.sub_client.get_recent_blogs(pageToken=token, start=x, size=100)
                token = blogs.nextPageToken
                if token in old:
                    break
                old.append(token)
                for blog_id in blogs.blogId:
                    if blog_id in old:
                        continue
                    old.append(blog_id)
                    try:
                        await self.sub_client.like_blog(blogId=blog_id)
                        count += 1
                        logger.info(f"Лайкнуто {count} постов")
                        await self.sub_client.comment(blogId=blog_id, message=random.choice(comments))
                    except:
                        pass
        except Exception as e:
            logger.error(e.args[0]["api:message"])
            return

    async def follow_all(self):
        old = []
        count = 0
        try:
            for i in range(0, 20000, 100):
                recent_users = await self.sub_client.get_all_users(type="recent", start=i, size=100)
                users = [*recent_users.profile.userId]
                if not users:
                    break
                await asyncio.gather(*[asyncio.create_task(self.sub_client.follow(i)) for i in users])
                count += len(users)
                logger.info(f"Подписано на {count} пользователей")
            for i in range(0, 20000, 100):
                online_users = await self.sub_client.get_online_users(start=i, size=100)
                users = [*online_users.profile.userId]
                if not users:
                    break
                await asyncio.gather(*[asyncio.create_task(self.sub_client.follow(i)) for i in users])
                count += len(users)
                logger.info(f"Подписано на {count} пользователей")
            for i in range(0, 20000, 100):
                banned_users = await self.sub_client.get_all_users(type="banned", start=i, size=100)
                users = [*banned_users.profile.userId]
                if not users:
                    break
                await asyncio.gather(*[asyncio.create_task(self.sub_client.follow(i)) for i in users])
                count += len(users)
                logger.info(f"Подписано на {count} пользователей")
            for i in range(0, 20000, 100):
                chats = await self.sub_client.get_public_chat_threads(type="recommended", start=i, size=100)
                if not chats:
                    break
                for chatid in chats.chatId:
                    for x in range(0, 1000, 100):
                        users = await self.sub_client.get_chat_users(chatId=chatid, start=x, size=100)
                        users_list = users.userId
                        if not users_list:
                            break
                        for userid in old:
                            if userid in users_list:
                                users_list.remove(userid)
                        await asyncio.gather(*[asyncio.create_task(self.sub_client.follow(i)) for i in users_list])
                        count += len(users_list)
                        logger.info(f"Подписано на {count} пользователей")
        except Exception as e:
            logger.error(e.args[0]["api:message"])
            return

    async def get_blocker_users(self):
        try:
            users = await self.sub_client.get_blocker_users(start=0, size=100)
            if not users:
                return
            for i in users:
                user = await self.sub_client.get_user_info(i)
                logger.info(f"Userid: {i}")
                logger.info(f"Nickname: {user.nickname}")
                logger.info("")
        except Exception as e:
            logger.error(e.args[0]["api:message"])
            return

    async def send_coins(self):
        count = int(input("Количество монет: "))
        blog_link = input("Ссылка на пост: ")
        from_code = await self.sub_client.client.get_from_code(str(blog_link.split('/')[-1]))
        blog_id = from_code.objectId
        try:
            if count <= 500:
                await self.sub_client.send_coins(coins=count, blogId=blog_id)
                logger.info(f"Отправлено {count} монет")
            else:
                await asyncio.gather(*[asyncio.create_task(self.sub_client.send_coins(500, blog_id)) for _ in range(int(count / 500))])
                if count % 500 >= 1:
                    await self.sub_client.send_coins(coins=count % 500, blogId=blog_id)
        except Exception as e:
            logger.error(e.args[0]["api:message"])
            return
