import logging


def printlog(message):
        logging.basicConfig(filename='pi_log.txt', level=logging.INFO)
        print(message)
        logging.info(message)