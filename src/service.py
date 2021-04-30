import json
import os
import pathlib
from functools import partial
from multiprocessing.pool import ThreadPool

from termcolor import colored

import amino
from .login import login
from .other import get_accounts, get_count, set_auth_data, converter
from .scripts.badass import Badass
from .scripts.bot_management import BotManagement
from .scripts.chat_moderation import ChatModeration
from .scripts.create_accounts import CreateAccounts
from .scripts.single_management import SingleManagement


class ServiceApp:
    def __init__(self):
        accounts = json.load(open(os.path.join(os.getcwd(), "src", "auth", "data.json"), "r"))
        email = None
        password = None
        if accounts:
            print("Accounts:")
            for x, account in enumerate(accounts, 1):
                print(f"{x}. {account.get('email')}")
            choice = input("\nEnter \"+\" to add account\n>>> ")
            if choice == "+":
                email = input("Email: ")
                password = input("Password: ")
                set_auth_data({"email": email, "password": password})
            else:
                index = int(choice) - 1
                email = accounts[index].get("email")
                password = accounts[index].get("password")
        if not accounts:
            email = input("Email: ")
            password = input("Password: ")
            set_auth_data({"email": email, "password": password})

        self.client = login({"email": email, "password": password})
        if not self.client:
            print(colored("Failed login", "red"))
            exit(0)
        print(colored("Login was successful!", "green"))

        subs = self.client.sub_clients(start=0, size=100)
        for x, com_name in enumerate(subs.name, 1):
            print(f"{x}. {com_name}")
        self.sub_client = amino.SubClient(comId=subs.comId[int(input("Enter community number: ")) - 1], client=self.client)

        self.single_management = SingleManagement(self.sub_client)
        self.bot_management = BotManagement(self.sub_client)
        self.chat_moderation = ChatModeration(self.sub_client)
        self.badass = Badass(self.sub_client)

    def run(self):
        while True:
            try:
                print(colored(open("src/view/management_choice.txt", "r").read(), "cyan"))
                management_choice = input("Enter the number >>> ")
                if management_choice == "1":
                    while True:
                        print(colored(open("src/view/single_management.txt", "r").read(), "cyan"))
                        choice = input("Enter the number >>> ")
                        if choice == "1":
                            quiz_link = input("Quiz link: ")
                            object_id = self.client.get_from_code(str(quiz_link.split('/')[-1])).objectId
                            self.single_management.play_quiz(object_id)
                            print("[PlayQuiz]: Finish.")
                        elif choice == "2":
                            self.single_management.unfollow_all()
                            print("[UnfollowAll]: Finish.")
                        elif choice == "3":
                            self.single_management.like_recent_blogs()
                            print("[LikeRecentBlogs]: Finish.")
                        elif choice == "4":
                            self.single_management.follow_all()
                            print("[FollowAll]: Finish.")
                        elif choice == "5":
                            self.single_management.get_blocker_users()
                            print("[BlockerUsers]: Finish.")
                        elif choice == "6":
                            count = input("Number of coins: ")
                            blog_link = input("Blog link: ")
                            object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            self.single_management.send_coins(int(count), object_id)
                            print("[SendCoins]: Finish.")
                        elif choice == "b":
                            break
                elif management_choice == "2":
                    pool = ThreadPool(int(input("Number of threads: ")))
                    while True:
                        print(colored(open("src/view/bot_management.txt", "r").read(), "cyan"))
                        choice = input("Enter the number >>> ")
                        if choice == "1":
                            result = pool.map(self.bot_management.play_lottery, get_accounts())
                            count_result = get_count(result)
                            print(f"Accounts: {count_result['accounts']}\nResult: +{count_result['count']} coins")
                            print("[PlayLottery]: Finish.")
                        elif choice == "2":
                            blog_link = input("Blog link: ")
                            object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            result = pool.map(partial(self.bot_management.send_coins, object_id), get_accounts())
                            count_result = get_count(result)
                            print(f"Accounts {count_result['accounts']}\nResult: +{count_result['count']} coins")
                            print("[SendCoins]: Finish.")
                        elif choice == "3":
                            blog_link = input("Blog link: ")
                            object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.like_blog, object_id), get_accounts())
                            print("[LikeBlog]: Finish.")
                        elif choice == "4":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.join_bots_to_chat, object_id), get_accounts())
                            print("[JoinBotsToChat]: Finish.")
                        elif choice == "5":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.leave_bots_from_chat, object_id), get_accounts())
                            print("[LeaveBotsFromChat]: Finish.")
                        elif choice == "6":
                            subs = self.client.sub_clients(start=0, size=100)
                            for x, com_name in enumerate(subs.name, 1):
                                print(f"{x}. {com_name}")
                            object_id = subs.comId[int(input("Enter community number: ")) - 1]
                            invite_link = None
                            if self.client.get_community_info(object_id).joinType == 2:
                                invite_link = input("Enter invite link/code: ")
                            pool.map(partial(self.bot_management.join_bots_to_community, invite_link), get_accounts())
                            print("[JoinBotsToCommunity]: Finish.")
                        elif choice == "7":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            text = input("Message text: ")
                            pool.map(partial(self.bot_management.send_message, object_id, text), get_accounts())
                            print("[SendMessage]: Finish.")
                        elif choice == "8":
                            user_link = input("Link to user: ")
                            object_id = self.client.get_from_code(str(user_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.follow, object_id), get_accounts())
                            print("[Follow]: Finish.")
                        elif choice == "9":
                            user_link = input("Link to user: ")
                            object_id = self.client.get_from_code(str(user_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.unfollow, object_id), get_accounts())
                            print("[Unfollow]: Finish.")
                        elif choice == "10":
                            pool.map(self.bot_management.set_online_status, get_accounts())
                            print("[SetOnlineStatus]: Finish.")
                        elif choice == "11":
                            print("1 - Random nick")
                            print("2 - Set custom nick")
                            mode = input("Select mode: ")
                            if mode == "1":
                                max_length = int(input("Max nick length: "))
                                pool.map(partial(self.bot_management.change_nick_random, max_length, None), get_accounts())
                            else:
                                nick = input("Enter nick: ")
                                pool.map(partial(self.bot_management.change_nick_random, None, nick), get_accounts())
                            print("[ChangeNickname]: Finish.")
                        elif choice == "12":
                            user_link = input("User link: ")
                            userid = self.client.get_from_code(str(user_link.split('/')[-1])).objectId
                            text = input("Text: ")
                            pool.map(partial(self.bot_management.wall_comment, userid, text), get_accounts())
                            print("[WallComment]: Finish.")
                        elif choice == "13":
                            images = []
                            currentDirectory = pathlib.Path('src\\icons')
                            for currentFile in currentDirectory.iterdir():
                                images.append(str(currentFile).split("\\")[2])
                            if images:
                                pool.map(partial(self.bot_management.change_icon_random, images), get_accounts())
                            else:
                                print(colored("icons is empty", "red"))
                            print("[ChangeIcon]: Finish.")
                        elif choice == "14":
                            blog_link = input("Blog link: ")
                            object_id = self.client.get_from_code(str(blog_link.split('/')[-1])).objectId
                            polls = self.sub_client.get_blog_info(blogId=object_id).json["blog"]["polloptList"]
                            for x, i in enumerate(polls, 1):
                                print(f"{x}. {i.get('title')}")
                            option = polls[int(input("Select option number: ")) - 1]["polloptId"]
                            pool.map(partial(self.bot_management.vote_poll, object_id, option), get_accounts())
                            print("[Vote]: Finish.")
                        elif choice == "15":
                            object_link = input("User link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            pool.map(partial(self.bot_management.start_chat, object_id), get_accounts())
                            print("[StartChat]: Finish.")
                        elif choice == "b":
                            break
                elif management_choice == "3":
                    while True:
                        print(colored(open("src/view/chat_moderation.txt", "r").read(), "cyan"))
                        choice = input("Enter the number >>> ")
                        if choice == "1":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            count = input("Number of messages: ")
                            self.chat_moderation.clear_chat(object_id, int(count))
                            print("[ClearChat]: Finish.")
                        elif choice == "2":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            self.chat_moderation.save_chat_settings(object_id)
                            print("[SaveChatSettings]: Finish.")
                        elif choice == "3":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            self.chat_moderation.set_view_mode(object_id)
                            print("[SetViewMode]: Finish.")
                        elif choice == "4":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            duration = int(input("Duration in seconds: "))
                            self.chat_moderation.set_view_mode_timer(object_id, duration)
                            print("[SetViewMode]: Finish.")
                        elif choice == "b":
                            break
                elif management_choice == "4":
                    while True:
                        print(colored(open("src/view/badass.txt", "r").read(), "cyan"))
                        choice = input("Enter the number >>> ")
                        if choice == "1":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            self.badass.send_system_message(object_id)
                            print("[SendSystem]: Finish.")
                        elif choice == "2":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            self.badass.spam_system_message(object_id)
                            print("[SpamSystem]: Finish.")
                        elif choice == "3":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            self.badass.delete_chat(object_id)
                            print("[DeleteChat]: Finish.")
                        elif choice == "4":
                            object_link = input("Link: ")
                            object_id = self.client.get_from_code(str(object_link.split('/')[-1])).objectId
                            self.badass.invite_all_users(object_id)
                            print("[InviteAll]: Finish.")
                        elif choice == "5":
                            self.badass.spam_posts()
                            print("[SpamPosts]: Finish.")
                        elif choice == "b":
                            break
                elif management_choice == "5":
                    CreateAccounts().run()
                elif management_choice == "0":
                    converter()
            except Exception as e:
                print(colored(str(e), "red"))
