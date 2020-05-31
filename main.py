import telegram
from time import sleep
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import configparser
import logging
import argparse
import importlib
import os

# TODO: functionality for restart 
# TODO: logging module to file

CHAT_ID = 'chat_id'
CONFIG_FILE = 'config.ini'
BOT_TOKEN = 'token'
START_COMMAND = 'start_command'
IMPORT_FILE = 'import_file'
CLASS_NAME = 'class_name'
LOG_PATH = 'log_path'


def read_config(filename):
    config = configparser.ConfigParser()
    logging.info("Reading the configuration from " + filename)
    config.read(filename)
    logging.info('Config file ' + filename + ' read')
    for section in config.sections():
        logging.debug('Found section ' + section)
        for key in config[section].keys():
            logging.debug('Read ' + key + ':' + config[section][key])
    return config

class BotHandler:

    def __init__(self, token, start_command = 'Start', chat_id = ''):
        logging.debug("Initializing bot with token: " + token)
        self.bot = telegram.Bot(token=token)
        logging.info('Bot ' + self.bot.getMe().full_name + ' successfully initialized')
        self.chat_id = chat_id
        if chat_id != '':
            logging.debug("Chat ID set to " + str(self.chat_id))
        self.start_command = start_command
        logging.debug("Start command set to " + self.start_command)

    def wait_for_user(self):
        logging.info('Start command is ' + self.start_command + ", waiting for users")
        while len(self.bot.get_updates()) == 0:
            sleep(5)

        upd = self.bot.get_updates()[0]
        logging.info('Got first message from ' + str(upd.message.from_user.username) + ':' + upd.message.text)
        while upd.message.text != self.start_command:
            while len(self.bot.get_updates(offset = upd.update_id + 1)) == 0:
                sleep(5)
            upd = self.bot.get_updates(offset = upd.update_id + 1)[0]
            logging.info('Got another message from ' + str(upd.message.from_user) + ':' + upd.message.text)
        self.bot.get_updates(offset = upd.update_id + 1)
        logging.debug('Chat id of user is ' + str(upd.message.chat_id))
        self.bot.send_message(chat_id = upd.message.chat_id, text = "Connection successful, welcome!")
        return upd.message.chat_id

    def notify_user(self, message):
        if message == None or message == '':
            return
        logging.debug("Sending the following message to chat ID: " + str(self.chat_id))
        logging.debug(message)
        self.bot.send_message(chat_id = self.chat_id, text = message)




# TODO: error checking

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = "Security watchdog")
    parser.add_argument("--debug", "-d", help = "Debug mode", action = 'store_true')
    parser.add_argument("--verbose", "-v", help = "Increase verbosity", action = 'store_true')
    parser.add_argument("--config", "-c",  help = "Configuration filename")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level = logging.DEBUG)
    elif args.verbose:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level = logging.INFO)
    else:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
        
    logging.info('Logging initialized')
    # read config
    if args.config != None:
        CONFIG_FILE = args.config
    print(CONFIG_FILE)
    config = read_config(CONFIG_FILE)

    bot = None

    if CHAT_ID not in list(config['MAIN'].keys()) or config['MAIN'][CHAT_ID] == '':
        bot = BotHandler(config['MAIN'][BOT_TOKEN], start_command = config['MAIN'][START_COMMAND])
        bot.wait_for_user()
    else:
        bot = BotHandler(config['MAIN'][BOT_TOKEN], chat_id = config['MAIN'][CHAT_ID])

    observers = []
    # go through each section, dinamically load the class   
    for section in config.sections():
        if section == 'MAIN':
            continue
        logging.debug("Importing " + config[section][IMPORT_FILE])
        module = importlib.import_module(config[section][IMPORT_FILE])
        o = Observer()
        logging.debug('Extracting class ' + config[section][CLASS_NAME])
        event_handler_class =   getattr(module, config[section][CLASS_NAME])
        event_handler = event_handler_class(config[section], bot.notify_user)
        # check if terminator is there, or if its a file
        logging.debug("Scheduling event handler for path " + os.path.dirname(config[section][LOG_PATH]))
        o.schedule(event_handler, os.path.dirname(config[section][LOG_PATH]))
        observers.append(o)


    for observer in observers:
        observer.start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        for observer in observers:
            observer.join()






