import telegram
from watchdog.events import FileSystemEventHandler
import logging

class AuthEventHandler(FileSystemEventHandler):
    
    def __init__(self, config, notify_function):
        super().__init__()
        self.path = config['log_path']
        self.tell = 0
        self.notify = notify_function
        #self.logging = logging.getLogger(__name_)
        #self.logging.basicConfig(

    def parse_log(self, log):
        logging.info("Handling information from the log")
        for line in log.split('\n'):
            if 'sshd' in line:
                # SSH event
                logging.info("SSH event encountered")
                logging.debug(line)
                evt = line.split(':')[3]
                if '[preauth]' not in evt:
                    # preauth fails before authentication
                    self.notify(evt)
            if 'sudo:' in line:
                # Sudo event
                logging.info("Sudo event encountered")
                logging.debug(line)
                evt = line.split('sudo:')[1]
                self.notify(evt)
                

    def dispatch(self, event):
        if event.src_path == self.path:
            logging.debug("Dispatching modified event for " + event.src_path)
            super().dispatch(event)

    def on_modified(self, event):
        logging.info("Modification event is being handled for " + event.src_path)
        f = open(event.src_path,'r')
        if self.tell == 0:
            # new file, parse last line
            logging.info("First time a modification was recorded for this file")
            log = f.readlines()[-1]
            self.parse_log(log)
            self.tell = f.tell()
            logging.debug("Setting new tell to " + str(self.tell))
        else:
            f.read()
            new_tell = f.tell()
            logging.debug("File length is " + str(new_tell))
            if new_tell < self.tell:
                # new file is shorter than previous - logrotate for example
                logging.debug("New file is shorter than previous, parsing everything")
                f.seek(0)
                log = f.read()
                self.parse_log(log)
                self.tell = new_tell
                logging.debug("Setting new tell to " + str(new_tell))
            else:
                # content was added to the file
                logging.debug("Content was added to " + event.src_path)
                f.seek(self.tell)
                log = f.read()
                self.parse_log(log)
                self.tell = f.tell()
                logging.debug("Setting new tell to " + str(self.tell))

        f.close()


