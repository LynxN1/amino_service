import random

import amino
from src.other import align


def login(account: dict):
    client = amino.Client()
    email = account.get("email")
    password = account.get("password")
    while True:
        try:
            client.login(email, password)
            return client
        except amino.exceptions.ActionNotAllowed:
            client.device_id = client.headers.device_id = random.choice(open("src\\devices\\devices.txt", "r").readlines()).replace("\n", "")
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
