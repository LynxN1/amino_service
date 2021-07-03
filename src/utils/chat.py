import amino_async
from src.utils.logger import logger


async def get_chat_id(sub_client: amino_async.SubClient):
    logger.info("1 - Выбрать чат из списка")
    logger.info("2 - Выбрать чат по ссылке")
    choice = int(input(">>> "))
    if choice == 1:
        chats = await sub_client.get_chat_threads(start=0, size=100)
        if not chats.chatId:
            raise Exception("Список чатов пуст")
        for x, title in enumerate(chats.title, 1):
            logger.info(f"{x}. {title}")
        index = input("Select chat: ")
        if int(index) <= 0 or int(index) > len(chats.chatId):
            raise Exception("Invalid chat number")
        return chats.chatId[int(choice)-1]
    if choice == 2:
        link = input("Ссылка: ")
        from_code = await sub_client.client.get_from_code(link.split("/")[-1])
        return from_code.objectId
