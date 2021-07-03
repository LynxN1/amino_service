import asyncio
import time

from client import Client
from sub_client import SubClient


# Иницилизация и запуск потоков
# await asyncio.gather(*[asyncio.create_task(client.login("akinatamain@inpwa.com", "b66ixib0tez")) for _ in range(2)])


client = Client()


async def main():
    start_time = time.time()
    await client.login("akinata888@inpwa.com", "Lyxn1God")
    sub_client = SubClient("156542274", client)
    a = await asyncio.gather(*[asyncio.create_task(test(sub_client)) for _ in range(100)])
    print(a)
    await client.session.close()
    print(f"Time: {time.time() - start_time}")


async def test(sub_client):
    return sub_client.client.userId


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
