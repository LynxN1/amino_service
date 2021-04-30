import random

import yaml
from termcolor import colored

import amino
from src.nick_gen import UsernameGenerator


class CreateAccounts:
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
        reg_devices = open("src\\devices\\reg_devices.txt", "r").readlines()
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
                nick = UsernameGenerator(2, 10).generate()
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
                self.client.device_id = random.choice(open("src\\devices\\devices.txt", "r").readlines()).replace("\n", "")
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
        with open("src\\accounts\\created_accounts.yaml", "a") as accounts_file:
            yaml.dump([{"email": self.email, "password": self.password}], accounts_file, Dumper=yaml.Dumper)
        print(colored(f"{self.email} saved in created_accounts.yaml", "green"))

    def remove_device(self):
        devices = open("src\\devices\\reg_devices.txt", "r").readlines()
        devices.pop(0)
        with open("src\\devices\\reg_devices.txt", "w") as devices_file:
            for i in devices:
                devices_file.write(i)
