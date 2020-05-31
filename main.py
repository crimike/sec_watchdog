import telegram
from time import sleep
from wathcdog.events import FileSystemEventHandler
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
    config.read(filename)
    logging.info('Config file ' + filename + ' read')
    logging.debug('DEFAULT section in config file:')
    for key in config['DEFAULT'].keys():
        logging.debug('Read ' + key + ':' config['DEFAULT'][key])
    for section in config.sections():
        logging.debug('Found section ' + section)
        for key in config[section].keys():
            logging.debug('Read ' + key + ':' + config[section][key])
    return config

class BotHandler:

    def __init__(self, token, start_command = 'Start', chat_id = ''):
        self.bot = telegram.Bot(token=token)
        logging.info('Bot ' + bot.getMe().full_name + ' successfully initialized')
        self.chat_id = chat_id
        logging.debug("Chat ID set to " + str(self.chat_id))
        self.start_command = start_command
        logging.debug("Start command set to " + self.start_command)

    def wait_for_user(self):
        logging.debug('Start command is ' + self.start_command)
        while len(self.bot.get_updates()) == 0:
            sleep(5)

        upd = self.bot.get_updates()[0]
        logging.info('Got first message from ' + upd.message.from_user + ':' + upd.message.text)
        while upd.message.text != self.start_command:
            while len(self.bot.get_updates(offset = upd.update_id + 1)) == 0:
                sleep(5)
            upd = self.bot.get_updates(offset = upd.update_id + 1)[0]
            logging.info('Got another message from ' + upd.message.from_user + ':' + upd.message.text)
        self.bot.get_updates(offset = upd.update_id + 1)
        logging.debug('Chat id of user is ' + upd.message.chat_id)
        self.bot.send_message(chat_id = upd.message.chat_id, text = "Connection successful, welcome!")
        return upd.message.chat_id

    def notify_user(self, message):
        logging.debug("Sending the following message to chat ID: " + str(self.chat_id))
        logging.debug(message)
        self.bot.send_message(chat_id = self.chat_id, text = message)




# TODO: error checking

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = "Security watchdog")
    parser.add_argument("-d", "--debug", help = "Debug mode", action = 'store_true')
    parser.add_argument("-v", "--verbose", help = "Increase verbosity", action = 'store_true')
    parser.add_argument("-c", "--config", help = "Configuration filename")
    parser.parse_args()

    if parser.debug:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level = logging.DEBUG)
    elif parser.verbose:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level = logging.INFO)
    else:
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
        
    logging.info('Logging initialized')
    # read config
    if parser.config != '':
        CONFIG_FILE = parser.config
    config = read_config(CONFIG_FILE)

    bot = None

    if CHAT_ID not in list(config['DEFAULT'].keys()) or config['DEFAULT'][CHAT_ID] == '':
        bot = BotHandler(config['DEFAULT'][BOT_TOKEN], start_command = config['DEFAULT'][START_COMMAND])
        bot.wait_for_user()
    else:
        bot = BotHandler(config['DEFAULT'][BOT_TOKEN], chat_id = config['DEFAULT'][CHAT_ID])

    observers = []
    # go through each section, dinamically load the class   
    for section in config.sections():
        logging.debug("Importing " + section[IMPORT_FILE])
        module = importlib.import(section[IMPORT_FILE])
        o = Observer()
        logging.debug('Extracting class ' + section[CLASS_NAME])
        event_handler_class =   getattr(module, section[CLASS_NAME])
        event_handler = event_handler_class(section, bot.notify_user)
        # check if terminator is there, or if its a file
        logging.debug("Scheduling event handler for path " + os.path.dirname(section[LOG_PATH]))
        o.schedule(event_handler, os.path.dirname(section[LOG_PATH]))
        observers.append(o)


    for observer in observers:
        observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for observer in observers:
            observer.join()






