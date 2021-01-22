import os
import amino
import json
import random
import threading
import time
import traceback
from multiprocessing import Pool
from termcolor import colored


def get_accounts():
    with open(os.getcwd() + "/src/accounts/bots.json", "r") as accounts_file:
        return json.loads(accounts_file.read())


def get_comments():
    with open(os.getcwd() + "/src/activity/comments.txt", "r", encoding="utf-8") as comments_file:
        return comments_file.readlines()


def get_devices():
    with open(os.getcwd() + "/src/devices/devices.txt", "r") as devices_file:
        return devices_file.readlines()


class Login:
    def __init__(self, email: str = None, account: dict = None):
        self.client = amino.Client()
        self.devices = get_devices()
        self.accounts = get_accounts()
        if email:
            self.email = email
        elif account:
            self.email = account.get("email")
            self.password = account.get("password")
            self.sid = account.get("sid")
        else:
            pass

    def login(self):
        while True:
            password = self.get_password()
            try:
                print(f"Authorization {self.email}...")
                self.client.login(email=self.email, password=password)
                print("Authorization was successful")
                self.save_auth_data(password)
                return self.client
            except amino.exceptions.ActionNotAllowed:
                self.client.device_id = random.choice(self.devices).replace("\n", "")
            except amino.exceptions.FailedLogin:
                print(f"[{self.email}]: Failed Login")
            except amino.exceptions.InvalidAccountOrPassword:
                print(f"[{self.email}]: Invalid account or password.")
            except amino.exceptions.InvalidPassword:
                print(f"[{self.email}]: Invalid Password")
            except amino.exceptions.InvalidEmail:
                print(f"[{self.email}]: Invalid Email")
            except amino.exceptions.AccountDoesntExist:
                print(f"[{self.email}]: Account does not exist")
            except amino.exceptions.VerificationRequired as verify:
                print(f"[Confirm your account]: {verify}")

    def multilogin(self):
        if self.sid is None:
            while True:
                try:
                    index = self.accounts.index({"email": self.email, "password": self.password})
                    self.client.login(email=self.email, password=self.password)
                    self.sid = self.client.sid
                    self.save_sid(index)
                    return self.client
                except amino.exceptions.ActionNotAllowed:
                    self.client.device_id = random.choice(self.devices).replace("\n", "")
                except amino.exceptions.FailedLogin:
                    print(f"[{self.email}]: Failed Login")
                    return False
                except amino.exceptions.InvalidAccountOrPassword:
                    print(f"[{self.email}]: Invalid account or password.")
                    return False
                except amino.exceptions.InvalidPassword:
                    print(f"[{self.email}]: Invalid Password")
                    return False
                except amino.exceptions.InvalidEmail:
                    print(f"[{self.email}]: Invalid Email")
                    return False
                except amino.exceptions.AccountDoesntExist:
                    print(f"[{self.email}]: Account does not exist")
                    return False
                except amino.exceptions.VerificationRequired as verify:
                    print(verify)
                    input("Confirm your account and press ENTER...")
        else:
            while True:
                try:
                    self.client.login_sid(self.sid)
                    return self.client
                except amino.exceptions.ActionNotAllowed:
                    self.client.device_id = random.choice(self.devices).replace("\n", "")
                except amino.exceptions.FailedLogin:
                    print(f"[{self.email}]: Failed Login")
                    return False
                except amino.exceptions.InvalidAccountOrPassword:
                    print(f"[{self.email}]: Invalid account or password.")
                    return False
                except amino.exceptions.InvalidPassword:
                    print(f"[{self.email}]: Invalid Password")
                    return False
                except amino.exceptions.InvalidEmail:
                    print(f"[{self.email}]: Invalid Email")
                    return False
                except amino.exceptions.AccountDoesntExist:
                    print(f"[{self.email}]: Account does not exist")
                    return False
                except amino.exceptions.VerificationRequired as verify:
                    print(verify)
                    input("Confirm your account and press ENTER...")
                except amino.exceptions.InvalidSession:
                    index = self.accounts.index({"email": self.email, "password": self.password})
                    self.client.device_id = random.choice(self.devices).replace("\n", "")
                    self.client.login(email=self.email, password=self.password)
                    self.sid = self.client.sid
                    self.save_sid(index)

    def save_sid(self, index: int):
        with open("src/accounts/bots.json", "r") as accounts_file:
            data = json.loads(accounts_file.read())
        data[index]["sid"] = self.client.sid
        with open("src/accounts/bots.json", "w") as accounts_file:
            json.dump(data, accounts_file, indent=2)

    def get_password(self):
        with open("src/auth/data.json", "r") as f:
            auth_data = json.load(f)
        try:
            password = auth_data[self.email]
            return password
        except (KeyError, IndexError, TypeError):
            password = input("Password: ")
            return password

    def save_auth_data(self, password: str):
        with open("src/auth/data.json", "r") as f:
            auth_data = json.load(f)
        with open("src/auth/data.json", "w") as f:
            auth_data.update({self.email: password})
            json.dump(auth_data, f, indent=2)


class Community:
    def __init__(self, client):
        self.client = client

    def select(self):
        sub_clients = self.client.sub_clients(start=0, size=100)
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
        chats = self.sub_client.get_chat_threads(start=0, size=100)
        x = 0
        for name, thread_type in zip(chats.title, chats.type):
            if thread_type != 0:
                x += 1
                print(f"{x}. {name}")
        choice_chat = input("\nEnter chat number: ")
        return chats.chatId[int(choice_chat) - 1]


class Log:
    def __init__(self, text: str):
        self.text = text

    def replace_code(self):
        if self.text == "200":
            self.text = "Success"
        return self.text


class ServiceApp:
    def __init__(self):
        self.accounts = get_accounts()
        self.pool_count = len(self.accounts) if len(self.accounts) <= 10 else 10
        self.client = Login(email=input("Email: ")).login()
        self.com_id = Community(self.client).select()
        self.object_id = None
        self.back = False

    def run(self):
        while True:
            self.accounts = get_accounts()
            try:
                logo = open("src/draw/menu.txt", "r").read()
                print(colored(logo, "cyan"))
                choice = input("Enter the number >>> ")
                if choice == "1":
                    pool = Pool(self.pool_count)
                    pool.map(self.play_lottery, self.accounts)
                    print("[PlayLottery]: Finish.")
                elif choice == "2":
                    blog_link = input("Blog link: ")
                    self.object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                    pool = Pool(self.pool_count)
                    pool.map(self.send_coins, self.accounts)
                    print("[SendCoins]: Finish.")
                elif choice == "3":
                    quiz_link = input("Quiz link: ")
                    self.object_id = self.client.get_from_code(str(quiz_link.split('/')[-1])).objectId
                    self.play_quiz()
                    print("[PlayQuiz]: Finish.")
                elif choice == "4":
                    blog_link = input("Blog link: ")
                    self.object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                    pool = Pool(self.pool_count)
                    pool.map(self.like_blog, self.accounts)
                    print("[LikeBlog]: Finish.")
                elif choice == "5":
                    self.unfollow()
                    print("[Unfollow]: Finish.")
                elif choice == "6":
                    like_blogs = threading.Thread(target=self.like_recent_blogs)
                    like_blogs.start()
                    input("\nPress ENTER to stop...\n")
                    self.back = True
                    like_blogs.join()
                    self.back = False
                    print("[Activity]: Finish.")
                elif choice == "7":
                    self.object_id = Threads(self.client, self.com_id).select()
                    pool = Pool(self.pool_count)
                    pool.map(self.join_bots_to_chat, self.accounts)
                    print("[JoinBotsToChat]: Finish.")
                elif choice == "8":
                    self.object_id = Community(self.client).select()
                    pool = Pool(self.pool_count)
                    pool.map(self.join_bots_to_community, self.accounts)
                    print("[JoinBotsToCommunity]: Finish.")
                elif choice == "0":
                    self.com_id = Community(self.client).select()
                    print("Community changed")
            except Exception:
                print(traceback.format_exc())

    def play_lottery(self, account: dict):
        email = account.get("email")
        self.client = Login(account=account).multilogin()
        if self.client is not False:
            sub_client = Community(self.client).sub_client(self.com_id)

            try:
                sub_client.lottery()
            except amino.exceptions.AlreadyPlayedLottery:
                print(f"[{email}]: AlreadyPlayedLottery")
            except Exception as e:
                print(f"[{email}][Exception]:\n{e}")

    def send_coins(self, account: dict):
        email = account.get("email")
        self.client = Login(account=account).multilogin()
        if self.client is not False:
            sub_client = Community(self.client).sub_client(self.com_id)
            coins = int(self.client.get_wallet_info().totalCoins)
            if coins != 0:
                try:
                    sub_client.send_coins(coins=coins, blogId=self.object_id)
                    print(f"[{email}][send_coins]: {coins}")
                except amino.exceptions.NotEnoughCoins:
                    print(f"[{email}][NotEnoughCoins][coins {coins}]")
                    return
                except amino.exceptions.InvalidRequest:
                    print(f"[{email}][InvalidRequest][coins {coins}]")
                    return
                print(f"[{email}]: {coins} монет отправлено.")
            else:
                print(f"[{email}][NotEnoughCoins]")

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
                sub_client.play_quiz(quizId=self.object_id, questionIdsList=questions_list, answerIdsList=answers_list, quizMode=i)
            except amino.exceptions.InvalidRequest:
                pass
        print(f"[quiz]: Passed the quiz!")
        print(f"[quiz]: Score: {sub_client.get_quiz_rankings(quizId=self.object_id).profile.highestScore}")

    def like_blog(self, account: dict):
        email = account.get("email")
        self.client = Login(account=account).multilogin()
        if self.client is not False:
            sub_client = Community(self.client).sub_client(self.com_id)
            try:
                print(f"[{email}][like]: {Log(str(sub_client.like_blog(blogId=self.object_id))).replace_code()}")
            except amino.exceptions.RequestedNoLongerExists:
                print(f"[{email}][like]: {Log(str(sub_client.like_blog(wikiId=self.object_id))).replace_code()}")

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
        self.client = Login(account=account).multilogin()
        if self.client is not False:
            sub_client = Community(self.client).sub_client(self.com_id)
            print(f"[{email}][Join to chat]: {Log(str(sub_client.join_chat(chatId=self.object_id))).replace_code()}")

    def join_bots_to_community(self, account: dict):
        email = account.get("email")
        self.client = Login(account=account).multilogin()
        if self.client is not False:
            print(f"[{email}][Join to community]: {Log(str(self.client.join_community(comId=self.object_id))).replace_code()}")
