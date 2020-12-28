import json
import os
import random
import traceback
from multiprocessing import Pool
from pathlib import Path

import amino

with open(os.getcwd() + "/lib/devices/devices.txt", "r") as file:
    devices = file.readlines()

path = Path(os.getcwd() + '/lib/accounts/bots.json')
accounts = json.loads(path.read_text(encoding='utf-8'))


def run():
    com_id = input("Community ID: ")
    while True:
        try:
            choice = input("0. Change Community\n"
                           "1. PlayLottery\n"
                           "2. SendCoins\n"
                           "3. PlayQuiz\n"
                           ">>> ")
            if choice == "1":
                PlayLottery(com_id)
                print("[PlayLottery]: Finish.")
            elif choice == "2":
                SendCoins(com_id)
                print("[SendCoins]: Finish.")
            elif choice == "3":
                PlayQuiz(com_id)
                print("[PlayQuiz]: Finish.")
            elif choice == "0":
                com_id = input("Community ID: ")
                print("Community ID changed")
        except:
            print(traceback.format_exc())


class PlayLottery:
    def __init__(self, com_id: str):
        self.com_id = com_id
        self.client = amino.Client()
        pool = Pool(10)
        pool.map(self.play_lottery, accounts.items())

    def play_lottery(self, account: dict):
        email = account[0]
        password = account[1]
        while True:
            try:
                print(f"[Login][{email}]: {self.client.login(email=email, password=password)}")
                break
            except amino.exceptions.ActionNotAllowed:
                print("Change device_id")
                self.client.device_id = devices[random.randint(1, len(devices))].replace("\n", "")
                continue
            except amino.exceptions.FailedLogin:
                print(f"[{email}]: Failed Login")
                return
            except amino.exceptions.InvalidAccountOrPassword:
                print(f"[{email}]: Invalid account or password.")
                return
            except amino.exceptions.InvalidPassword:
                print(f"[{email}]: Invalid Password")
                return
            except amino.exceptions.InvalidEmail:
                print(f"[{email}]: Invalid Email")
                return

        try:
            sub_client = amino.SubClient(comId=self.com_id, profile=self.client.profile)
        except Exception as e:
            print(f"[{email}][Exception]:\n{e}")
            return

        try:
            sub_client.lottery()
        except amino.exceptions.AlreadyPlayedLottery:
            print(f"[{email}]: AlreadyPlayedLottery")
            return
        except Exception as e:
            print(f"[{email}][Exception]:\n{e}")
            return


class SendCoins:
    def __init__(self, com_id: str):
        self.com_id = com_id
        self.client = amino.Client()
        blog_link = input("Blog link: ")
        self.blog_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
        pool = Pool(10)
        pool.map(self.send_coins, accounts.items())

    def send_coins(self, account: dict):
        email = account[0]
        password = account[1]
        while True:
            try:
                print(f"[Login][{email}]: {self.client.login(email=email, password=password)}")
                break
            except amino.exceptions.ActionNotAllowed:
                print("Change device_id")
                self.client.device_id = devices[random.randint(1, len(devices))].replace("\n", "")
                continue
            except amino.exceptions.FailedLogin:
                print(f"[{email}]: Failed Login")
                return
            except amino.exceptions.InvalidAccountOrPassword:
                print(f"[{email}]: Invalid account or password.")
                return
            except amino.exceptions.InvalidPassword:
                print(f"[{email}]: Invalid Password")
                return
            except amino.exceptions.InvalidEmail:
                print(f"[{email}]: Invalid Email")
                return

        try:
            sub_client = amino.SubClient(comId=self.com_id, profile=self.client.profile)
        except Exception as e:
            print(f"[{email}][Exception]:\n{e}")
            return

        coins = int(self.client.get_wallet_info().totalCoins)
        if coins == 0:
            print(f"[{email}][NotEnoughCoins]")
            return

        try:
            print(f"[{email}][send_coins]: {sub_client.send_coins(coins=coins, blogId=self.blog_id)}")
        except amino.exceptions.NotEnoughCoins:
            print(f"[{email}][NotEnoughCoins][coins {coins}]")
            return
        except amino.exceptions.InvalidRequest:
            print(f"[{email}][InvalidRequest][coins {coins}]")
            return
        print(f"[{email}]: {coins} монет отправлено.")


class PlayQuiz:
    def __init__(self, com_id: str):
        self.com_id = com_id
        self.client = amino.Client()
        self.quiz_link = input("Link: ")
        self.play_quiz()

    def play_quiz(self):
        questions_list = []
        answers_list = []

        while True:
            email = input("Email: ")
            password = input("Password: ")
            try:
                self.client.login(email=str(email), password=str(password))
                break
            except amino.exceptions.ActionNotAllowed:
                print("Change device_id")
                self.client.device_id = devices[random.randint(1, len(devices))].replace("\n", "")
                continue
            except amino.exceptions.FailedLogin:
                print("[quiz]: Failed Login")
            except amino.exceptions.InvalidAccountOrPassword:
                print("[quiz]: Invalid account or password.")
            except amino.exceptions.InvalidPassword:
                print("[quiz]: Invalid Password")
            except amino.exceptions.InvalidEmail:
                print("[quiz]: Invalid Email")

        subclient = amino.SubClient(comId=self.com_id, profile=self.client.profile)
        quiz_id = subclient.get_from_code(str(self.quiz_link.split('/')[-1])).objectId
        quiz_info = subclient.get_blog_info(quizId=quiz_id).json
        quiestions = quiz_info["blog"]["quizQuestionList"]
        total_questions = quiz_info["blog"]["extensions"]["quizTotalQuestionCount"]

        for x, question in enumerate(quiestions, 1):
            print(f"[quiz][{x}/{total_questions}]: Choosing the right answer...")
            question_id = question["quizQuestionId"]
            answers = question["extensions"]["quizQuestionOptList"]
            for answer in answers:
                answer_id = answer["optId"]
                subclient.play_quiz(quizId=quiz_id, questionIdsList=[question_id], answerIdsList=[answer_id])
                latest_score = subclient.get_quiz_rankings(quizId=quiz_id).profile.latestScore
                if latest_score > 0:
                    print(f"[quiz][{x}/{total_questions}]: Answer found!")
                    questions_list.append(question_id)
                    answers_list.append(answer_id)

        if "quizInBestQuizzes" in quiz_info["blog"]["extensions"]:
            for i in range(2):
                subclient.play_quiz(quizId=quiz_id, questionIdsList=questions_list, answerIdsList=answers_list,
                                    quizMode=i)
        else:
            subclient.play_quiz(quizId=quiz_id, questionIdsList=questions_list, answerIdsList=answers_list, quizMode=0)

        print(f"[quiz]: Passed the quiz!")
        print(f"[quiz]: Score: {subclient.get_quiz_rankings(quizId=quiz_id).profile.highestScore}")
