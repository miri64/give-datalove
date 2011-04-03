import logging
import logging.handlers

LOG_FILENAME = 'give_datalove.log'
LOG_LEVEL = logging.DEBUG
FORMAT = "%(levelname)s (%(module)s.py#%(funcName)s) [%(asctime)s]: %(message)s"

## The log object
log = logging.getLogger('MainLog')
log.setLevel(LOG_LEVEL)

formatter = logging.Formatter(FORMAT)
handler = logging.handlers.RotatingFileHandler(
        LOG_FILENAME, 
        maxBytes=20*1024, 
        backupCount=5
    )
handler.setFormatter(formatter)
log.addHandler(handler)
