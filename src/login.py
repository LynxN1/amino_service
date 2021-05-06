import os
import random
import time
from multiprocessing.pool import ThreadPool

import yaml

import amino
from src.other import align, get_accounts


def login(account: dict):
    client = amino.Client()
    email = account.get("email")
    password = account.get("password")
    while True:
        try:
            client.login(email, password)
            return client
        except amino.exceptions.ActionNotAllowed:
            client.device_id = client.headers.device_id = random.choice(open(os.path.join(os.getcwd(), "src", "devices", "devices.txt"), "r").readlines()).replace("\n", "")
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
        except Exception as e:
            print(align(email, str(e)))
            return False


def login_sid(account: dict):
    client = amino.Client()
    email = account.get("email")
    sid = account.get("sid")
    is_valid = account.get("isValid")
    if is_valid:
        while True:
            try:
                client.login_sid(sid)
                return client
            except amino.exceptions.ActionNotAllowed:
                client.device_id = client.headers.device_id = random.choice(open(os.path.join(os.getcwd(), "src", "devices", "devices.txt"), "r").readlines()).replace("\n", "")
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
            except Exception as e:
                print(align(email, str(e)))
                return False


def check_sid():
    accounts = get_accounts()
    bads = []
    for i in accounts:
        if i.get("sid") is None or i.get("validTime") is None or i.get("isValid") is None:
            bads.append(i)
            continue
        if i.get("validTime") <= int(time.time()):
            bads.append(i)
            continue
    if bads:
        print(f"{len(bads)} invalid accounts, start fixing...")
        pool = ThreadPool(100)
        valid_list = pool.map(update_sid, bads)
        with open(os.path.join(os.getcwd(), "src", "accounts", "bots.yaml"), "w") as accounts_file:
            yaml.dump(valid_list, accounts_file, Dumper=yaml.Dumper)


def update_sid(account: dict):
    email = account.get("email")
    password = account.get("password")
    client = login(account)
    if client:
        return {"email": email, "password": password, "sid": client.sid, "isValid": True, "validTime": int(time.time()) + 43200}
    else:
        return {"email": email, "password": password, "isValid": False}
