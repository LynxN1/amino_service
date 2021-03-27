import os
import amino
import yaml
import random
import time
import pathlib

from functools import partial
from multiprocessing.pool import ThreadPool
from termcolor import colored
from string import ascii_letters
from .config import get_accounts, get_devices, get_count, get_reg_devices, get_comments, set_pool_count, set_accounts, get_auth_data, set_auth_data, converter, align
from .nick_gen import UsernameGenerator


class Login:
    @staticmethod
    def login_sid(account: dict):
        client = amino.Client()
        email = account.get("email")
        sid = account.get("sid")
        while True:
            try:
                client.login_sid(sid)
                return client
            except amino.exceptions.ActionNotAllowed:
                client.device_id = client.headers.device_id = random.choice(get_devices()).replace("\n", "")
            except amino.exceptions.FailedLogin:
                print(align(email, "Failed login"))
                return False
            except amino.exceptions.InvalidAccountOrPassword:
                print(align(email, "Invalid account or password"))
                return False
            except amino.exceptions.InvalidPassword:
                print(align(email, "Invalid Password"))
                return False
            except amino.exceptions.InvalidEmail:
                print(align(email, "Invalid Email"))
                return False
            except amino.exceptions.AccountDoesntExist:
                print(align(email, "Account does not exist"))
                return False
            except amino.exceptions.VerificationRequired as verify:
                print(align(email, str(verify)))
                return False
            except amino.exceptions.InvalidSession:
                print(align(email, "SID update required..."))
                return False
            except Exception as e:
                print(align(email, str(e)))
                return False

    @staticmethod
    def login(account: dict):
        client = amino.Client()
        email = account.get("email")
        password = account.get("password")
        while True:
            try:
                client.login(email, password)
                return client
            except amino.exceptions.ActionNotAllowed:
                client.device_id = client.headers.device_id = random.choice(get_devices()).replace("\n", "")
            except amino.exceptions.FailedLogin:
                print(align(email, "Failed login"))
                return False
            except amino.exceptions.InvalidAccountOrPassword:
                print(align(email, "Invalid account or password"))
                return False
            except amino.exceptions.InvalidPassword:
                print(align(email, "Invalid Password"))
                return False
            except amino.exceptions.InvalidEmail:
                print(align(email, "Invalid Email"))
                return False
            except amino.exceptions.AccountDoesntExist:
                print(align(email, "Account does not exist"))
                return False
            except amino.exceptions.VerificationRequired as verify:
                print(align(email, str(verify)))
                return False
            except amino.exceptions.InvalidSession:
                print(align(email, "InvalidSession"))
                return False
            except Exception as e:
                print(align(email, str(e)))
                return False

    def check_sid(self, pool: ThreadPool):
        print("Checking accounts...")
        accounts = []
        for i in get_accounts():
            if i not in accounts:
                accounts.append(i)
        with open(os.path.join(os.getcwd(), "src", "accounts", "bots.yaml"), "w") as file:
            yaml.dump(accounts, file)
        bad_accounts = []
        if accounts:
            for account in accounts:
                if account and account.get("sid") is None:
                    bad_accounts.append(account)
            if bad_accounts:
                print(f"{len(bad_accounts)} bad accounts detected.")
                print("Starting update...")
                self.update_sid(bad_accounts, pool)
        else:
            print(colored("bots.yaml is empty", "red"))

    def update_sid(self, accounts: list, pool: ThreadPool):
        sid_pool = pool.map(self.get_sid, accounts)
        correct_accounts = []
        for account in sid_pool:
            if account:
                correct_accounts.append(account)
        all_accounts = get_accounts()
        for i in get_accounts():
            if i in accounts:
                all_accounts.remove(i)
        if all_accounts:
            with open(os.path.join(os.getcwd(), "src", "accounts", "bots.yaml"), "w") as file:
                yaml.dump(all_accounts, file)
        else:
            open(os.path.join(os.getcwd(), "src", "accounts", "bots.yaml"), "w").close()
        set_accounts(correct_accounts)

    def get_sid(self, account: dict):
        client = self.login(account)
        if client:
            print(align(account.get("email"), "SID updated"))
            return {"email": account.get("email"), "password": account.get("password"), "sid": client.sid, "uid": client.profile.userId}
        else:
            return False


class Register:
    def __init__(self):
        self.client = amino.Client()
        self.email = None
        self.password = input("Set a password for all accounts: ")
        while len(self.password) < 6:
            print(colored("Password must be at least 6 characters long", "red"))
            self.password = input("Set a password for all accounts: ")
        self.code = None
        self.count = 0

    def run(self):
        reg_devices = get_reg_devices()
        if reg_devices:
            for device in reg_devices:
                self.client.device_id = self.client.headers.device_id = device.replace("\n", "")
                for _ in range(3):
                    self.email = input("Email: ")
                    if self.register():
                        self.client.request_verify_code(email=self.email)
                        if self.verify():
                            if self.login():
                                if self.activate():
                                    self.save_account()
                                    self.count += 1
                                    print(f"{self.count} accounts registered")
                                else:
                                    continue
                            else:
                                continue
                        else:
                            continue
                    else:
                        continue
                self.remove_device()
        else:
            print(colored("reg_devices.txt is empty", "red"))

    def register(self):
        while True:
            try:
                nick = ''.join(random.choice(ascii_letters) for _ in range(random.randint(2, 5)))
                self.client.register(nickname=nick, email=self.email, password=str(self.password))
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
                input("Open this link in a browser and click the checkmark: " + str(e) + "\n\npress ENTER to continue...")
            except Exception as e:
                print(colored(str(e), "red"))
                return False

    def verify(self):
        while True:
            self.code = input("Code: ")
            try:
                self.client.verify(email=self.email, code=self.code)
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
        with open(os.getcwd() + "/src/accounts/new_accounts.yaml", "a") as accounts_file:
            yaml.dump([{"email": self.email, "password": self.password}], accounts_file, Dumper=yaml.Dumper)
        print(colored(f"{self.email} saved in new_accounts.yaml", "green"))

    def remove_device(self):
        devices = get_reg_devices()
        devices.pop(0)
        with open(os.getcwd() + "/src/devices/reg_devices.txt", "w") as devices_file:
            for i in devices:
                devices_file.write(i)


class Community:
    @staticmethod
    def select(client: amino.Client):
        sub_clients = client.sub_clients(start=0, size=100)
        print("Select the community:")
        for x, name in enumerate(sub_clients.name, 1):
            print(f"{x}. {name}")
        while True:
            choice_sub_client = input("Enter community number: ")
            try:
                return sub_clients.comId[int(choice_sub_client) - 1]
            except (IndexError, TypeError):
                print(colored("Invalid community number", "red"))

    @staticmethod
    def sub_client(com_id: str, client: amino.Client):
        try:
            sub_client = amino.SubClient(comId=com_id, client=client)
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
    def __init__(self, client: amino.Client, com_id: str):
        self.sub_client = Community().sub_client(com_id, client)

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


class ServiceApp:
    def __init__(self):
        single_management = SingleAccountManagement()
        single_management.login()
        if single_management.client:
            multi_management        = MultiAccountsManagement()
            multi_management.client = single_management.client
            multi_management.com_id = single_management.com_id
            chat_moderation         = ChatModeration()
            chat_moderation.client  = single_management.client
            chat_moderation.com_id  = single_management.com_id
            badass                  = Badass()
            badass.client           = single_management.client
            badass.com_id           = single_management.com_id
            while True:
                try:
                    print(colored(open("src/draw/management_choice.txt", "r").read(), "cyan"))
                    management_choice = input("Enter the number >>> ")
                    if management_choice == "1":
                        while True:
                            print(colored(open("src/draw/account_management.txt", "r").read(), "cyan"))
                            choice = input("Enter the number >>> ")
                            if choice == "1":
                                quiz_link = input("Quiz link: ")
                                object_id = single_management.client.get_from_code(str(quiz_link.split('/')[-1])).objectId
                                single_management.play_quiz(object_id)
                                print("[PlayQuiz]: Finish.")
                            elif choice == "2":
                                single_management.unfollow_all()
                                print("[UnfollowAll]: Finish.")
                            elif choice == "3":
                                single_management.activity()
                                print("[Activity]: Finish.")
                            elif choice == "4":
                                single_management.follow_all()
                                print("[FollowAll]: Finish.")
                            elif choice == "5":
                                Register().run()
                                print("[Register]: Finish.")
                            elif choice == "6":
                                single_management.get_blocker_users()
                            elif choice == "b":
                                break
                    elif management_choice == "2":
                        pool = ThreadPool(set_pool_count())
                        Login().check_sid(pool)
                        while True:
                            print(colored(open("src/draw/bot_management.txt", "r").read(), "cyan"))
                            choice = input("Enter the number >>> ")
                            if choice == "1":
                                result = pool.map(multi_management.play_lottery, get_accounts())
                                count_result = get_count(result)
                                print(f"Accounts: {count_result['accounts']}\nResult: +{count_result['count']} coins")
                                print("[PlayLottery]: Finish.")
                            elif choice == "2":
                                blog_link = input("Blog link: ")
                                object_id = single_management.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                                result = pool.map(partial(multi_management.send_coins, object_id), get_accounts())
                                count_result = get_count(result)
                                print(f"Accounts {count_result['accounts']}\nResult: +{count_result['count']} coins")
                                print("[SendCoins]: Finish.")
                            elif choice == "3":
                                blog_link = input("Blog link: ")
                                object_id = single_management.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                                pool.map(partial(multi_management.like_blog, object_id), get_accounts())
                                print("[LikeBlog]: Finish.")
                            elif choice == "4":
                                object_id = Chats(single_management.client, multi_management.com_id).select()
                                pool.map(partial(multi_management.join_bots_to_chat, object_id), get_accounts())
                                print("[JoinBotsToChat]: Finish.")
                            elif choice == "5":
                                object_id = Chats(single_management.client, multi_management.com_id).select()
                                pool.map(partial(multi_management.leave_bots_from_chat, object_id), get_accounts())
                            elif choice == "6":
                                object_id = Community().select(single_management.client)
                                invite_link = None
                                if single_management.client.get_community_info(object_id).joinType == 2:
                                    invite_link = input("Enter invite link/code: ")
                                pool.map(partial(multi_management.join_bots_to_community, invite_link), get_accounts())
                                print("[JoinBotsToCommunity]: Finish.")
                            elif choice == "7":
                                object_id = Chats(single_management.client, multi_management.com_id).select()
                                text = input("Message text: ")
                                pool.map(partial(multi_management.send_message, object_id, text), get_accounts())
                                print("[SendMessage]: Finish.")
                            elif choice == "8":
                                user_link = input("Link to user: ")
                                object_id = single_management.client.get_from_code(str(user_link.split('/')[-1])).objectId
                                pool.map(partial(multi_management.follow, object_id), get_accounts())
                                print("[Follow]: Finish.")
                            elif choice == "9":
                                user_link = input("Link to user: ")
                                object_id = single_management.client.get_from_code(str(user_link.split('/')[-1])).objectId
                                pool.map(partial(multi_management.unfollow, object_id), get_accounts())
                                print("[Unfollow]: Finish.")
                            elif choice == "10":
                                pool.map(multi_management.set_online_status, get_accounts())
                                print("[SetOnlineStatus]: Finish.")
                            elif choice == "11":
                                print("1 - Random nick")
                                print("2 - Set custom nick")
                                mode = input("Select mode: ")
                                if mode == "1":
                                    max_length = int(input("Max nick length: "))
                                    pool.map(partial(multi_management.change_nick_random, max_length, None), get_accounts())
                                else:
                                    nick = input("Enter nick: ")
                                    pool.map(partial(multi_management.change_nick_random, None, nick), get_accounts())
                                print("[ChangeNickname]: Finish.")
                            elif choice == "12":
                                user_link = input("User link: ")
                                userid = single_management.client.get_from_code(str(user_link.split('/')[-1])).objectId
                                text = input("Text: ")
                                pool.map(partial(multi_management.wall_comment, userid, text), get_accounts())
                                print("[WallComment]: Finish.")
                            elif choice == "13":
                                images = []
                                currentDirectory = pathlib.Path('src\\icons')
                                for currentFile in currentDirectory.iterdir():
                                    images.append(str(currentFile).split("\\")[2])
                                if images:
                                    pool.map(partial(multi_management.change_icon_random, images), get_accounts())
                                else:
                                    print(colored("icons is empty", "red"))
                                print("[ChangeIcon]: Finish.")
                            elif choice == "14":
                                blog_link = input("Blog link: ")
                                object_id = single_management.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                                sub_client = Community().sub_client(single_management.com_id, single_management.client)
                                polls = sub_client.get_blog_info(blogId=object_id).json["blog"]["polloptList"]
                                for x, i in enumerate(polls, 1):
                                    print(f"{x}. {i.get('title')}")
                                option = polls[int(input("Select option number: ")) - 1]["polloptId"]
                                pool.map(partial(multi_management.vote_poll, object_id, option), get_accounts())
                                print("[Vote]: Finish.")
                            elif choice == "s":
                                Login().update_sid(get_accounts(), pool)
                                print("[UpdateSIDs]: Finish.")
                            elif choice == "b":
                                break
                    elif management_choice == "3":
                        while True:
                            print(colored(open("src/draw/chat_moderation.txt", "r").read(), "cyan"))
                            choice = input("Enter the number >>> ")
                            if choice == "1":
                                object_id = Chats(single_management.client, single_management.com_id).select()
                                count = input("Number of messages: ")
                                chat_moderation.clear_chat(object_id, int(count))
                                print("[ClearChat]: Finish.")
                            elif choice == "2":
                                object_id = Chats(single_management.client, single_management.com_id).select()
                                chat_moderation.save_chat_settings(object_id)
                                print("[SaveChatSettings]: Finish.")
                            elif choice == "3":
                                object_id = Chats(single_management.client, single_management.com_id).select()
                                chat_moderation.set_view_mode(object_id)
                                print("[SetViewMode]: Finish.")
                            elif choice == "4":
                                object_id = Chats(single_management.client, single_management.com_id).select()
                                duration = int(input("Duration in seconds: "))
                                chat_moderation.set_view_mode_timer(object_id, duration)
                                print("[SetViewMode]: Finish.")
                            elif choice == "b":
                                break
                    elif management_choice == "4":
                        while True:
                            print(colored(open("src/draw/badass_management.txt", "r").read(), "cyan"))
                            choice = input("Enter the number >>> ")
                            if choice == "1":
                                choice_mode = input("Select a chat from the list or by link?\n1 - by link\n2 - from the list\n>>> ")
                                if choice_mode == "1":
                                    link = input("Link: ")
                                    object_id = single_management.client.get_from_code(str(link.split('/')[-1])).objectId
                                else:
                                    object_id = Chats(single_management.client, single_management.com_id).select()
                                badass.send_system_message(object_id)
                                print("[SendSystem]: Finish.")
                            elif choice == "2":
                                choice_mode = input("Select a chat from the list or by link?\n1 - by link\n2 - from the list\n>>> ")
                                if choice_mode == "1":
                                    link = input("Link: ")
                                    object_id = single_management.client.get_from_code(str(link.split('/')[-1])).objectId
                                else:
                                    object_id = Chats(single_management.client, single_management.com_id).select()
                                badass.spam_system_message(object_id)
                                print("[SpamSystem]: Finish.")
                            elif choice == "3":
                                object_id = Chats(single_management.client, single_management.com_id).select()
                                badass.delete_chat(object_id)
                                print("[DeleteChat]: Finish.")
                            elif choice == "4":
                                object_id = Chats(single_management.client, single_management.com_id).select()
                                badass.invite_all_users(object_id)
                                print("[InviteAll]: Finish.")
                            elif choice == "5":
                                badass.spam_posts()
                                print("[SpamPosts]: Finish.")
                            elif choice == "b":
                                break
                    elif management_choice == "0":
                        converter()
                except Exception as e:
                    print(colored(str(e), "red"))
        else:
            exit(0)


class SingleAccountManagement:
    def __init__(self):
        self.client = None
        self.com_id = None

    def login(self):
        accounts = get_auth_data()
        if accounts:
            print("Accounts:")
            for x, account in enumerate(accounts, 1):
                print(f"{x}. {account.get('email')}")
            choice = input("\nEnter \"+\" to add account\n>>> ")
            if choice == "+":
                email = input("Email: ")
                password = input("Password: ")
                self.client = Login().login({"email": email, "password": password})
                if self.client:
                    set_auth_data({"email": email, "password": password})
                else:
                    print(colored("Failed login", "red"))
                    return False
            else:
                index = int(choice) - 1
                email = accounts[index].get("email")
                password = accounts[index].get("password")
                self.client = Login().login({"email": email, "password": password})
        else:
            email = input("Email: ")
            password = input("Password: ")
            self.client = Login().login({"email": email, "password": password})
            set_auth_data({"email": email, "password": password})
        if self.client:
            self.com_id = Community().select(self.client)
            print("Login was successful!")
            return True
        else:
            print(colored("Failed login", "red"))
            return False

    def play_quiz(self, object_id: str):
        questions_list = []
        answers_list = []

        sub_client = Community().sub_client(self.com_id, self.client)
        quiz_info = sub_client.get_blog_info(quizId=object_id).json
        questions = quiz_info["blog"]["quizQuestionList"]
        total_questions = quiz_info["blog"]["extensions"]["quizTotalQuestionCount"]

        for x, question in enumerate(questions, 1):
            print(f"[quiz][{x}/{total_questions}]: Choosing the right answer...")
            question_id = question["quizQuestionId"]
            answers = question["extensions"]["quizQuestionOptList"]
            for answer in answers:
                answer_id = answer["optId"]
                sub_client.play_quiz(quizId=object_id, questionIdsList=[question_id], answerIdsList=[answer_id])
                latest_score = sub_client.get_quiz_rankings(quizId=object_id).profile.latestScore
                if latest_score > 0:
                    print(f"[quiz][{x}/{total_questions}]: Answer found!")
                    questions_list.append(question_id)
                    answers_list.append(answer_id)
        for i in range(2):
            try:
                sub_client.play_quiz(quizId=object_id, questionIdsList=questions_list, answerIdsList=answers_list,
                                     quizMode=i)
            except amino.exceptions.InvalidRequest:
                pass
        print(f"[quiz]: Passed the quiz!")
        print(f"[quiz]: Score: {sub_client.get_quiz_rankings(quizId=object_id).profile.highestScore}")

    def unfollow_all(self):
        print("Unfollowing...")
        pool_count = int(input("Number of threads: "))
        thread_pool = ThreadPool(pool_count)
        sub_client = Community().sub_client(self.com_id, self.client)
        back = False
        x = 0
        while not back:
            followings = sub_client.get_user_following(userId=self.client.userId, start=x, size=100)
            x += 100
            if followings.userId:
                for i in followings.userId:
                    thread_pool.apply_async(sub_client.unfollow, [i])
            else:
                back = True

    def activity(self):
        print("Activity...")
        comments = get_comments()
        sub_client = Community().sub_client(self.com_id, self.client)
        old_blogs = []
        while True:
            recent_blogs = sub_client.get_recent_blogs(start=0, size=10)
            for blog_id in recent_blogs.blogId:
                if blog_id not in old_blogs:
                    try:
                        sub_client.like_blog(blogId=blog_id)
                        if comments:
                            while True:
                                try:
                                    sub_client.comment(message=random.choice(comments), blogId=blog_id)
                                    break
                                except amino.exceptions.VerificationRequired:
                                    time.sleep(1)
                    except amino.exceptions.RequestedNoLongerExists:
                        sub_client.like_blog(wikiId=blog_id)
                        if comments:
                            while True:
                                try:
                                    sub_client.comment(message=random.choice(comments), wikiId=blog_id)
                                    break
                                except amino.exceptions.VerificationRequired:
                                    time.sleep(1)
                    old_blogs.append(blog_id)

    def follow_all(self):
        print("Subscribe...")
        sub_client = Community().sub_client(self.com_id, self.client)
        old = []
        pool = ThreadPool(10)
        for i in range(0, 20000, 50):
            recent_users = sub_client.get_all_users(type="recent", start=i, size=50).profile.userId
            online_users = sub_client.get_online_users(start=i, size=50).profile.userId
            users = [*recent_users, *online_users]
            if users:
                try:
                    pool.apply_async(sub_client.follow, [users])
                except:
                    pass
            else:
                break
        for i in range(0, 20000, 100):
            chats = sub_client.get_public_chat_threads(type="recommended", start=i, size=100).chatId
            if chats:
                for chatid in chats:
                    for x in range(0, 1000, 50):
                        users = sub_client.get_chat_users(chatId=chatid, start=x, size=50).userId
                        if users:
                            for userid in old:
                                if userid in users:
                                    users.remove(userid)
                            for userid in users:
                                old.append(userid)
                            try:
                                pool.apply_async(sub_client.follow, [users])
                            except:
                                pass
                        else:
                            break
            else:
                break

    def get_blocker_users(self):
        sub_client = Community().sub_client(self.com_id, self.client)
        users = sub_client.get_blocker_users(start=0, size=100)
        if users:
            for x, i in enumerate(users, 1):
                user = sub_client.get_user_info(i)
                print(f"{x}.")
                print(f"Userid: {i}")
                print(f"Nickname: {user.nickname}")
                print(f"Lvl: {user.level}")
                print()


class MultiAccountsManagement:
    def __init__(self):
        self.com_id = None
        self.client = None

    def play_lottery(self, account: dict):
        email = account.get("email")
        client = Login().login_sid(account)
        if client:
            sub_client = Community().sub_client(self.com_id, client)
            if sub_client:
                try:
                    play = sub_client.lottery()
                    award = play.awardValue if play.awardValue else 0
                    print(align(email, f"+{award} coins won"))
                    return int(award)
                except amino.exceptions.AlreadyPlayedLottery:
                    print(align(email, "AlreadyPlayedLottery"))
                except amino.exceptions.YouAreBanned:
                    print(align(email, "You are banned"))
                except amino.exceptions.InvalidSession:
                    print(align(email, "SID update required..."))
                except Exception as e:
                    print(align(email, str(e)))
            else:
                print(align(email, "Community error"))

    def send_coins(self, object_id, account: dict):
        email = account.get("email")
        client = Login().login_sid(account)
        if client:
            sub_client = Community().sub_client(self.com_id, client)
            if sub_client:
                try:
                    coins = int(client.get_wallet_info().totalCoins)
                    if coins != 0:
                        sub_client.send_coins(coins=coins, blogId=object_id)
                        print(align(email, f"+{coins} coins"))
                        return coins
                    else:
                        print(align(email, "NotEnoughCoins"))
                except amino.exceptions.NotEnoughCoins:
                    print(align(email, "NotEnoughCoins"))
                except amino.exceptions.InvalidRequest:
                    print(align(email, "InvalidRequest"))
                except amino.exceptions.YouAreBanned:
                    print(align(email, "You are banned"))
                except amino.exceptions.InvalidSession:
                    print(align(email, "SID update required..."))
                except Exception as e:
                    print(align(email, str(e)))
            else:
                print(align(email, "Community error"))

    def like_blog(self, object_id, account: dict):
        email = account.get("email")
        client = Login().login_sid(account)
        if client:
            sub_client = Community().sub_client(self.com_id, client)
            if sub_client:
                try:
                    sub_client.like_blog(blogId=object_id)
                    print(align(email, "Like"))
                except amino.exceptions.RequestedNoLongerExists:
                    sub_client.like_blog(wikiId=object_id)
                    print(align(email, "Like"))
                except amino.exceptions.YouAreBanned:
                    print(align(email, "You are banned"))
                except amino.exceptions.InvalidSession:
                    print(align(email, "SID update required..."))
                except Exception as e:
                    print(align(email, str(e)))
            else:
                print(align(email, "Community error"))

    def join_bots_to_chat(self, object_id, account: dict):
        email = account.get("email")
        client = Login().login_sid(account)
        if client:
            sub_client = Community().sub_client(self.com_id, client)
            if sub_client:
                try:
                    sub_client.join_chat(chatId=object_id)
                    print(align(email, "Join"))
                except amino.exceptions.YouAreBanned:
                    print(align(email, "You are banned"))
                except amino.exceptions.RemovedFromChat:
                    print(align(email, "You are removed from this chatroom"))
                except amino.exceptions.InvalidSession:
                    print(align(email, "SID update required..."))
                except Exception as e:
                    print(align(email, str(e)))
            else:
                print(align(email, "Community error"))

    def leave_bots_from_chat(self, object_id, account: dict):
        email = account.get("email")
        client = Login().login_sid(account)
        if client:
            sub_client = Community().sub_client(self.com_id, client)
            if sub_client:
                try:
                    sub_client.leave_chat(chatId=object_id)
                    print(align(email, "Leave"))
                except amino.exceptions.YouAreBanned:
                    print(align(email, "You are banned"))
                except amino.exceptions.RemovedFromChat:
                    print(align(email, "You are removed from this chatroom"))
                except amino.exceptions.InvalidSession:
                    print(align(email, "SID update required..."))
                except Exception as e:
                    print(align(email, str(e)))
            else:
                print(align(email, "Community error"))

    def join_bots_to_community(self, inv_link=None, account: dict = None):
        email = account.get("email")
        client = Login().login_sid(account)
        if client:
            if inv_link:
                invitation_id = client.link_identify(code=str(inv_link.split("/")[-1])).get("invitationId")
                if invitation_id:
                    try:
                        client.join_community(comId=self.com_id, invitationId=invitation_id)
                        print(align(email, "Join"))
                    except amino.exceptions.InvalidSession:
                        print(align(email, "SID update required..."))
                    except Exception as e:
                        print(align(email, str(e)))
            else:
                try:
                    client.join_community(comId=self.com_id)
                    print(align(email, "Join"))
                except amino.exceptions.InvalidSession:
                    print(align(email, "SID update required..."))
                except Exception as e:
                    print(align(email, str(e)))

    def send_message(self, object_id, text, account: dict):
        email = account.get("email")
        client = Login().login_sid(account)
        if client:
            sub_client = Community().sub_client(self.com_id, client)
            if sub_client:
                try:
                    sub_client.send_message(chatId=object_id, message=text)
                    print(align(email, "Send"))
                except amino.exceptions.YouAreBanned:
                    print(align(email, "You are banned"))
                except amino.exceptions.RemovedFromChat:
                    print(align(email, "You are removed from this chatroom"))
                except amino.exceptions.ChatViewOnly:
                    print(align(email, "Chat in view only mode"))
                except amino.exceptions.AccessDenied:
                    print(align(email, "Access denied"))
                except amino.exceptions.InvalidSession:
                    print(align(email, "SID update required..."))
                except Exception as e:
                    print(align(email, str(e)))
            else:
                print(align(email, "Community error"))

    def follow(self, object_id, account: dict):
        email = account.get("email")
        client = Login().login_sid(account)
        if client:
            sub_client = Community().sub_client(self.com_id, client)
            if sub_client:
                try:
                    sub_client.follow(userId=object_id)
                    print(align(email, "Follow"))
                except amino.exceptions.YouAreBanned:
                    print(align(email, "You are banned"))
                except amino.exceptions.AccessDenied:
                    print(align(email, "Access denied"))
                except amino.exceptions.InvalidSession:
                    print(align(email, "SID update required..."))
                except Exception as e:
                    print(align(email, str(e)))
            else:
                print(align(email, "Community error"))

    def unfollow(self, object_id, account: dict):
        email = account.get("email")
        client = Login().login_sid(account)
        if client:
            sub_client = Community().sub_client(self.com_id, client)
            if sub_client:
                try:
                    sub_client.unfollow(userId=object_id)
                    print(align(email, "Unfollow"))
                except amino.exceptions.YouAreBanned:
                    print(align(email, "You are banned"))
                except amino.exceptions.AccessDenied:
                    print(align(email, "Access denied"))
                except amino.exceptions.InvalidSession:
                    print(align(email, "SID update required..."))
                except Exception as e:
                    print(align(email, str(e)))
            else:
                print(align(email, "Community error"))

    def set_online_status(self, account: dict):
        email = account.get("email")
        client = Login().login_sid(account)
        if client:
            sub_client = Community().sub_client(self.com_id, client)
            if sub_client:
                try:
                    sub_client.activity_status("on")
                    print(align(email, "Online status is set"))
                except amino.exceptions.YouAreBanned:
                    print(align(email, "You are banned"))
                except amino.exceptions.InvalidSession:
                    print(align(email, "SID update required..."))
                except Exception as e:
                    print(align(email, str(e)))
            else:
                print(align(email, "Community error"))

    def change_nick_random(self, max_length, nick, account: dict):
        email = account.get("email")
        client = Login().login_sid(account)
        if client:
            sub_client = Community().sub_client(self.com_id, client)
            if sub_client:
                try:
                    if nick is None:
                        nick = UsernameGenerator(2, max_length).generate()
                    sub_client.edit_profile(nickname=nick)
                    print(align(email, f"Nickname changed to {nick}"))
                except amino.exceptions.YouAreBanned:
                    print(align(email, "You are banned"))
                except amino.exceptions.InvalidSession:
                    print(align(email, "SID update required..."))
                except Exception as e:
                    print(align(email, str(e)))
            else:
                print(align(email, "Community error"))

    def change_icon_random(self, images: list, account: dict):
        email = account.get("email")
        client = Login().login_sid(account)
        if client:
            sub_client = Community().sub_client(self.com_id, client)
            if sub_client:
                try:
                    with open(os.path.join(os.getcwd(), "src", "icons", f"{random.choice(images)}"), "rb") as file:
                        icon = client.upload_media(file, "image")
                    sub_client.edit_profile(icon=icon)
                    print(align(email, "Icon changed"))
                except amino.exceptions.YouAreBanned:
                    print(align(email, "You are banned"))
                except amino.exceptions.InvalidSession:
                    print(align(email, "SID update required..."))
                except Exception as e:
                    print(align(email, str(e)))
            else:
                print(align(email, "Community error"))

    def wall_comment(self, userid: str, text: str, account: dict):
        email = account.get("email")
        client = Login().login_sid(account)
        if client:
            sub_client = Community().sub_client(self.com_id, client)
            if sub_client:
                try:
                    sub_client.comment(message=text, userId=userid)
                    print(align(email, "Comment sent"))
                except amino.exceptions.YouAreBanned:
                    print(align(email, "You are banned"))
                except amino.exceptions.InvalidSession:
                    print(align(email, "SID update required..."))
                except Exception as e:
                    print(align(email, str(e)))
            else:
                print(align(email, "Community error"))

    def vote_poll(self, blog_id: str, option_id: str, account: dict):
        email = account.get("email")
        client = Login().login_sid(account)
        if client:
            sub_client = Community().sub_client(self.com_id, client)
            if sub_client:
                try:
                    sub_client.vote_poll(blogId=blog_id, optionId=option_id)
                    print(align(email, "Comment sent"))
                except amino.exceptions.YouAreBanned:
                    print(align(email, "You are banned"))
                except amino.exceptions.InvalidSession:
                    print(align(email, "SID update required..."))
                except Exception as e:
                    print(align(email, str(e)))
            else:
                print(align(email, "Community error"))


class ChatModeration:
    def __init__(self):
        self.com_id = None
        self.client = None

    def clear_chat(self, chatid: str, count: int):
        print("Clearing chat...")
        pool = ThreadPool(50)
        deleted = 0
        next_page = None
        back = False
        sub_client = Community().sub_client(self.com_id, self.client)
        chat = sub_client.get_chat_thread(chatId=chatid)
        admins = [*chat.coHosts, chat.author.userId]
        if self.client.userId in admins:
            while not back:
                messages = sub_client.get_chat_messages(chatId=chatid, size=100, pageToken=next_page)
                if messages.messageId:
                    next_page = messages.nextPageToken
                    for message_id in messages.messageId:
                        if deleted < count:
                            pool.apply_async(sub_client.delete_message, [chatid, message_id, False, None])
                            deleted += 1
                        else:
                            back = True
                            break
                else:
                    break
        else:
            print(colored("You don't have co-host/host rights to use this function", "red"))

    def save_chat_settings(self, chatid: str):
        if os.path.exists(os.path.join(os.getcwd(), "src", "chat_settings")):
            pass
        else:
            os.mkdir(os.path.join(os.getcwd(), "src", "chat_settings"))
        sub_client = Community().sub_client(self.com_id, self.client)
        with open(os.path.join(os.getcwd(), "src", "chat_settings", f"{chatid}.txt"), "w", encoding="utf-8") as settings_file:
            chat = sub_client.get_chat_thread(chatId=chatid)
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
        print(colored(f"Settings saved in {os.path.join(os.getcwd(), 'src', 'chat_settings', f'{chatid}.txt')}", "green"))

    def set_view_mode(self, chatid: str):
        sub_client = Community().sub_client(self.com_id, self.client)
        chat = sub_client.get_chat_thread(chatId=chatid)
        admins = [*chat.coHosts, chat.author.userId]
        if self.client.userId in admins:
            sub_client.edit_chat(chatId=chatid, viewOnly=True)
            print("Chat mode is set to view")
        else:
            print(colored("You don't have co-host/host rights to use this function", "red"))

    def set_view_mode_timer(self, chatid: str, duration: int):
        sub_client = Community().sub_client(self.com_id, self.client)
        chat = sub_client.get_chat_thread(chatId=chatid)
        admins = [*chat.coHosts, chat.author.userId]
        if self.client.userId in admins:
            sub_client.edit_chat(chatId=chatid, viewOnly=True)
            print("Chat mode is set to view")
            while duration > 0:
                print(f"{duration} seconds left")
                duration -= 1
                time.sleep(1)
            sub_client.edit_chat(chatId=chatid, viewOnly=False)
            print("View mode disabled")
        else:
            print(colored("You don't have co-host/host rights to use this function", "red"))


class Badass:
    def __init__(self):
        self.com_id = None
        self.client = None

    def send_system_message(self, chatid: str):
        sub_client = Community().sub_client(self.com_id, self.client)
        sub_client.join_chat(chatid)
        back = False
        while not back:
            message_type = int(input("Message type: "))
            message = input("Message: ")

            try:
                sub_client.send_message(chatId=chatid, messageType=message_type, message=message)
                print("Message sent")
            except amino.exceptions.ChatViewOnly:
                print(colored("Chat is in only view mode", "red"))
            except:
                pass
            choice = input("Send again?(y/n): ")
            if choice.lower() == "n":
                back = True

    def spam_system_message(self, chatid: str):
        sub_client = Community().sub_client(self.com_id, self.client)
        pool_count = int(input("Number of threads: "))
        pool = ThreadPool(pool_count)
        count_messages = int(input("Number of messages: "))
        message_type = int(input("Message type: "))
        message = input("Message: ")
        sub_client.join_chat(chatid)
        back = False
        while not back:
            for _ in range(count_messages):
                print("Message sent")
                pool.apply_async(sub_client.send_message, [chatid, message, message_type])
            choice = input("Spam again?(y/n): ")
            if choice.lower() == "n":
                back = True

    def delete_chat(self, chatid: str):
        sub_client = Community().sub_client(self.com_id, self.client)
        chat = sub_client.get_chat_thread(chatId=chatid)
        admins = [*chat.coHosts, chat.author.userId]
        if self.client.userId in admins:
            sub_client.kick(chatId=chatid, allowRejoin=False, userId=chat.author.userId)
            print("Chat deleted")
        else:
            print(colored("You don't have co-host/host rights to use this function", "red"))

    def invite_all_users(self, chatid: str):
        sub_client = Community().sub_client(self.com_id, self.client)
        pool = ThreadPool(20)
        for i in range(0, 10000, 100):
            users = sub_client.get_online_users(start=i, size=100).profile.userId
            if users:
                for userid in users:
                    print(f"{userid} Invited to chat")
                    pool.apply_async(sub_client.invite_to_chat, [userid, chatid])
            else:
                break
        print("All online users invited to chat")

    def spam_posts(self):
        sub_client = Community().sub_client(self.com_id, self.client)
        pool_count = int(input("Number of threads: "))
        pool = ThreadPool(pool_count)
        posts_count = int(input("Number of posts: "))
        title = input("Post title: ")
        content = input("Post content: ")
        back = False
        while not back:
            for i in range(posts_count):
                print("Post sent")
                pool.apply_async(sub_client.post_blog, [title, content])
            choice = input("Send again?(y/n): ")
            if choice.lower() == "n":
                back = True
