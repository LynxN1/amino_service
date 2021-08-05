import asyncio
import time
import traceback

from src import database, amino_async, configs
from src.utils import service_align, logger, file_logger


DEVICES = open(configs.DEVICES_PATH, "r").readlines()


async def login(account: tuple):
    client = amino_async.Client()
    email = account[0]
    password = account[1]
    while True:
        try:
            await client.login(email, password)
            return client
        except amino_async.utils.exceptions.ActionNotAllowed:
            client.device_id = client.headers.device_id = random.choice(DEVICES).strip()
        except amino_async.utils.exceptions.VerificationRequired as verify:
            logger.error("[" + email + "]: " + str(verify.args[0]["url"]))
            await client.session.close()
            return False
        except Exception as e:
            logger.error("[" + email + "]: " + e.args[0]["api:message"])
            file_logger.debug(traceback.format_exc())
            await client.session.close()
            return False


async def login_sid(account: tuple):
    email = account[0]
    sid = account[2]
    is_valid = account[3]
    if is_valid == 1:
        client = amino_async.Client()
        while True:
            try:
                await client.login_sid(sid)
                return client
            except amino_async.utils.exceptions.ActionNotAllowed:
                client.device_id = client.headers.device_id = random.choice(DEVICES).strip()
            except amino_async.utils.exceptions.VerificationRequired as verify:
                service_align(email, verify.args[0]["url"], level="error")
                await client.session.close()
                return False
            except Exception as e:
                service_align(email, e.args[0]["api:message"], level="error")
                file_logger.debug(traceback.format_exc())
                await client.session.close()
                return False


async def check_accounts():
    accounts = database.get_bots()
    invalids = []
    bads = []
    for i in accounts:
        sid = i[2]
        is_valid = i[3]
        valid_time = i[4]
        if is_valid == 0:
            invalids.append(i)
            continue
        if sid is None or valid_time is None or is_valid is None:
            bads.append(i)
            continue
        if valid_time <= int(time.time()):
            bads.append(i)
            continue
    if invalids:
        logger.warning(f"{len(invalids)} нерабочих аккаунтов")
    if bads:
        logger.warning(f"{len(bads)} аккаунтов поставлено в очередь для обновления SID...")
        valid_list = await asyncio.gather(*[asyncio.create_task(update_sid(i)) for i in bads])
        for i in valid_list:
            database.remove_bot(i.get("email"))
        database.set_bots(list(valid_list))


async def update_sid(account: tuple):
    email = account[0]
    password = account[1]
    client = await login(account)
    if client:
        service_align(email, "SID обновлён")
        await client.session.close()
        return {"email": email, "password": password, "sid": client.sid, "isValid": True, "validTime": int(time.time()) + 43200}
    else:
        return {"email": email, "password": password, "isValid": False}
