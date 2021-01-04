import json
import os
import random
import threading
import time
import traceback
from multiprocessing import Pool
from pathlib import Path

from termcolor import colored

import amino

with open(os.getcwd() + "/src/devices/devices.txt", "r") as file:
    devices = file.readlines()

with open(os.getcwd() + "/src/activity/comments.txt", "r") as comments_file:
    comments = comments_file.readlines()

path = Path(os.getcwd() + '/src/accounts/bots.json')
accounts = json.loads(path.read_text(encoding='utf-8'))


class Login:
    def login(self):
        while True:
            email = input("Email: ")
            password = self.get_password(email)
            client = amino.Client()
            try:
                print(f"Authorization {email}...")
                client.login(email=email, password=password)
                break
            except amino.exceptions.ActionNotAllowed:
                print("Change device_id")
                client.device_id = devices[random.randint(1, len(devices))].replace("\n", "")
                continue
            except amino.exceptions.FailedLogin:
                print(f"[{email}]: Failed Login")
                continue
            except amino.exceptions.InvalidAccountOrPassword:
                print(f"[{email}]: Invalid account or password.")
                continue
            except amino.exceptions.InvalidPassword:
                print(f"[{email}]: Invalid Password")
                continue
            except amino.exceptions.InvalidEmail:
                print(f"[{email}]: Invalid Email")
                continue
            except amino.exceptions.AccountDoesntExist:
                print(f"[{email}]: Account does not exist")
                continue
            except amino.exceptions.VerificationRequired as verify:
                print(verify)
                input("Confirm your account and press ENTER...")
        print("Authorization was successful")
        self.save_auth_data(email, password)
        return client

    @staticmethod
    def multilogin(client, email: str, password: str):
        while True:
            try:
                print(f"[Login][{email}]: {client.login(email=email, password=password)}")
                break
            except amino.exceptions.ActionNotAllowed:
                print("Change device_id")
                client.device_id = devices[random.randint(1, len(devices))].replace("\n", "")
                continue
            except amino.exceptions.FailedLogin:
                print(f"[{email}]: Failed Login")
                return False
            except amino.exceptions.InvalidAccountOrPassword:
                print(f"[{email}]: Invalid account or password.")
                return False
            except amino.exceptions.InvalidPassword:
                print(f"[{email}]: Invalid Password")
                return False
            except amino.exceptions.InvalidEmail:
                print(f"[{email}]: Invalid Email")
                return False
            except amino.exceptions.AccountDoesntExist:
                print(f"[{email}]: Account does not exist")
                return False
            except amino.exceptions.VerificationRequired as verify:
                print(verify)
                input("Confirm your account and press ENTER...")
        return client

    @staticmethod
    def get_password(email: str):
        with open("src/auth/data.json", "r") as f:
            auth_data = json.load(f)
        try:
            email = email
            password = auth_data[email]
            return password
        except (KeyError, IndexError, TypeError):
            password = input("Password: ")
            return password

    @staticmethod
    def save_auth_data(email: str, password: str):
        with open("src/auth/data.json", "r") as f:
            auth_data = json.load(f)
        with open("src/auth/data.json", "w") as f:
            auth_data.update({email: password})
            json.dump(auth_data, f)


class Community:
    def __init__(self, client):
        self.client = client

    def select(self):
        sub_clients = self.client.sub_clients(start=0, size=100)
        for x, name in enumerate(sub_clients.name, 1):
            print(f"{x}. {name}")
        choice_sub_client = input("Enter community number: ")
        return sub_clients.comId[int(choice_sub_client) - 1]


class ServiceApp:
    def __init__(self):
        self.back = False
        self.client = Login().login()
        self.com_id = Community(self.client).select()
        self.object_id = None

    def run(self):
        while True:
            try:
                logo = open("src/draw/menu.txt", "r").read()
                print(colored(logo, "cyan"))
                choice = input("Enter the number >>> ")
                if choice == "1":
                    pool = Pool(10)
                    pool.map(self.play_lottery, accounts.items())
                    print("[PlayLottery]: Finish.")
                elif choice == "2":
                    blog_link = input("Blog link: ")
                    self.object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                    pool = Pool(10)
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
                    pool = Pool(10)
                    pool.map(self.like_blog, accounts.items())
                    print("[LikeBlog]: Finish.")
                elif choice == "5":
                    self.unfollow()
                    print("[Unfollow]: Finish.")
                elif choice == "6":
                    threading.Thread(target=self.like_recent_blogs).start()
                    input("\nPress ENTER to stop...\n")
                    self.back = True
                    print("[LikeRecentBlogs]: Finish.")
                elif choice == "0":
                    self.com_id = Community(self.client).select()
                    print("Community changed")
            except:
                print(traceback.format_exc())

    def play_lottery(self, account: dict):
        email = account[0]
        password = account[1]
        self.client = Login().multilogin(self.client, email, password)
        if self.client is False:
            return
        sub_client = amino.SubClient(comId=self.com_id, profile=self.client.profile)

        try:
            sub_client.lottery()
        except amino.exceptions.AlreadyPlayedLottery:
            print(f"[{email}]: AlreadyPlayedLottery")
            return
        except Exception as e:
            print(f"[{email}][Exception]:\n{e}")
            return

    def send_coins(self, account: dict):
        email = account[0]
        password = account[1]
        self.client = Login().multilogin(self.client, email, password)
        if self.client is False:
            return
        sub_client = amino.SubClient(comId=self.com_id, profile=self.client.profile)

        coins = int(self.client.get_wallet_info().totalCoins)
        if coins == 0:
            print(f"[{email}][NotEnoughCoins]")
            return

        try:
            print(f"[{email}][send_coins]: {sub_client.send_coins(coins=coins, blogId=self.object_id)}")
        except amino.exceptions.NotEnoughCoins:
            print(f"[{email}][NotEnoughCoins][coins {coins}]")
            return
        except amino.exceptions.InvalidRequest:
            print(f"[{email}][InvalidRequest][coins {coins}]")
            return
        print(f"[{email}]: {coins} монет отправлено.")

    def play_quiz(self):
        questions_list = []
        answers_list = []

        subclient = amino.SubClient(comId=self.com_id, profile=self.client.profile)
        quiz_info = subclient.get_blog_info(quizId=self.object_id).json
        quiestions = quiz_info["blog"]["quizQuestionList"]
        total_questions = quiz_info["blog"]["extensions"]["quizTotalQuestionCount"]

        for x, question in enumerate(quiestions, 1):
            print(f"[quiz][{x}/{total_questions}]: Choosing the right answer...")
            question_id = question["quizQuestionId"]
            answers = question["extensions"]["quizQuestionOptList"]
            for answer in answers:
                answer_id = answer["optId"]
                subclient.play_quiz(quizId=self.object_id, questionIdsList=[question_id], answerIdsList=[answer_id])
                latest_score = subclient.get_quiz_rankings(quizId=self.object_id).profile.latestScore
                if latest_score > 0:
                    print(f"[quiz][{x}/{total_questions}]: Answer found!")
                    questions_list.append(question_id)
                    answers_list.append(answer_id)

        if "quizInBestQuizzes" in quiz_info["blog"]["extensions"]:
            for i in range(2):
                subclient.play_quiz(quizId=self.object_id, questionIdsList=questions_list, answerIdsList=answers_list,
                                    quizMode=i)
        else:
            subclient.play_quiz(quizId=self.object_id, questionIdsList=questions_list, answerIdsList=answers_list, quizMode=0)

        print(f"[quiz]: Passed the quiz!")
        print(f"[quiz]: Score: {subclient.get_quiz_rankings(quizId=self.object_id).profile.highestScore}")

    def like_blog(self, account: dict):
        email = account[0]
        password = account[1]
        self.client = Login().multilogin(self.client, email, password)
        if self.client is False:
            return
        sub_client = amino.SubClient(comId=self.com_id, profile=self.client.profile)
        try:
            print(f"[{email}][like]: {sub_client.like_blog(blogId=self.object_id)}")
        except amino.exceptions.RequestedNoLongerExists:
            print(f"[{email}][like]: {sub_client.like_blog(wikiId=self.object_id)}")

    def unfollow(self):
        subclient = amino.SubClient(comId=self.com_id, profile=self.client.profile)
        back = False
        iteration = 0
        while not back:
            for i in range(0, 2000, 100):
                followings = subclient.get_user_following(userId=self.client.userId, start=i, size=100)
                if len(followings.userId) == 0:
                    back = True
                    break
                for user_id in followings.userId:
                    iteration += 1
                    print(f"[{iteration}]: Unfollow")
                    subclient.unfollow(userId=user_id)

    def like_recent_blogs(self):
        subclient = amino.SubClient(comId=self.com_id, profile=self.client.profile)
        old_blogs = []
        while not self.back:
            print("Get recent blogs")
            recent_blogs = subclient.get_recent_blogs(start=0, size=100)
            for blog_id, blog_type in zip(recent_blogs.blog.blogId, recent_blogs.blog.type):
                if blog_id not in old_blogs:
                    try:
                        try:
                            subclient.like_blog(blogId=blog_id)
                            subclient.comment(message=random.choice(comments), blogId=blog_id)
                            time.sleep(2.5)
                        except amino.exceptions.RequestedNoLongerExists:
                            subclient.like_blog(wikiId=blog_id)
                            subclient.comment(message=random.choice(comments), wikiId=blog_id)
                            time.sleep(2.5)
                        print("Like")
                    except Exception as e:
                        print(e)
                    old_blogs.append(blog_id)
            time.sleep(10)
