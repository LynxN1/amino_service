import amino


def send_coins(client, account: str, x: int, blog_id: str, com_id: str):
    try:
        email = account[0]
        password = account[1]
        while True:
            try:
                print(f"[{x}][Login][{email}]: {client.login(email=email, password=password)}")
                break
            except amino.exceptions.ActionNotAllowed:
                input(f"[{x}]Wait to VPN...")
                continue

        sub_client = amino.SubClient(comId=com_id, profile=client.profile)

        coins = int(client.get_wallet_info().totalCoins)
        if coins == 0:
            print(f"[{x}][NotEnoughCoins][email {email}]")
            return

        try:
            print(f"[{x}][send_coins]: {sub_client.send_coins(coins=coins, blogId=blog_id)}")
        except amino.exceptions.NotEnoughCoins:
            print(f"[{x}][NotEnoughCoins][coins {coins}][email {email}]")
            return
        except amino.exceptions.InvalidRequest:
            print(f"[{x}][InvalidRequest][coins {coins}][email {email}]")
            return
        print(f"[{x}]{coins} монет отправлено.")
        return
    except Exception as e:
        print(f"[{x}][send_coins][Exception]: {e}")
