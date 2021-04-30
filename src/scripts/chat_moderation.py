import os
import time
from multiprocessing.pool import ThreadPool

from termcolor import colored

import amino


class ChatModeration:
    def __init__(self, sub_client: amino.SubClient):
        self.sub_client = sub_client

    def clear_chat(self, chatid: str, count: int):
        pool = ThreadPool(50)
        deleted = 0
        next_page = None
        back = False
        chat = self.sub_client.get_chat_thread(chatId=chatid)
        admins = [*chat.coHosts, chat.author.userId]
        if self.sub_client.profile.userId in admins:
            while not back:
                messages = self.sub_client.get_chat_messages(chatId=chatid, size=100, pageToken=next_page)
                if messages.messageId:
                    next_page = messages.nextPageToken
                    for message_id in messages.messageId:
                        if deleted < count:
                            pool.apply_async(self.sub_client.delete_message, [chatid, message_id, False, None])
                            deleted += 1
                            print(f"{deleted} messages deleted", end="\r")
                        else:
                            back = True
                            break
                else:
                    break
        else:
            print(colored("You don't have co-host/host rights to use this function", "red"))

    def save_chat_settings(self, chatid: str):
        if not os.path.exists(os.path.join(os.getcwd(), "src", "chat_settings")):
            os.mkdir(os.path.join(os.getcwd(), "src", "chat_settings"))
        with open(os.path.join(os.getcwd(), "src", "chat_settings", f"{chatid}.txt"), "w", encoding="utf-8") as settings_file:
            chat = self.sub_client.get_chat_thread(chatId=chatid)
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
        chat = self.sub_client.get_chat_thread(chatId=chatid)
        admins = [*chat.coHosts, chat.author.userId]
        if self.sub_client.profile.userId in admins:
            self.sub_client.edit_chat(chatId=chatid, viewOnly=True)
            print("Chat mode is set to view")
        else:
            print(colored("You don't have co-host/host rights to use this function", "red"))

    def set_view_mode_timer(self, chatid: str, duration: int):
        chat = self.sub_client.get_chat_thread(chatId=chatid)
        admins = [*chat.coHosts, chat.author.userId]
        if self.sub_client.profile.userId in admins:
            self.sub_client.edit_chat(chatId=chatid, viewOnly=True)
            print("Chat mode is set to view")
            while duration > 0:
                print(f"{duration} seconds left", end="\r")
                duration -= 1
                time.sleep(1)
            self.sub_client.edit_chat(chatId=chatid, viewOnly=False)
            print("View mode disabled")
        else:
            print(colored("You don't have co-host/host rights to use this function", "red"))
