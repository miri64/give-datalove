import logging
import logging.handlers
from web import ctx

LOG_FILENAME = 'give_datalove.log'
LOG_LEVEL = logging.DEBUG
FORMAT = "%(levelname)s (%(module)s.py) [%(asctime)s]: " + \
            "%(message)s"

## The log object
log = logging.getLogger('MainLog')
log.setLevel(LOG_LEVEL)

formatter = logging.Formatter(FORMAT)
handler = logging.handlers.RotatingFileHandler(
        LOG_FILENAME, 
        maxBytes=100*1024, 
        backupCount=5
    )
handler.setFormatter(formatter)
log.addHandler(handler)

def get_ctx():
    return "('%s' for %s)" % (str(ctx.get('path')),str(ctx.get('ip')))
