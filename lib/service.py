import amino
import json

from pathlib import Path
from lib.lottery import lottery
from lib.send_coins import send_coins


class Service:
    def __init__(self):
        self.path = Path('lib/accounts/bots.json')
        self.bots = json.loads(self.path.read_text(encoding='utf-8'))

        self.client = amino.Client()

    def run(self):
        print("1. lottery\n2. send_coins")
        while True:
            try:
                inp = input(">>> ")
                com_id = input("Community ID: ")
                if inp == "1":
                    for x, account in enumerate(self.bots.items(), 1):
                        lottery(client=self.client, account=account, x=x, com_id=com_id)
                    print("[check_in]: Finish.")
                if inp == "2":
                    blog_id = input("Blog ID: ")
                    for x, account in enumerate(self.bots.items(), 1):
                        send_coins(client=self.client, account=account, x=x, blog_id=blog_id, com_id=com_id)
                    print("[send_coins]: Finish.")
            except Exception as e:
                print(e)
