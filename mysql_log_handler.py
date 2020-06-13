import telegram
from watchdog.events import FileSystemEventHandler
import logging
import os

class MysqlEventHandler(FileSystemEventHandler):
    
    def __init__(self, config, notify_function):
        super().__init__()
        self.path = config['log_path']
        self.notify = notify_function
        self.logger = logging.getLogger(__name__)
        #self.logging = logging.getLogger(__name_)
        #self.logging.basicConfig(

    def on_created(self, event):
        self.logger.info("Creation event is being handled for " + event.src_path)    
        self.notify(os.path.basename(event.src_path))