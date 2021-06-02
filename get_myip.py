from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging


class GetMyIp():

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.logger = logging.getLogger(__name__)


    def handler(self, update: Update, _: CallbackContext) -> None:
        if str(update.message.chat_id) != self.chat_id:
            self.logger.warning("Different chat tried to access this command")
        else:
            update.message.reply_text("My ip is")
