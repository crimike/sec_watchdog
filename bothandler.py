import telegram
import logging
from time import sleep

class BotHandler:

    def __init__(self, token, start_command = 'Start', chat_id = ''):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing bot ...")
        self.bot = telegram.Bot(token=token)
        self.logger.info('Bot ' + self.bot.getMe().full_name + ' successfully initialized')
        self.chat_id = chat_id
        if chat_id != '':
            self.logger.debug("Chat ID set to " + str(self.chat_id))
        self.start_command = start_command
        self.logger.debug("Start command set to " + self.start_command)

    def wait_for_user(self):
        self.logger.info('Start command is ' + self.start_command + ", waiting for users")
        while len(self.bot.get_updates()) == 0:
            sleep(5)

        upd = self.bot.get_updates()[0]
        self.logger.info('Got first message from ' + str(upd.message.from_user.username) + ':' + upd.message.text)
        while upd.message.text != self.start_command:
            while len(self.bot.get_updates(offset = upd.update_id + 1)) == 0:
                sleep(5)
            upd = self.bot.get_updates(offset = upd.update_id + 1)[0]
            self.logger.info('Got another message from ' + str(upd.message.from_user) + ':' + upd.message.text)
        self.bot.get_updates(offset = upd.update_id + 1)
        self.logger.info("Successfully registered user with chat id: " + str(upd.message.chat_id))
        self.bot.send_message(chat_id = upd.message.chat_id, text = "Connection successful, welcome!")
        return upd.message.chat_id

    def notify_user(self, message):
        if message == None or message == '':
            return
        self.logger.debug("Sending the following message to chat ID: " + str(self.chat_id))
        self.logger.debug(message)
        self.bot.send_message(chat_id = self.chat_id, text = message)

