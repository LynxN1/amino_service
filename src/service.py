import amino
import json
import os
import random
import threading
import time
import traceback
from multiprocessing import Pool
from pathlib import Path
from termcolor import colored

with open(os.getcwd() + "/src/devices/devices.txt", "r") as file:
    devices = file.readlines()

with open(os.getcwd() + "/src/activity/comments.txt", "r") as comments_file:
    comments = comments_file.readlines()

accounts = json.loads(Path(os.getcwd() + '/src/accounts/bots.json').read_text(encoding='utf-8'))


class Login:
    def __init__(self, email: str):
        self.client = amino.Client()
        self.email = email

    def login(self):
        while True:
            password = self.get_password()
            try:
                print(f"Authorization {self.email}...")
                self.client.login(email=self.email, password=password)
                break
            except amino.exceptions.ActionNotAllowed:
                print("Change device_id")
                self.client.device_id = devices[random.randint(1, len(devices))].replace("\n", "")
                continue
            except amino.exceptions.FailedLogin:
                print(f"[{self.email}]: Failed Login")
                continue
            except amino.exceptions.InvalidAccountOrPassword:
                print(f"[{self.email}]: Invalid account or password.")
                continue
            except amino.exceptions.InvalidPassword:
                print(f"[{self.email}]: Invalid Password")
                continue
            except amino.exceptions.InvalidEmail:
                print(f"[{self.email}]: Invalid Email")
                continue
            except amino.exceptions.AccountDoesntExist:
                print(f"[{self.email}]: Account does not exist")
                continue
            except amino.exceptions.VerificationRequired as verify:
                print(f"[Confirm your account]: {verify}")
        print("Authorization was successful")
        self.save_auth_data(password)
        return self.client

    def multilogin(self, password: str):
        while True:
            try:
                print(f"[Login][{self.email}]: {self.client.login(email=self.email, password=password)}")
                break
            except amino.exceptions.ActionNotAllowed:
                print("Change device_id")
                self.client.device_id = devices[random.randint(1, len(devices))].replace("\n", "")
                continue
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
        return self.client

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
            json.dump(auth_data, f)


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


class ServiceApp:
    def __init__(self):
        self.pool_count = len(accounts) if len(accounts) <= 10 else 10
        self.client = Login(input("Email: ")).login()
        self.com_id = Community(self.client).select()
        self.object_id = None
        self.back = False

    def run(self):
        while True:
            try:
                logo = open("src/draw/menu.txt", "r").read()
                print(colored(logo, "cyan"))
                choice = input("Enter the number >>> ")
                if choice == "1":
                    pool = Pool(self.pool_count)
                    pool.map(self.play_lottery, accounts.items())
                    print("[PlayLottery]: Finish.")
                elif choice == "2":
                    blog_link = input("Blog link: ")
                    self.object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                    pool = Pool(self.pool_count)
                    pool.map(self.send_coins, accounts.items())
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
                    pool.map(self.like_blog, accounts.items())
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
                    print("[LikeRecentBlogs]: Finish.")
                elif choice == "7":
                    self.object_id = Threads(self.client, self.com_id).select()
                    pool = Pool(self.pool_count)
                    pool.map(self.join_bots_to_chat, accounts.items())
                    print("[JoinBotsToChat]: Finish.")
                elif choice == "8":
                    self.object_id = Community(self.client).select()
                    pool = Pool(self.pool_count)
                    pool.map(self.join_bots_to_community, accounts.items())
                    print("[JoinBotsToCommunity]: Finish.")
                elif choice == "0":
                    self.com_id = Community(self.client).select()
                    print("Community changed")
            except:
                print(traceback.format_exc())

    def play_lottery(self, account: dict):
        email = account[0]
        password = account[1]
        self.client = Login(email).multilogin(password)
        if self.client is not False:
            sub_client = Community(self.client).sub_client(self.com_id)

            try:
                sub_client.lottery()
            except amino.exceptions.AlreadyPlayedLottery:
                print(f"[{email}]: AlreadyPlayedLottery")
            except Exception as e:
                print(f"[{email}][Exception]:\n{e}")

    def send_coins(self, account: dict):
        email = account[0]
        password = account[1]
        self.client = Login(email).multilogin(password)
        if self.client is not False:
            sub_client = Community(self.client).sub_client(self.com_id)
            coins = int(self.client.get_wallet_info().totalCoins)
            if coins != 0:
                try:
                    print(f"[{email}][send_coins]: {sub_client.send_coins(coins=coins, blogId=self.object_id)}")
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
                sub_client.play_quiz(quizId=self.object_id, questionIdsList=questions_list, answerIdsList=answers_list,
                                     quizMode=i)
            except:
                pass
        print(f"[quiz]: Passed the quiz!")
        print(f"[quiz]: Score: {sub_client.get_quiz_rankings(quizId=self.object_id).profile.highestScore}")

    def like_blog(self, account: dict):
        email = account[0]
        password = account[1]
        self.client = Login(email).multilogin(password)
        if self.client is not False:
            sub_client = Community(self.client).sub_client(self.com_id)
            try:
                print(f"[{email}][like]: {sub_client.like_blog(blogId=self.object_id)}")
            except amino.exceptions.RequestedNoLongerExists:
                print(f"[{email}][like]: {sub_client.like_blog(wikiId=self.object_id)}")

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

    def join_bots_to_chat(self, account):
        email = account[0]
        password = account[1]
        self.client = Login(email).multilogin(password)
        if self.client is not False:
            sub_client = Community(self.client).sub_client(self.com_id)
            print(f"[{email}][Join to chat]: {sub_client.join_chat(chatId=self.object_id)}")

    def join_bots_to_community(self, account):
        email = account[0]
        password = account[1]
        self.client = Login(email).multilogin(password)
        if self.client is not False:
            print(f"[{email}][Join to community]: {self.client.join_community(comId=self.object_id)}")
