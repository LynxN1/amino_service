import os
import yaml

from termcolor import colored


def get_accounts():
    with open(os.getcwd() + "/src/accounts/bots.yaml", "r") as accounts_file:
        return yaml.load(accounts_file.read(), Loader=yaml.Loader)


def get_comments():
    with open(os.getcwd() + "/src/activity/comments.txt", "r", encoding="utf-8") as comments_file:
        return comments_file.readlines()


def get_devices():
    with open(os.getcwd() + "/src/devices/devices.txt", "r") as devices_file:
        return devices_file.readlines()


def get_reg_devices():
    with open(os.getcwd() + "/src/devices/reg_devices.txt", "r") as reg_devices_file:
        return reg_devices_file.readlines()


def get_count(values: list):
    total_count = 0
    total_accounts = 0
    for i in values:
        if type(i) == int:
            total_accounts += 1
            total_count += i
    return {"count": total_count, "accounts": total_accounts}


def set_bots():
    accounts = []
    with open(os.getcwd() + "/src/accounts/bots.txt", "r") as bots_file:
        bots = bots_file.readlines()
    for account in bots:
        split = account.split(":")
        email = split[0].replace("\n", "")
        password = split[1].replace("\n", "")
        accounts.append({"email": email, "password": password})
    with open(os.getcwd() + "/src/accounts/bots.yaml", "a") as accounts_file:
        yaml.dump(accounts, accounts_file, Dumper=yaml.Dumper)
    print("Ready!")


def set_pool_count():
    if len(get_accounts()) >= 10:
        while True:
            processes = input("Set the number of threads(1-50): ")
            if 50 >= int(processes) >= 1:
                return int(processes)
            else:
                print(colored("The number of threads must be from 1 to 50", "red"))
    else:
        return len(get_accounts()) if len(get_accounts()) <= 10 else 10
