import telegram
from watchdog.events import FileSystemEventHandler
import logging
import requests
import json

class NginxEventHandler(FileSystemEventHandler):
    
    def __init__(self, config, notify_function):
        super().__init__()
        self.path = config['log_path']
        self.tell = 0
        self.ips = set()
        self.api_key = config['api_key']
        self.notify = notify_function
        self.logger = logging.getLogger(__name__)

    def get_ip_location(self, ip_address):
        localization = ""
        try:
            data = requests.get(f'https://api.ipdata.co/{ip_address}?api-key={self.api_key}').json()
            localization =  data['city'] +" - " + data['country_name']
            if data['is_proxy']:
                localization += ', is_proxy'
                self.logger.info('IP is a proxy')
            if data['is_anonymous']:
                localization += ', is_anonymous'
                self.logger.info('IP is anonymous')
            if data['is_known_attacker']:
                localization += ', is_known_attacker'
                self.logger.info('IP is known attacker')
            if data['is_known_abuser']:
                localization += ', is_known_abuser'
                self.logger.info('IP is known abuser')
            if data['is_threat']:
                localization += ', is_threat'
                self.logger.info('IP is a threat')
        except Exception as e:
            self.logger.info("Exception at getting localization for IP " + ip_address)
            self.logger.debug(str(e))
        return localization


    def parse_log(self, log):
        for line in log.split('\n'):
            self.logger.debug(line)
            if line == '' or line.isspace():
                continue
            elements = line.split('-')
            ip = elements[0].strip()
            self.logger.debug("Handling " + ip)
            if ip not in self.ips:
                self.ips.add(ip)
                localization = get_ip_location(ip)
                self.logger.info("New IP(" + ip + ") from " + localization)
                self.notify(ip + " - " + localization)    

    def dispatch(self, event):
        if event.src_path == self.path:
            self.logger.debug("Dispatching modified event for " + event.src_path)
            super().dispatch(event)

    def on_modified(self, event):
        self.logger.debug("Modification event is being handled for " + event.src_path)
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


