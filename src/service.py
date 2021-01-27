import os
import amino
import json
import yaml
import random
import threading
import time
import traceback
from sys import platform
from multiprocessing import Pool, cpu_count
from multiprocessing.pool import ThreadPool
from termcolor import colored


def get_accounts():
    with open(os.getcwd() + "/src/accounts/bots.yaml", "r") as accounts_file:
        return yaml.load(accounts_file.read(), Loader=yaml.Loader)


def get_comments():
    with open(os.getcwd() + "/src/activity/comments.txt", "r", encoding="utf-8") as comments_file:
        return comments_file.readlines()


def get_devices():
    with open(os.getcwd() + "/src/devices/devices.txt", "r") as devices_file:
        return devices_file.readlines()


def set_bots():
    accounts = []
    with open(os.getcwd() + "/src/accounts/bots.txt", "r") as bots_file:
        bots = bots_file.readlines()
    for account in bots:
        split = account.split(":")
        email = split[0].replace("\n", "")
        password = split[1].replace("\n", "")
        accounts.append({"email": email, "password": password})
    with open(os.getcwd() + "/src/accounts/bots.yaml", "w") as accounts_file:
        yaml.dump(accounts, accounts_file, Dumper=yaml.Dumper)
    print("Ready!")


def get_count(values: list):
    total_count = 0
    for i in values:
        if type(i) == int:
            total_count += i
    return total_count


class Login:
    def __init__(self):
        self.accounts = get_accounts()
        self.client = amino.Client()

    def login(self, email: str):
        while True:
            password = self.get_password(email)
            try:
                print(f"Authorization {email}...")
                self.client.login(email=email, password=password)
                print("Authorization was successful")
                self.save_auth_data(email, password)
                return self.client
            except amino.exceptions.ActionNotAllowed:
                self.client.device_id = random.choice(get_devices()).replace("\n", "")
            except amino.exceptions.FailedLogin:
                print(f"[{email}]: Failed Login")
            except amino.exceptions.InvalidAccountOrPassword:
                print(f"[{email}]: Invalid account or password.")
            except amino.exceptions.InvalidPassword:
                print(f"[{email}]: Invalid Password")
            except amino.exceptions.InvalidEmail:
                print(f"[{email}]: Invalid Email")
            except amino.exceptions.AccountDoesntExist:
                print(f"[{email}]: Account does not exist")
            except amino.exceptions.VerificationRequired as verify:
                print(f"[Confirm your account]: {verify}")

    def check_accounts(self):
        print("Checking accounts...")
        bad_accounts = []
        for i in self.accounts:
            if i.get("sid") is None:
                bad_accounts.append(self.accounts.index(i))
        if len(bad_accounts) > 0:
            print(f"{len(bad_accounts)} bad accounts detected. Starting fix...")
            pool = ThreadPool(10)
            pool.map(self.set_sid, bad_accounts)
            with open("src/accounts/bots.yaml", "w") as accounts_file:
                yaml.dump(self.accounts, accounts_file, Dumper=yaml.Dumper)
            bad_accounts.clear()

    def update_sid(self):
        print("Starting update...")
        pool = ThreadPool(10)
        indexes = []
        for i in range(len(self.accounts)):
            indexes.append(i)
        pool.map(self.set_sid, indexes)
        with open("src/accounts/bots.yaml", "w") as accounts_file:
            yaml.dump(self.accounts, accounts_file, Dumper=yaml.Dumper)

    def set_sid(self, index: int):
        client = amino.Client()
        email = self.accounts[index].get("email")
        password = self.accounts[index].get("password")
        client.device_id = random.choice(get_devices()).replace("\n", "")
        while True:
            try:
                client.login(email, password)
                print(Log().align(email, "SID updated"))
                self.accounts[index]["sid"] = client.sid
                break
            except amino.exceptions.ActionNotAllowed:
                print(Log().align(email, "device_id updated"))
                client.device_id = random.choice(get_devices()).replace("\n", "")
            except amino.exceptions.FailedLogin:
                print(Log().align(email, "Failed login"))
                return
            except amino.exceptions.InvalidAccountOrPassword:
                print(Log().align(email, "Invalid account or password"))
                return
            except amino.exceptions.InvalidPassword:
                print(Log().align(email, "Invalid Password"))
                return
            except amino.exceptions.InvalidEmail:
                print(Log().align(email, "Invalid Email"))
                return
            except amino.exceptions.AccountDoesntExist:
                print(Log().align(email, "Account does not exist"))
                return
            except amino.exceptions.VerificationRequired as verify:
                print(Log().align(email, str(verify)))
                return

    def multilogin(self, account: dict):
        email = account.get("email")
        sid = account.get("sid")
        while True:
            try:
                self.client.login_sid(sid)
                return self.client
            except amino.exceptions.ActionNotAllowed:
                self.client.device_id = random.choice(get_devices()).replace("\n", "")
            except amino.exceptions.FailedLogin:
                print(Log().align(email, "Failed login"))
                return False
            except amino.exceptions.InvalidAccountOrPassword:
                print(Log().align(email, "Invalid account or password"))
                return False
            except amino.exceptions.InvalidPassword:
                print(Log().align(email, "Invalid Password"))
                return False
            except amino.exceptions.InvalidEmail:
                print(Log().align(email, "Invalid Email"))
                return False
            except amino.exceptions.AccountDoesntExist:
                print(Log().align(email, "Account does not exist"))
                return False
            except amino.exceptions.VerificationRequired as verify:
                print(Log().align(email, str(verify)))
                return False
            except amino.exceptions.InvalidSession:
                print(Log().align(email, "SID update required..."))
                return False

    def get_password(self, email: str):
        with open("src/auth/data.json", "r") as f:
            auth_data = json.load(f)
        try:
            password = auth_data[email]
            return password
        except (KeyError, IndexError, TypeError):
            password = input("Password: ")
            return password

    def save_auth_data(self, email: str, password: str):
        with open("src/auth/data.json", "r") as f:
            auth_data = json.load(f)
        with open("src/auth/data.json", "w") as f:
            auth_data.update({email: password})
            json.dump(auth_data, f, indent=2)


class Community:
    def __init__(self, client):
        self.client = client

    def select(self):
        sub_clients = self.client.sub_clients(start=0, size=100)
        print("Select the community:")
        for x, name in enumerate(sub_clients.name, 1):
            print(f"{x}. {name}")
        while True:
            choice_sub_client = input("Enter community number: ")
            try:
                return sub_clients.comId[int(choice_sub_client) - 1]
            except IndexError:
                print(colored("Invalid community number", "red"))

    def sub_client(self, com_id: str):
        sub_client = amino.SubClient(comId=com_id, profile=self.client.profile)
        return sub_client


class Threads:
    def __init__(self, client, com_id: str):
        self.sub_client = Community(client).sub_client(com_id)

    def select(self):
        get_chats = self.sub_client.get_chat_threads(start=0, size=100)
        chat_list = []
        x = 0
        print("Select the chat:")
        for name, thread_type, chatid in zip(get_chats.title, get_chats.type, get_chats.chatId):
            if thread_type != 0:
                x += 1
                print(f"{x}. {name}")
                chat_list.append(chatid)
        while True:
            choice_chat = input("Enter chat number: ")
            try:
                return chat_list[int(choice_chat) - 1]
            except IndexError:
                print(colored("Invalid chat number", "red"))


class Log:
    def align(self, text: str, action: str):
        spaces = 30 - len(text)
        text = f"[{text}"
        for _ in range(spaces):
            text += " "
        text += f"]: {action}"
        return text


class ServiceApp:
    def __init__(self):
        if platform in ["linux", "linux2", "linux3"]:
            self.pool_count = cpu_count()
        else:
            self.pool_count = len(get_accounts()) if len(get_accounts()) <= 10 else 10
        with open(os.getcwd() + "/src/auth/data.json", "r") as auth_file:
            auth_data = json.loads(auth_file.read())
            if auth_data:
                for email in auth_data.keys():
                    self.client = Login().login(email=email)
            else:
                self.client = Login().login(email=input("Email: "))
        self.com_id = Community(self.client).select()
        self.object_id = None
        self.text = None
        self.back = False

    def run(self):
        while True:
            try:
                print(colored(open("src/draw/management_choice.txt", "r").read(), "cyan"))
                management_choice = input("Enter the number >>> ")
                if management_choice == "0":
                    self.com_id = Community(self.client).select()
                elif management_choice == "1":
                    back = False
                    while not back:
                        print(colored(open("src/draw/account_management.txt", "r").read(), "cyan"))
                        choice = input("Enter the number >>> ")
                        if choice == "1":
                            quiz_link = input("Quiz link: ")
                            self.object_id = self.client.get_from_code(str(quiz_link.split('/')[-1])).objectId
                            self.play_quiz()
                            print("[PlayQuiz]: Finish.")
                        elif choice == "2":
                            self.unfollow()
                            print("[Unfollow]: Finish.")
                        elif choice == "3":
                            like_blogs = threading.Thread(target=self.like_recent_blogs)
                            like_blogs.start()
                            input("\nPress ENTER to stop...\n")
                            self.back = True
                            like_blogs.join()
                            self.back = False
                            print("[Activity]: Finish.")
                        elif choice == "b":
                            back = True
                elif management_choice == "2":
                    Login().check_accounts()
                    back = False
                    while not back:
                        print(colored(open("src/draw/bot_management.txt", "r").read(), "cyan"))
                        choice = input("Enter the number >>> ")
                        if choice == "0":
                            set_bots()
                            input("Changes saved. Please restart the program...")
                            exit(0)
                        elif choice == "1":
                            pool = Pool()
                            result = pool.map(self.play_lottery, get_accounts())
                            print(f"Result: +{get_count(result)} coins")
                            print("[PlayLottery]: Finish.")
                        elif choice == "2":
                            blog_link = input("Blog link: ")
                            self.object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            pool = Pool()
                            result = pool.map(self.send_coins, get_accounts())
                            print(f"Result: +{get_count(result)} coins")
                            print("[SendCoins]: Finish.")
                        elif choice == "3":
                            blog_link = input("Blog link: ")
                            self.object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            pool = Pool()
                            pool.map(self.like_blog, get_accounts())
                            print("[LikeBlog]: Finish.")
                        elif choice == "4":
                            self.object_id = Threads(self.client, self.com_id).select()
                            pool = Pool()
                            pool.map(self.join_bots_to_chat, get_accounts())
                            print("[JoinBotsToChat]: Finish.")
                        elif choice == "5":
                            self.object_id = Community(self.client).select()
                            pool = Pool()
                            pool.map(self.join_bots_to_community, get_accounts())
                            print("[JoinBotsToCommunity]: Finish.")
                        elif choice == "6":
                            self.object_id = Threads(self.client, self.com_id).select()
                            self.text = input("Message text: ")
                            pool = Pool()
                            pool.map(self.send_message, get_accounts())
                            print("[SendMessage]: Finish.")
                        elif choice == "7":
                            user_link = input("Link to user: ")
                            self.object_id = self.client.get_from_code(str(user_link.split('/')[-1])).objectId
                            pool = Pool()
                            pool.map(self.follow, get_accounts())
                            print("[Follow]: Finish.")
                        elif choice == "s":
                            Login().update_sid()
                            print("[UpdateSIDs]: Finish.")
                        elif choice == "b":
                            back = True
            except Exception:
                print(traceback.format_exc())

    def play_lottery(self, account: dict):
        email = account.get("email")
        client = Login().multilogin(account)
        if client is not False:
            sub_client = Community(client).sub_client(self.com_id)
            try:
                play = sub_client.lottery()
                award = play.awardValue if play.awardValue else 0
                return int(award)
            except amino.exceptions.AlreadyPlayedLottery:
                print(Log().align(email, "AlreadyPlayedLottery"))
            except amino.exceptions.YouAreBanned:
                print(Log().align(email, "You are banned"))
            except amino.exceptions.InvalidSession:
                print(Log().align(email, "SID update required..."))
            except Exception as e:
                print(Log().align(email, str(e)))

    def send_coins(self, account: dict):
        email = account.get("email")
        client = Login().multilogin(account)
        if client is not False:
            sub_client = Community(client).sub_client(self.com_id)
            coins = int(client.get_wallet_info().totalCoins)
            if coins != 0:
                try:
                    sub_client.send_coins(coins=coins, blogId=self.object_id)
                    print(Log().align(email, f"{coins} coins sent"))
                    return coins
                except amino.exceptions.NotEnoughCoins:
                    print(Log().align(email, "NotEnoughCoins"))
                except amino.exceptions.InvalidRequest:
                    print(Log().align(email, "InvalidRequest"))
                except amino.exceptions.YouAreBanned:
                    print(Log().align(email, "You are banned"))
                except amino.exceptions.InvalidSession:
                    print(Log().align(email, "SID update required..."))
                except Exception as e:
                    print(Log().align(email, str(e)))
            else:
                print(Log().align(email, "NotEnoughCoins"))

    def play_quiz(self):
        questions_list = []
        answers_list = []

        sub_client = Community(self.client).sub_client(self.com_id)
        quiz_info = sub_client.get_blog_info(quizId=self.object_id).json
        questions = quiz_info["blog"]["quizQuestionList"]
        total_questions = quiz_info["blog"]["extensions"]["quizTotalQuestionCount"]

        for x, question in enumerate(questions, 1):
            print(f"[quiz][{x}/{total_questions}]: Choosing the right answer...")
            question_id = question["quizQuestionId"]
            answers = question["extensions"]["quizQuestionOptList"]
            for answer in answers:
                answer_id = answer["optId"]
                sub_client.play_quiz(quizId=self.object_id, questionIdsList=[question_id], answerIdsList=[answer_id])
                latest_score = sub_client.get_quiz_rankings(quizId=self.object_id).profile.latestScore
                if latest_score > 0:
                    print(f"[quiz][{x}/{total_questions}]: Answer found!")
                    questions_list.append(question_id)
                    answers_list.append(answer_id)
        for i in range(2):
            try:
                sub_client.play_quiz(quizId=self.object_id, questionIdsList=questions_list, answerIdsList=answers_list,
                                     quizMode=i)
            except amino.exceptions.InvalidRequest:
                pass
        print(f"[quiz]: Passed the quiz!")
        print(f"[quiz]: Score: {sub_client.get_quiz_rankings(quizId=self.object_id).profile.highestScore}")

    def like_blog(self, account: dict):
        email = account.get("email")
        client = Login().multilogin(account)
        if client is not False:
            sub_client = Community(client).sub_client(self.com_id)
            try:
                sub_client.like_blog(blogId=self.object_id)
                print(Log().align(email, "Like"))
            except amino.exceptions.RequestedNoLongerExists:
                sub_client.like_blog(wikiId=self.object_id)
                print(Log().align(email, "Like"))
            except amino.exceptions.YouAreBanned:
                print(Log().align(email, "You are banned"))
            except amino.exceptions.InvalidSession:
                print(Log().align(email, "SID update required..."))
            except Exception as e:
                print(Log().align(email, str(e)))

    def unfollow(self):
        sub_client = Community(self.client).sub_client(self.com_id)
        back = False
        iteration = 0
        while not back:
            for i in range(0, 2000, 100):
                followings = sub_client.get_user_following(userId=self.client.userId, start=i, size=100)
                if len(followings.userId) == 0:
                    back = True
                else:
                    for user_id in followings.userId:
                        iteration += 1
                        print(f"[{iteration}]: Unfollow")
                        sub_client.unfollow(userId=user_id)

    def like_recent_blogs(self):
        comments = get_comments()
        subclient = amino.SubClient(comId=self.com_id, profile=self.client.profile)
        old_blogs = []
        while not self.back:
            print("Get recent blogs")
            recent_blogs = subclient.get_recent_blogs(start=0, size=100)
            for blog_id, blog_type in zip(recent_blogs.blog.blogId, recent_blogs.blog.type):
                if blog_id not in old_blogs:
                    try:
                        subclient.like_blog(blogId=blog_id)
                        if len(comments) > 0:
                            subclient.comment(message=random.choice(comments), blogId=blog_id)
                        time.sleep(2.5)
                    except amino.exceptions.RequestedNoLongerExists:
                        subclient.like_blog(wikiId=blog_id)
                        if len(comments) > 0:
                            subclient.comment(message=random.choice(comments), wikiId=blog_id)
                        time.sleep(2.5)
                    print("Like")
                    old_blogs.append(blog_id)
            time.sleep(5)

    def join_bots_to_chat(self, account: dict):
        email = account.get("email")
        client = Login().multilogin(account)
        if client is not False:
            sub_client = Community(client).sub_client(self.com_id)
            try:
                sub_client.join_chat(chatId=self.object_id)
                print(Log().align(email, "Join"))
            except amino.exceptions.YouAreBanned:
                print(Log().align(email, "You are banned"))
            except amino.exceptions.RemovedFromChat:
                print(Log().align(email, "You are removed from this chatroom"))
            except amino.exceptions.InvalidSession:
                print(Log().align(email, "SID update required..."))
            except Exception as e:
                print(Log().align(email, str(e)))

    def join_bots_to_community(self, account: dict):
        email = account.get("email")
        client = Login().multilogin(account)
        if client is not False:
            try:
                client.join_community(comId=self.object_id)
                print(Log().align(email, "Join"))
            except amino.exceptions.InvalidSession:
                print(Log().align(email, "SID update required..."))
            except Exception as e:
                print(Log().align(email, str(e)))

    def send_message(self, account: dict):
        email = account.get("email")
        client = Login().multilogin(account)
        if client is not False:
            sub_client = Community(client).sub_client(self.com_id)
            try:
                sub_client.send_message(chatId=self.object_id, message=self.text)
                print(Log().align(email, "Send"))
            except amino.exceptions.YouAreBanned:
                print(Log().align(email, "You are banned"))
            except amino.exceptions.RemovedFromChat:
                print(Log().align(email, "You are removed from this chatroom"))
            except amino.exceptions.ChatViewOnly:
                print(Log().align(email, "Chat in view only mode"))
            except amino.exceptions.AccessDenied:
                print(Log().align(email, "Access denied"))
            except amino.exceptions.InvalidSession:
                print(Log().align(email, "SID update required..."))
            except Exception as e:
                print(Log().align(email, str(e)))

    def follow(self, account: dict):
        email = account.get("email")
        client = Login().multilogin(account)
        if client is not False:
            sub_client = Community(client).sub_client(self.com_id)
            try:
                sub_client.follow(userId=self.object_id)
                print(Log().align(email, "Follow"))
            except amino.exceptions.YouAreBanned:
                print(Log().align(email, "You are banned"))
            except amino.exceptions.AccessDenied:
                print(Log().align(email, "Access denied"))
            except amino.exceptions.BlockedByUser:
                print(Log().align(email, "You are blocked by this user"))
            except amino.exceptions.InvalidSession:
                print(Log().align(email, "SID update required..."))
            except Exception as e:
                print(Log().align(email, str(e)))
