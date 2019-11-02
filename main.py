from telegram.ext import Updater
import logging

from telegram.ext import CommandHandler
import os
import sys

MODE = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger()

updater = Updater(TOKEN)
PORT = int(os.environ.get('PORT', '8443'))

dispatcher = updater.dispatcher


def start_handler(bot, update):
    logger.info("User {} started bot".format(update.effective_user["id"]))
    update.message.reply_text("Hello from Python!\nPress /random to get random number")


if MODE == "dev":
    def run(updater):
        updater.start_polling()
elif MODE == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
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

    run(updater)

