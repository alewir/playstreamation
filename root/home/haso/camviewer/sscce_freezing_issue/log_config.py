import logging
from logging.handlers import RotatingFileHandler

# create & configure logger
log_level = logging.INFO

log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log_handler_file = RotatingFileHandler(filename='player4cams.log', mode='w', maxBytes=5000000, backupCount=3)
log_handler_console = logging.StreamHandler()
log_handler_console.setLevel(log_level)
log_handler_console.setFormatter(log_formatter)

log = logging.getLogger('player4cams')
log.setLevel(log_level)
log_handler_file.setLevel(log_level)
log_handler_file.setFormatter(log_formatter)
log.addHandler(log_handler_console)
log.addHandler(log_handler_file)
