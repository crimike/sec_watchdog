import schedule
from timer_event import TimerEvent
import socket
import logging

class Host():
    
    def __init__(self, host):
        self.hostname = host.split(':')[0]
        self.port = int(host.split(':')[1])
        self.isDown = False

class PortAliveAlarm(TimerEvent):

    def __init__(self,config,notify_function):
        self.logger = logging.getLogger(__name__)
        self.notify = notify_function
        all_hosts = config['hosts'].split(',')
        self.hosts = []
        self.logger.debug("Registering " + str(all_hosts))
        for host in all_hosts:
            self.logger.info("Registering " + host + " for monitoring Port alive state")
            self.hosts.append(Host(host))
        

    def invoke(self):
        for host in self.hosts:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((host.hostname, host.port))
                if result != 0:
                    if host.isDown == False:
                        self.notify(host.hostname + ':' + str(host.port) + ' is not responding')
                        host.isDown = True
                        self.logger.info(host.hostname + ':' + str(host.port) + ' is not responding')
                else:
                    if host.isDown == True:
                        self.notify(host.hostname + ':' + str(host.port) + ' is back  up')
                        host.isDown = False
                        self.logger.info(host.hostname + ':' + str(host.port) + ' is back  up')
                sock.close()
            except Exception as e:
                self.logger.debug(e.message)
