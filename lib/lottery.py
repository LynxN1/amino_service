import amino


def lottery(client, account: str, x: int, com_id: str):
    try:
        email = account[0]
        password = account[1]
        while True:
            try:
                print(f"[{x}][Login][{email}]: {client.login(email=email, password=password)}")
                break
            except amino.exceptions.ActionNotAllowed:
                input(f"[{x}]: Wait to VPN...")
            except amino.exceptions.FailedLogin:
                print(f"[{x}]: Failed Login")
                return
            except amino.exceptions.InvalidAccountOrPassword:
                print(f"[[{x}]: Invalid account or password.")
                return
            except amino.exceptions.InvalidPassword:
                print(f"[{x}]: Invalid Password")
                return
            except amino.exceptions.InvalidEmail:
                print(f"[{x}]: Invalid Email")
                return

        sub_client = amino.SubClient(comId=com_id, profile=client.profile)

        try:
            sub_client.lottery()
        except amino.exceptions.AlreadyPlayedLottery:
            print(f"[{x}][AlreadyPlayedLottery]")
            return
        except Exception as e:
            print(f"[{x}][Exception]: {e}")
            return
        return
    except Exception as e:
        print(f"[{x}][lottery][Exception]: {e}")
