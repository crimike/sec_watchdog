from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging
import requests


class GetMyIp():

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.logger = logging.getLogger(__name__)

    def getIp():
        headers = {'User-Agent' : 'curl/7.68.0'}
        r = requests.get("http://ifconfig.co", headers = headers)
        return r.text


    def handler(self, update: Update, _: CallbackContext) -> None:
        if str(update.message.chat_id) != self.chat_id:
            self.logger.warning("Different chat tried to access this command")
        else:
            update.message.reply_text("My ip is " + getIp())
