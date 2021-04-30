from multiprocessing.pool import ThreadPool

from termcolor import colored

import amino


class Badass:
    def __init__(self, sub_client: amino.SubClient):
        self.sub_client = sub_client

    def send_system_message(self, chatid: str):
        self.sub_client.join_chat(chatid)
        while True:
            message_type = int(input("Message type: "))
            message = input("Message: ")
            try:
                self.sub_client.send_message(chatId=chatid, messageType=message_type, message=message)
                print("Message sent")
            except amino.exceptions.ChatViewOnly:
                print(colored("Chat is in only view mode", "red"))
            except:
                pass
            choice = input("Repeat?(y/n): ")
            if choice.lower() == "n":
                break

    def spam_system_message(self, chatid: str):
        pool_count = int(input("Number of threads: "))
        pool = ThreadPool(pool_count)
        count_messages = int(input("Count of messages: "))
        message_type = int(input("Message type: "))
        message = input("Message: ")
        self.sub_client.join_chat(chatid)
        while True:
            for _ in range(count_messages):
                print("Message sent")
                pool.apply_async(self.sub_client.send_message, [chatid, message, message_type])
            choice = input("Repeat?(y/n): ")
            if choice.lower() == "n":
                break

    def delete_chat(self, chatid: str):
        chat = self.sub_client.get_chat_thread(chatId=chatid)
        admins = [*chat.coHosts, chat.author.userId]
        if self.sub_client.profile.userId in admins:
            self.sub_client.kick(chatId=chatid, allowRejoin=False, userId=chat.author.userId)
            print("Chat deleted")
        else:
            print(colored("You don't have co-host/host rights to use this function", "red"))

    def invite_all_users(self, chatid: str):
        pool = ThreadPool(100)
        count = 0
        for i in range(0, 10000, 100):
            users = self.sub_client.get_online_users(start=i, size=100).profile.userId
            if users:
                for userid in users:
                    pool.apply_async(self.sub_client.invite_to_chat, [userid, chatid])
                    count += 1
                    print(f"{count} users invited to chat", end="\r")
            else:
                break
        print("All online users invited to chat")

    def spam_posts(self):
        pool_count = int(input("Number of threads: "))
        pool = ThreadPool(pool_count)
        posts_count = int(input("Count of posts: "))
        title = input("Post title: ")
        content = input("Post content: ")
        while True:
            for i in range(posts_count):
                print("Post sent")
                pool.apply_async(self.sub_client.post_blog, [title, content])
            choice = input("Repeat?(y/n): ")
            if choice.lower() == "n":
                break
