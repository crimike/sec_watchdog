import schedule
from timer_event import TimerEvent
import requests
import logging

class Url():
    
    def __init__(self, url):
        self.url = url
        self.isDown = False

class HttpAliveAlarm(TimerEvent):

    def __init__(self,config,notify_function):
        self.logger = logging.getLogger(__name__)
        self.notify = notify_function
        all_urls = config['urls'].split(',')
        self.logger.debug("Registering " + str(all_urls))
        self.urls = []
        for url in all_urls:
            self.logger.info("Registering " + url + " for monitoring HTTP status every " + config['rtime'] + " minutes")
            self.urls.append(Url(url))
        

    def invoke(self):
        for url in self.urls:
            try:
                r = requests.get(url.url)
                if r.status_code == 200:
                    if url.isDown == True:
                        self.notify(url.url + " is back up and replying with 200")
                        self.logger.info(url.url + " is back up and replying with 200")
                        url.isDown = False
                else:
                    if url.isDown == False:
                        self.notify(url.url + " returned " + str(r.status_code))
                        self.logger.info(url.url + " returned " + str(r.status_code))
                        url.isDown = True
                r.close()
            except Exception as e:
                self.logger.debug(e)
                if url.isDown == False:
                    self.notify(url.url + " is not responding")
                    self.logger.info(url.url + ' is not responding')
                    url.isDown = True


