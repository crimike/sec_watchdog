import telegram
from watchdog.events import FileSystemEventHandler
import logging

class AuthEventHandler(FileSystemEventHandler):
    
    def __init__(self, config, notify_function):
        super().__init__()
        self.path = config['log_path']
        self.tell = 0
        self.notify = notify_function
        self.logger = logging.getLogger(__name__)
        #self.logging = logging.getLogger(__name_)
        #self.logging.basicConfig(

    def parse_log(self, log):
        self.logger.info("Handling information from the log")
        for line in log.split('\n'):
            self.logger.debug(line)
            if 'sshd' in line:
                # SSH event
                self.logger.info("SSH event encountered")
                evt = ''.join(line.split(':')[3:])
                #if '[preauth]' not in evt:
                    # preauth fails before authentication
                if 'session closed for user' not in evt and 'session opened for user' not in evt and 'Did not receive identification string from' not in evt and 'Connection closed by' not in evt and 'Received disconnect from' not in evt and 'Disconnected from invalid user' not in evt and 'Disconnected from authenticating' not in evt:
                    self.notify(evt)
            if 'sudo: ' in line:
                # Sudo event
                self.logger.info("Sudo event encountered")
                evt = ''.join(line.split('sudo: ')[1:])
                if 'session closed for user' not in evt and 'session opened for user' not in evt:
                    self.notify(evt)
                

    def dispatch(self, event):
        if event.src_path == self.path:
            self.logger.debug("Dispatching modified event for " + event.src_path)
            super().dispatch(event)

    def on_modified(self, event):
        self.logger.info("Modification event is being handled for " + event.src_path)
        f = open(event.src_path,'r')
        if self.tell == 0:
            # new file, parse last line
            self.logger.info("First time a modification was recorded for this file, grabbing last line")
            log = f.readlines()[-1]
            self.parse_log(log)
            self.tell = f.tell()
            self.logger.debug("Setting new tell to " + str(self.tell))
        else:
            f.read()
            new_tell = f.tell()
            self.logger.debug("File length is " + str(new_tell))
            if new_tell < self.tell:
                # new file is shorter than previous - logrotate for example
                self.logger.debug("New file is shorter than previous, parsing everything")
                f.seek(0)
                log = f.read()
                self.parse_log(log)
                self.tell = new_tell
                self.logger.debug("Setting new tell to " + str(new_tell))
            else:
                # content was added to the file
                self.logger.debug("Content was added to " + event.src_path)
                f.seek(self.tell)
                log = f.read()
                self.parse_log(log)
                self.tell = f.tell()
                self.logger.debug("Setting new tell to " + str(self.tell))

        f.close()


