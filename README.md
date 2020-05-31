# Security Watchdog

Example config.ini attached

`chat_id` can also be added in the MAIN section to directly talk to someone

## Extending
Extending can be done by extending the a watchdog event handler

`__init__` function takes config and a notify function that is called to send the telegram message
Section config needs to contain at least the below entried to properly load. Others can be added and then later extracted from the config

## Config.ini

New section needs to be created for each extension
`import_file` is the file name, without `.py` ending
`class_name` is the class that extends the watchdog handler
`log_path` is the file or folder that is watched for changes
