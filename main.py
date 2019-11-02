from telegram.ext import Updater
import logging

from telegram.ext import CommandHandler
import os

TOKEN = "AAG05g6L0oqNSGLYyGuGBwDPDdNexGXrFRA"
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

updater = Updater(TOKEN)
PORT = int(os.environ.get('PORT', '8443'))

dispatcher = updater.dispatcher


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


updater.start_webhook(listen='0.0.0.0',
                      port=PORT,
                      url_path=TOKEN)

updater.bot.set_webhook("https://polar-bayou-80647.herokuapp.com/" + TOKEN)
updater.idle()
