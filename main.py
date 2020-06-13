import telegram
from time import sleep
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import configparser
import logging
import argparse
import importlib
import os
from bothandler import BotHandler

# TODO: functionality for restart 
# TODO: logging module to file, with names

CHAT_ID = 'chat_id'
CONFIG_FILE = 'config.ini'
BOT_TOKEN = 'token'
START_COMMAND = 'start_command'
IMPORT_FILE = 'import_file'
CLASS_NAME = 'class_name'
LOG_PATH = 'log_path'
PREFIX = 'prefix'


def read_config(filename):
    config = configparser.ConfigParser()
    logger = logging.getLogger(__name__)
    config.read(filename)
    logger.info('Config file ' + filename + ' read')
    for section in config.sections():
        logger.debug('Found section ' + section)
        for key in config[section].keys():
            logger.debug('Read ' + key + ':' + config[section][key])
    return config



# TODO: error checking

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = "Security watchdog")
    parser.add_argument("--debug", "-d", help = "Debug mode", action = 'store_true')
    parser.add_argument("--verbose", "-v", help = "Increase verbosity", action = 'store_true')
    parser.add_argument("--config", "-c",  help = "Configuration filename")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format='%(asctime)s - %(levelname)s[%(name)s] - %(message)s', level = logging.DEBUG, datefmt = '%d/%m/%Y %H:%M:%S')
    elif args.verbose:
        logging.basicConfig(format='%(asctime)s - %(levelname)s[%(name)s] - %(message)s', level = logging.INFO, datefmt = '%d/%m/%Y %H:%M:%S')
    else:
        logging.basicConfig(format='%(asctime)s - %(levelname)s[%(name)s] - %(message)s', datefmt = '%d/%m/%Y %H:%M:%S')
        
    logger = logging.getLogger(__name__)
    logger.info('Logging initialized')
    # read config
    if args.config != None:
        CONFIG_FILE = args.config
    logger.debug('Reading config file ' + CONFIG_FILE)
    config = read_config(CONFIG_FILE)

    bot = None

    if CHAT_ID not in list(config['MAIN'].keys()) or config['MAIN'][CHAT_ID] == '':
        bot = BotHandler(config['MAIN'][BOT_TOKEN], start_command = config['MAIN'][START_COMMAND], prefix = config['MAIN'][PREFIX])
        bot.wait_for_user()
    else:
        bot = BotHandler(config['MAIN'][BOT_TOKEN], chat_id = config['MAIN'][CHAT_ID], prefix = config['MAIN'][PREFIX])

    observers = []
    # go through each section, dinamically load the class   
    for section in config.sections():
        if section == 'MAIN':
            continue
        logger.debug("Importing " + config[section][IMPORT_FILE])
        # TODO: add functionality for something to run regularly,not necessarily a filesystem watchdog
        module = importlib.import_module(config[section][IMPORT_FILE])
        o = Observer()
        logger.debug('Extracting class ' + config[section][CLASS_NAME])
        event_handler_class =   getattr(module, config[section][CLASS_NAME])
        event_handler = event_handler_class(config[section], bot.notify_user)
        file_path = config[section][LOG_PATH]
        if os.path.isfile(file_path):
            logger.debug("Scheduling event handler for path " + os.path.dirname(file_path))
            o.schedule(event_handler, os.path.dirname(file_path))
        elif os.path.isdir(file_path):
            logger.debug("Scheduling event handler for path " + file_path)
            o.schedule(event_handler, file_path)
        observers.append(o)


    logger.info("Starting observers")
    for observer in observers:
        observer.start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        logger.warning("CTRL + C detected, waiting for observers to finish")
        for observer in observers:
            observer.stop()
        for observer in observers:
            observer.join()






