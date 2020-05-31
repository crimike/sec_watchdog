import telegram
from wathcdog.events import FileSystemEventHandler
import logger

class AuthEventHandler(FileSystemEventHandler):
    
    def __init__(self, config, notify_function):
        super().__init__()
        self.path = config['log_path']
        self.tell = 0
        self.notify = notify_function
        #self.logger = logging.getLogger(__name_)
        #self.logger.basicConfig(

    def parse_log(log):
        for line in log:
            logger.debug(line)


    def dispatch(self, event):
        if event.src_path == self.path:
            logger.debug("Dispatching modified event for " + event.src_path)
            super().dispatch(event)

    def on_modified(self, event):
        logger.info("Modification event is being handled for " = event.src_path)
        f = open(event.src_path,'r')
        if self.tell == 0:
            # new file, parse everything
            logger.info("First time a modification was recorded for this file")
            log = f.read()
            parse_log(log)
            self.tell = f.tell()
            logger.debug("Setting new tell to " + str(self.tell))
        else:
            f.read()
            new_tell = f.tell()
            logger.debug("File length is " + str(new_tell))
            if new_tell < self.tell:
                # new file is shorter than previous - logrotate for example
                logger.debug("New file is shorter than previous, parsing everything")
                f.seek(0)
                log = f.read()
                parse_log(log)
                self.tell = new_tell
                logger.debug("Setting new tell to " + str(new_tell))
            else:
                # content was added to the file
                logger.debug("Content was added to " + event.src_path)
                f.seek(self.tell)
                log = f.read()
                parse_log(log)
                self.tell = f.tell()
                logger.debug("Setting new tell to " + str(self.tell))

        f.close()


