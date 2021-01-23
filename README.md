# Security Watchdog

Example config.ini attached

`chat_id` can also be added in the MAIN section to directly talk to someone

## Extending
Extending can be done by extending the a watchdog event handler

`__init__` function takes config and a notify function that is called to send the telegram message. 

Section config needs to contain at least the below entried to properly load. Others can be added and then later extracted from the config

## Config.ini

New section needs to be created for each extension
`import_file` is the file name, without `.py` ending
`class_name` is the class that extends the watchdog handler
`log_path` is the file or folder that is watched for changes

## Example config.ini

```
[MAIN]
token = xxx
start_command = Hai
chat_id = yyy
prefix = test


[AUTH]
import_file = auth_event_handler
class_name = AuthEventHandler
; path must be a file or a folder with / terminator
log_path = /var/log/auth.log
type = fs

[MYSQL]
import_file = mysql_log_handler
class_name = MysqlEventHandler
log_path = 
type = fs

[NGINX]
import_file = nginx_event_handler
class_name = nginxEventHandler
log_path = 
api_key = xxx
type = fs


[FAIL2BAN]
import_file = fail2ban_handler
class_name = Fail2BanEventHandler
log_path = /var/log/fail2ban.log
type = fs

[PORT_ALIVE_ALARM]
import_file = port_alive_alarm
class_name = PortAliveAlarm
hosts = 127.0.0.1:22
rtime = 5
type = time
```
