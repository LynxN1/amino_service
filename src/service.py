import os
import amino
import json
import yaml
import random
import time
import traceback

from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from termcolor import colored
from string import ascii_letters
from .config import get_accounts, get_devices, get_count, get_reg_devices, get_comments, set_bots, set_pool_count


class Login:
    def __init__(self):
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

    def multilogin_sid(self, account: dict):
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
            except Exception as e:
                print(Log().align(email, str(e)))
                return False

    def multilogin(self, account: dict):
        email = account.get("email")
        password = account.get("password")
        while True:
            try:
                self.client.login(email, password)
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
                print(Log().align(email, "InvalidSession"))
                return False
            except Exception as e:
                print(Log().align(email, str(e)))
                return False

    def check_sid(self):
        print("Checking accounts...")
        accounts = get_accounts()
        bad_accounts = []
        if accounts:
            for i in accounts:
                if i.get("sid") is None:
                    bad_accounts.append(i)
            for i in bad_accounts:
                accounts.remove(i)
            if bad_accounts:
                print(f"{len(bad_accounts)} bad accounts detected. Starting fix...")
                pool = Pool(set_pool_count())
                sid_pool = pool.map(self.get_sid, bad_accounts)
                for i in sid_pool:
                    if i:
                        accounts.append(i)
                if accounts:
                    with open("src/accounts/bots.yaml", "w") as accounts_file:
                        yaml.dump(accounts, accounts_file, Dumper=yaml.Dumper)
        else:
            print(colored("bots.yaml is empty", "red"))

    def update_sid(self):
        print("Starting update...")
        pool = Pool(set_pool_count())
        sid_pool = pool.map(self.get_sid, get_accounts())
        with open("src/accounts/bots.yaml", "w") as accounts_file:
            yaml.dump(sid_pool, accounts_file, Dumper=yaml.Dumper)

    def get_sid(self, account: dict):
        email = account.get("email")
        password = account.get("password")
        while True:
            try:
                self.client.login(email, password)
                print(Log().align(email, "SID updated"))
                return {"email": email, "password": password, "uid": self.client.userId, "sid": self.client.sid}
            except amino.exceptions.ActionNotAllowed:
                print(Log().align(email, "device_id updated"))
                self.client.device_id = random.choice(get_devices()).replace("\n", "")
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
            except Exception as e:
                print(Log().align(email, str(e)))
                return

    @staticmethod
    def get_password(email: str):
        with open("src/auth/data.json", "r") as f:
            auth_data = json.load(f)
        try:
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
            json.dump(auth_data, f, indent=2)


class Register:
    def __init__(self):
        self.client = amino.Client()
        self.email = None
        self.password = input("Set a password for all accounts: ")
        while len(self.password) < 6:
            print(colored("Password must be at least 6 characters long", "red"))
            self.password = input("Set a password for all accounts: ")
        self.current_device = None
        self.code = None

    def run(self):
        if get_reg_devices():
            for device in get_reg_devices():
                self.current_device = device.replace("\n", "")
                for _ in range(3):
                    self.email = input("Email: ")
                    if self.register():
                        self.client.request_verify_code(deviceId=self.current_device, email=self.email)
                        if self.verify():
                            if self.login():
                                self.save_account()
                            else:
                                continue
                        else:
                            continue
                    else:
                        continue
        else:
            print(colored("reg_devices.txt is empty", "red"))

    def register(self):
        while True:
            try:
                nick = ''.join(random.choice(ascii_letters) for _ in range(random.randint(2, 5)))
                self.client.register(nickname=nick, email=self.email, password=str(self.password),
                                     deviceId=self.current_device)
                return True
            except amino.exceptions.AccountLimitReached:
                print(colored("AccountLimitReached", "red"))
                return False
            except amino.exceptions.InvalidEmail:
                print(colored("Invalid Email", "red"))
                return False
            except amino.exceptions.EmailAlreadyTaken:
                print(colored("EmailAlreadyTaken", "red"))
                self.email = input("Email: ")
            except amino.exceptions.UnsupportedEmail:
                print(colored("UnsupportedEmail", "red"))
                return False
            except amino.exceptions.CommandCooldown:
                print(colored("CommandCooldown", "red"))
                return False
            except amino.exceptions.VerificationRequired as e:
                input(str(e) + "\n\npress ENTER to continue...")
            except Exception as e:
                print(colored(str(e), "red"))
                return False

    def verify(self):
        while True:
            self.code = input("Code: ")
            try:
                self.client.verify(deviceId=self.current_device, email=self.email, code=self.code)
                return True
            except amino.exceptions.IncorrectVerificationCode:
                print(colored("IncorrectVerificationCode", "red"))
            except Exception as e:
                print(colored(str(e), "red"))
                return False

    def login(self):
        while True:
            try:
                self.client.login(email=self.email, password=self.password)
                return True
            except amino.exceptions.ActionNotAllowed:
                self.client.device_id = random.choice(get_devices()).replace("\n", "")
            except Exception as e:
                print(colored(str(e), "red"))
                return False

    def activate(self):
        while True:
            try:
                self.client.activate_account(email=self.email, code=self.code)
                return True
            except Exception as e:
                print(colored(str(e), "red"))
                return False

    def save_account(self):
        with open(os.getcwd() + "/src/accounts/bots.yaml", "a") as accounts_file:
            yaml.dump([{"email": self.email, "password": self.password}], accounts_file, Dumper=yaml.Dumper)


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
        try:
            sub_client = amino.SubClient(comId=com_id, profile=self.client.profile)
            return sub_client
        except amino.exceptions.UserNotMemberOfCommunity:
            print("UserNotMemberOfCommunity")
            return False
        except amino.exceptions.UserUnavailable:
            print("UserUnavailable")
            return False
        except Exception as e:
            print(e)
            return False


class Chats:
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
    @staticmethod
    def align(text: str, action: str):
        spaces = 30 - len(text)
        text = f"[{text}"
        for _ in range(spaces):
            text += " "
        text += f"]: {action}"
        return text


class ServiceApp:
    def __init__(self):
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
        self.invite_link = None
        self.back = False

    def run(self):
        while True:
            try:
                print(colored(open("src/draw/management_choice.txt", "r").read(), "cyan"))
                management_choice = input("Enter the number >>> ")
                if management_choice == "s":
                    set_bots()
                    input("Changes saved. Please restart the program...")
                    exit(0)
                elif management_choice == "0":
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
                            self.unfollow_all()
                            self.back = False
                            print("[UnfollowAll]: Finish.")
                        elif choice == "3":
                            thread_pool = ThreadPool(1)
                            thread_pool.apply(self.activity)
                            input("\nPress ENTER to stop...\n")
                            self.back = True
                            thread_pool.join()
                            self.back = False
                            print("[Activity]: Finish.")
                        elif choice == "4":
                            self.follow_all()
                            print("[FollowAll]: Finish.")
                        elif choice == "5":
                            Register().run()
                            print("[Register]: Finish.")
                        elif choice == "b":
                            back = True
                elif management_choice == "2":
                    Login().check_sid()
                    back = False
                    while not back:
                        print(colored(open("src/draw/bot_management.txt", "r").read(), "cyan"))
                        choice = input("Enter the number >>> ")
                        if choice == "1":
                            pool = Pool(set_pool_count())
                            result = pool.map(self.play_lottery, get_accounts())
                            count_result = get_count(result)
                            print(f"Accounts: {count_result['accounts']}\nResult: +{count_result['count']} coins")
                            print("[PlayLottery]: Finish.")
                        elif choice == "2":
                            blog_link = input("Blog link: ")
                            self.object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            pool = Pool(set_pool_count())
                            result = pool.map(self.send_coins, get_accounts())
                            count_result = get_count(result)
                            print(f"Accounts {count_result['accounts']}\nResult: +{count_result['count']} coins")
                            print("[SendCoins]: Finish.")
                        elif choice == "3":
                            blog_link = input("Blog link: ")
                            self.object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            pool = Pool(set_pool_count())
                            pool.map(self.like_blog, get_accounts())
                            print("[LikeBlog]: Finish.")
                        elif choice == "4":
                            self.object_id = Chats(self.client, self.com_id).select()
                            pool = Pool(set_pool_count())
                            pool.map(self.join_bots_to_chat, get_accounts())
                            print("[JoinBotsToChat]: Finish.")
                        elif choice == "5":
                            self.object_id = Community(self.client).select()
                            pool = Pool(set_pool_count())
                            if self.client.get_community_info(self.object_id).joinType == 2:
                                self.invite_link = input("Enter invite link/code: ")
                                pool.map(self.join_bots_to_community, get_accounts())
                            else:
                                pool.map(self.join_bots_to_community, get_accounts())
                            print("[JoinBotsToCommunity]: Finish.")
                        elif choice == "6":
                            self.object_id = Chats(self.client, self.com_id).select()
                            self.text = input("Message text: ")
                            pool = Pool(set_pool_count())
                            pool.map(self.send_message, get_accounts())
                            print("[SendMessage]: Finish.")
                        elif choice == "7":
                            user_link = input("Link to user: ")
                            self.object_id = self.client.get_from_code(str(user_link.split('/')[-1])).objectId
                            pool = Pool(set_pool_count())
                            pool.map(self.follow, get_accounts())
                            print("[Follow]: Finish.")
                        elif choice == "s":
                            Login().update_sid()
                            print("[UpdateSIDs]: Finish.")
                        elif choice == "b":
                            back = True
            except Exception as e:
                print(traceback.format_exc())
                print(colored(str(e), "red"))

    def play_lottery(self, account: dict):
        email = account.get("email")
        client = Login().multilogin_sid(account)
        if client:
            sub_client = Community(client).sub_client(self.com_id)
            if sub_client:
                try:
                    play = sub_client.lottery()
                    award = play.awardValue if play.awardValue else 0
                    print(Log().align(email, f"+{award} coins won"))
                    return int(award)
                except amino.exceptions.AlreadyPlayedLottery:
                    print(Log().align(email, "AlreadyPlayedLottery"))
                except amino.exceptions.YouAreBanned:
                    print(Log().align(email, "You are banned"))
                except amino.exceptions.InvalidSession:
                    print(Log().align(email, "SID update required..."))
                except Exception as e:
                    print(Log().align(email, str(e)))
            else:
                print(Log().align(email, "Community error"))

    def send_coins(self, account: dict):
        email = account.get("email")
        client = Login().multilogin_sid(account)
        if client:
            sub_client = Community(client).sub_client(self.com_id)
            if sub_client:
                try:
                    coins = int(client.get_wallet_info().totalCoins)
                    if coins != 0:
                        sub_client.send_coins(coins=coins, blogId=self.object_id)
                        print(Log().align(email, f"+{coins} coins"))
                        return coins
                    else:
                        print(Log().align(email, "NotEnoughCoins"))
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
                print(Log().align(email, "Community error"))

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
        client = Login().multilogin_sid(account)
        if client:
            sub_client = Community(client).sub_client(self.com_id)
            if sub_client:
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
            else:
                print(Log().align(email, "Community error"))

    def unfollow_all(self):
        print("Unfollow all...")
        thread_pool = ThreadPool(40)
        sub_client = Community(self.client).sub_client(self.com_id)
        while not self.back:
            following_count = sub_client.get_user_info(userId=self.client.userId).followingCount
            if following_count > 0:
                for i in range(0, 1000, 100):
                    followings = sub_client.get_user_following(userId=self.client.userId, start=i, size=100)
                    if followings.userId:
                        for user_id in followings.userId:
                            thread_pool.apply(sub_client.unfollow, [user_id])
                    else:
                        self.back = True
                        break
            else:
                self.back = True

    def follow_all(self):
        print("Subscribe...")
        sub_client = Community(self.client).sub_client(self.com_id)
        old = []
        for i in range(0, 20000, 100):
            users = sub_client.get_all_users(type="recent", start=i, size=100).profile.userId
            if users:
                try:
                    sub_client.follow(userId=users)
                except Exception as e:
                    print(e)
            else:
                break
        for i in range(0, 20000, 100):
            users = sub_client.get_online_users(start=i, size=100).profile.userId
            if users:
                try:
                    sub_client.follow(userId=users)
                except Exception as e:
                    print(e)
            else:
                break
        for i in range(0, 50000, 100):
            chats = sub_client.get_public_chat_threads(type="recommended", start=i, size=100).chatId
            if chats:
                for chatid in chats:
                    for x in range(0, 1000, 100):
                        users = sub_client.get_chat_users(chatId=chatid, start=x, size=100).userId
                        if users:
                            try:
                                sub_client.follow(userId=users)
                            except Exception as e:
                                print(e)
                        else:
                            break
            else:
                break

    def activity(self):
        print("Activity...")
        comments = get_comments()
        subclient = amino.SubClient(comId=self.com_id, profile=self.client.profile)
        old_blogs = []
        while not self.back:
            recent_blogs = subclient.get_recent_blogs(start=0, size=100)
            for blog_id, blog_type in zip(recent_blogs.blog.blogId, recent_blogs.blog.type):
                if blog_id not in old_blogs:
                    try:
                        subclient.like_blog(blogId=blog_id)
                        if comments:
                            subclient.comment(message=random.choice(comments), blogId=blog_id)
                            time.sleep(2.5)
                    except amino.exceptions.RequestedNoLongerExists:
                        subclient.like_blog(wikiId=blog_id)
                        if comments:
                            subclient.comment(message=random.choice(comments), wikiId=blog_id)
                            time.sleep(2.5)
                    old_blogs.append(blog_id)
            time.sleep(5)

    def join_bots_to_chat(self, account: dict):
        email = account.get("email")
        client = Login().multilogin(account)
        if client:
            sub_client = Community(client).sub_client(self.com_id)
            if sub_client:
                print(sub_client.userId)
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
            else:
                print(Log().align(email, "Community error"))

    def join_bots_to_community(self, account: dict):
        email = account.get("email")
        client = Login().multilogin_sid(account)
        if client:
            if self.invite_link:
                invitation_id = self.client.link_identify(code=str(self.invite_link.split("/")[-1])).get("invitationId")
                if invitation_id:
                    try:
                        client.join_community(comId=self.object_id, invitationId=invitation_id)
                        print(Log().align(email, "Join"))
                    except amino.exceptions.InvalidSession:
                        print(Log().align(email, "SID update required..."))
                    except Exception as e:
                        print(Log().align(email, str(e)))
            else:
                try:
                    client.join_community(comId=self.object_id)
                    print(Log().align(email, "Join"))
                except amino.exceptions.InvalidSession:
                    print(Log().align(email, "SID update required..."))
                except Exception as e:
                    print(Log().align(email, str(e)))

    def send_message(self, account: dict):
        email = account.get("email")
        client = Login().multilogin_sid(account)
        if client:
            sub_client = Community(client).sub_client(self.com_id)
            if sub_client:
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
            else:
                print(Log().align(email, "Community error"))

    def follow(self, account: dict):
        email = account.get("email")
        client = Login().multilogin_sid(account)
        if client:
            sub_client = Community(client).sub_client(self.com_id)
            if sub_client:
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
            else:
                print(Log().align(email, "Community error"))
