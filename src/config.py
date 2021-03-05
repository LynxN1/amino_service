import json
import os

import yaml


def get_accounts():
    with open(os.path.join(os.getcwd(), "src", "accounts", "bots.yaml"), "r") as accounts_file:
        return yaml.load(accounts_file.read(), Loader=yaml.Loader)


def get_comments():
    with open(os.path.join(os.getcwd(), "src", "activity", "comments.txt"), "r", encoding="utf-8") as comments_file:
        return comments_file.readlines()


def get_devices():
    with open(os.path.join(os.getcwd(), "src", "devices", "devices.txt"), "r") as devices_file:
        return devices_file.readlines()


def get_reg_devices():
    with open(os.path.join(os.getcwd(), "src", "devices", "reg_devices.txt"), "r") as reg_devices_file:
        return reg_devices_file.readlines()


def get_count(values: list):
    total_count = 0
    total_accounts = 0
    for i in values:
        if type(i) == int:
            total_accounts += 1
            total_count += i
    return {"count": total_count, "accounts": total_accounts}


def get_auth_data():
    with open(os.path.join(os.getcwd(), "src", "auth", "data.json"), "r") as auth_data_file:
        auth_data = json.load(auth_data_file)
        return auth_data


def set_pool_count():
    pool_count = len(get_accounts()) if len(get_accounts()) <= 50 else 50
    return pool_count


def set_accounts(data):
    with open(os.path.join(os.getcwd(), "src", "accounts", "bots.yaml"), "a") as accounts_file:
        yaml.dump(data, accounts_file, Dumper=yaml.Dumper)


def set_auth_data(data):
    with open(os.path.join(os.getcwd(), "src", "auth", "data.json"), "w") as auth_data_file:
        json.dump(data, auth_data_file, indent=2)


def converter():
    with open(os.path.join(os.getcwd(), "src", "accounts", "bots.txt"), "r") as bots_file:
        bots = bots_file.readlines()
        accounts = get_accounts()
        for i in bots:
            split = i.split(":")
            accounts.append({"email": split[0], "password": split[1].replace("\n", "")})
    with open(os.path.join(os.getcwd(), "src", "accounts", "bots.yaml"), "w") as accounts_file:
        yaml.dump(accounts, accounts_file, Dumper=yaml.Dumper)
