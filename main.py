from telegram.ext import Updater
import logging
import psycopg2

from telegram.ext import CommandHandler
import os
import sys

MODE = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger()


def connect():
    return psycopg2.connect(database="postgres", user="saddam", password="root", host="127.0.0.1", port="5432")

    return psycopg2.connect("postgres://gssgzevclkgwcp:420864fc961167f10ebb989b644c811e44631943656b9424675b5a62e9b73d55"
                            "@ec2-174-129-253-68.compute-1.amazonaws.com:5432/d5cq83vubs3qhb", sslmode='require')


print("Database opened successfully")

updater = Updater(TOKEN)
PORT = int(os.environ.get('PORT', '8443'))

dispatcher = updater.dispatcher


def exist(chat_id):
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT COUNT(chat_id) as cnt from STUDENT WHERE chat_id = " + str(chat_id))
    cnt = cur.fetchall()[0][0]

    con.close()
    return cnt > 0


def start_handler(bot, update):
    logger.info("User {} started bot".format("Saddam"))

    if not exist(update.effective_user['id']):

        con = connect()
        cur = con.cursor()
        name = update.effective_user["first_name"]
        chat_id = update.effective_user["id"]
        user_name = update.effective_user["username"]
        cur.execute("INSERT INTO STUDENT (name, chat_id, user_name) VALUES ('{}', '{}', '{}')".format(name, chat_id,
                                                                                                      user_name))
        update.message.reply_text(
            "Hi! NU Secret Santa welcomes you! \nIf you want to create a game to play a Secret Santa with your friends "
            "just follow /create ! \n Or go through or /join to follow existing game!")
        con.commit()

        con.close()
        print("Record inserted successfully")
    else:

        update.message.reply_text(
            "Hi! You seem familiar to me! \nJust follow /create to create a game or /join to follow existing game")


def create_handler(bot, update):
    if not exist(update.effective_user['id']):
        update.message.reply_text(
            "Hi! You seem not registered. Follow /start please")

    con = connect()
    cur = con.cursor()
    cur.execute("SELECT COUNT(code) as cnt from game WHERE creator_id = " + str(update.effective_user['id']))
    cnt = cur.fetchall()[0][0]
    if cnt > 0:
        update.message.reply_text(
            "Hi! It seems you already leader at some game:)")
    else:
        name = update.effective_user["first_name"]
        chat_id = update.effective_user["id"]
        user_name = update.effective_user["username"]
        text = update.message['text']
        if len(text.split(' ')) <= 1:
            update.message.reply_text(
                "Hi! Please enter your unique game code")
            return
        elif len(text.split(' ')) > 2:
            update.message.reply_text(
                "Hi! Please enter your unique game code without any spaces. Thank you :)")
            return
        code = text.split(' ')[1]
        cur.execute("SELECT COUNT(code) as cnt from game WHERE code = '{}'".format(code))
        code_cnt = cur.fetchall()[0][0]
        if code_cnt > 0:
            update.message.reply_text(
                "Hi! Please enter another code. This one exists already. Thank you :)")
            return
        cur.execute("INSERT INTO game (code, name, creator_id) VALUES ('{}', '{}', '{}')".format(code, name,
                                                                                                 chat_id))
        cur.execute("INSERT INTO game_student (game_code, student_id) VALUES ('{}', '{}')".format(code, chat_id))
        update.message.reply_text(
            "Hi! Your game was created with unique code! Share it so that other can follow!"
            "\nAfter all players followed the game, you can go through /distribution")
        con.commit()

        con.close()
        print("Record inserted successfully")

    con.close()


def join_handler(bot, update):
    if not exist(update.effective_user['id']):
        update.message.reply_text(
            "Hi! You seem not registered. Follow /start please")

    name = update.effective_user["first_name"]
    chat_id = update.effective_user["id"]
    user_name = update.effective_user["username"]
    text = update.message['text']

    con = connect()
    cur = con.cursor()

    if len(text.split(' ')) == 1:
        update.message.reply_text(
            "Please send me in format /join <unique_code>. Thanks!")
        return
    code = text.split(' ')[1]
    cur.execute("SELECT COUNT(code) as cnt from game WHERE code = '{}'".format(code))
    code_cnt = cur.fetchall()[0][0]
    if code_cnt < 1:
        update.message.reply_text(
            "No any game with this unique code!")
        return
    try:
        cur.execute("INSERT INTO game_student (game_code, student_id) VALUES ('{}', '{}')".format(code, chat_id))
        con.commit()
        update.message.reply_text(
            "Great! You have been added to game {}".format(code))
    except psycopg2.Error:
        update.message.reply_text(
            "You are already in this game!".format(code))
    con.close()


def distribution_handler(bot, update):
    if not exist(update.effective_user['id']):
        update.message.reply_text(
            "Hi! You seem not registered. Follow /start please")
    name = update.effective_user["first_name"]
    chat_id = update.effective_user["id"]
    user_name = update.effective_user["username"]

    con = connect()
    cur = con.cursor()

    cur.execute("SELECT code FROM game WHERE creator_id = {}".format(chat_id))
    rows = cur.fetchall()
    if len(rows) == 0:
        update.message.reply_text(
            "You do not have any games at this moment!")
        return
    code = rows[0][0]

    players = list()
    cur.execute("SELECT student_id FROM game_student WHERE game_code = '{}'".format(code))
    rows = cur.fetchall()
    for row in rows:
        players.append(int(row[0]))
    print(players)
    for i, el in enumerate(players):
        pair = players[(i + 3) % len(players)]
        if len(players) == 3:
            pair = players[(i + 4) % len(players)]

        cur.execute("SELECT user_name FROM student WHERE chat_id = '{}'".format(pair))
        username = cur.fetchall()[0][0]
        bot.send_message(chat_id=el, text="You are preparing present for @{}".format(username))

    con.close()


if MODE == "dev":
    def run(updater):
        updater.start_polling()
elif MODE == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://nusecretsantabot.herokuapp.com/" + TOKEN)
else:
    logger.error("No MODE specified!")
    sys.exit(1)

if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN)
    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.dispatcher.add_handler(CommandHandler("create", create_handler))
    updater.dispatcher.add_handler(CommandHandler("join", join_handler))
    updater.dispatcher.add_handler(CommandHandler("distribution", distribution_handler))
    run(updater)
    con = connect()
    cur = con.cursor()
    cur.execute("CREATE TABLE student(name varchar(32),chat_id numeric PRIMARY KEY, user_name varchar(32));")
    cur.execute("CREATE TABLE game(code varchar(32) PRIMARY KEY, name varchar(32),creator_id numeric REFERENCES student (chat_id));")
    cur.execute("CREATE TABLE game_student(game_code varchar(32) references game(code), student_id numeric references student(chat_id),PRIMARY KEY (game_code, student_id));")
    con.commit()
    con.close()

# update.effective_user{'id': 247532533, 'first_name': 'Saddam', 'is_bot': False, 'last_name': 'Asmatullayev', 'username': 'sadda11_asm', 'language_code': 'ru'}
# update.message {'message_id': 26, 'date': 1572700228, 'chat': {'id': 247532533, 'type': 'private', 'username': 'sadda11_asm', 'first_name': 'Saddam', 'last_name': 'Asmatullayev'}, 'text': '/start', 'entities': [{'type': 'bot_command', 'offset': 0, 'length': 6}], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False, 'from': {'id': 247532533, 'first_name': 'Saddam', 'is_bot': False, 'last_name': 'Asmatullayev', 'username': 'sadda11_asm', 'language_code': 'ru'}}
