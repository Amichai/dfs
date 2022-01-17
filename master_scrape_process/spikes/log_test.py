
import logging


logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
logger = logging.getLogger("log test!")

logger.warning('Watch out!')  # will print a message to the console
logger.info('I told you so')  # will not print anything
