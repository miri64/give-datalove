import logging
import logging.handlers

LOG_FILENAME = 'give_datalove.log'
LOG_LEVEL = logging.DEBUG

## The log object
log = logging.getLogger('MainLog')
log.setLevel(LOG_LEVEL)
handler = logging.handlers.RotatingFileHandler(
        LOG_FILENAME, 
        maxBytes=20*1024, 
        backupCount=5
    )

log.addHandler(handler)
