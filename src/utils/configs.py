import os

LOG_FILE_PATH = os.path.join(os.getcwd(), "log.log")
DATABASE_PATH = os.path.join(os.getcwd(), "database.db")
ICONS_PATH = os.path.join(os.getcwd(), "src", "icons")
CHAT_SETTINGS_PATH = os.path.join(os.getcwd(), "src", "chat_settings")
BOTS_TXT_PATH = os.path.join(os.getcwd(), "src", "bots.txt")

CHOICE_ACTION_TEXT = "Выберите действие: "

CATEGORY_NAMES = [
    "Основной аккаунт",
    "Управление ботами",
    "Модерация чата",
    "Рейды"
]

MAIN_MENU = [
    ["0", "Добавить аккаунты в базу данных (bots.txt -> database.db)"],
    ["1", CATEGORY_NAMES[0]],
    ["2", CATEGORY_NAMES[1]],
    ["3", CATEGORY_NAMES[2]],
    ["4", CATEGORY_NAMES[3]]
]

MAIN_ACCOUNT_MENU = [
    ["b", "Назад"],
    ["1", "Пройти викторину"],
    ["2", "Лайкать последние записи (+ комментарии при наличии)"],
    ["3", "Подписаться на всех"],
    ["4", "Очистить подписки"],
    ["5", "Список пользователей которые добавили вас в чс"],
    ["6", "Отправить монеты"]
]

BOTS_MANAGEMENT_MENU = [
    ["b", "Назад"],
    ["s", "Показать список ботов в базе данных"],
    ["d", "Удалить аккаунт бота с базы данных"],
    ["1", "Сыграть в лотерею"],
    ["2", "Отправить монеты"],
    ["3", "Лайкнуть пост"],
    ["4", "Закинуть ботов в чат"],
    ["5", "Удалить ботов из чата"],
    ["6", "Закинуть ботов в сообщество"],
    ["7", "Отправить сообщение в чат"],
    ["8", "Подписать ботов на пользователя"],
    ["9", "Отписать ботов от пользователя"],
    ["10", "Изменить никнейм"],
    ["11", "Оставить комментарий на стенке"],
    ["12", "Изменить аватарку"],
    ["13", "Начать чат с пользователем"]
]

CHAT_MODERATION_MENU = [
    ["b", "Назад"],
    ["1", "Очистить сообщения в чате"],
    ["2", "Сохранить настройки чата в текстовом документе"],
    ["3", "Установить режим просмотра"],
    ["4", "Установить режим просмотра (с таймером)"]
]

BADASS_MENU = [
    ["b", "Назад"],
    ["1", "Отправить системное сообщение"],
    ["2", "Спамить системными сообщениями"],
    ["3", "Пригласить всех активных участников сообщества в чат"],
    ["4", "Спам по всем общим чатам"],
    ["5", "Спам сис. сообщениями по всем общим чатам"]
]
