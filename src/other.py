import json
import os

import yaml


def get_accounts():
    with open(os.path.join(os.getcwd(), "src", "accounts", "bots.yaml"), "r") as accounts_file:
        return yaml.load(accounts_file.read(), Loader=yaml.Loader)


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


def set_auth_data(data):
    get_data = list(get_auth_data())
    get_data.append(data)
    with open(os.path.join(os.getcwd(), "src", "auth", "data.json"), "w") as auth_data_file:
        json.dump(get_data, auth_data_file, indent=2)


def converter():
    with open(os.path.join(os.getcwd(), "src", "accounts", "bots.txt"), "r") as bots_file:
        bots = bots_file.readlines()
        accounts = get_accounts()
        print(accounts)
        if accounts is None:
            accounts = []
        for i in bots:
            split = i.replace(" ", "").split(":")
            accounts.append({"email": split[0], "password": split[1].replace("\n", "")})
    with open(os.path.join(os.getcwd(), "src", "accounts", "bots.yaml"), "w") as accounts_file:
        yaml.dump(accounts, accounts_file, Dumper=yaml.Dumper)


def align(email: str, action: str):
    spaces = 30 - len(email)
    text = f"[{email}"
    text += " "*spaces
    text += f"]: {action}"
    return text
