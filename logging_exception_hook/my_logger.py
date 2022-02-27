import logging

from utility.libnames import LOG_FILE

def getlogger1():
    # logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    #ch = logging_exception_hook.StreamHandler()
    ch = logging.FileHandler(LOG_FILE)
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(ch)
    # logger.propagate=True
    return logger

def clearlogger():
    logger = logging.getLogger(__name__)
    ch = logging.FileHandler(LOG_FILE,"w")
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(ch)

def setup_log():
    logger = logging.getLogger('MyStocks')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    # ch = logging_exception_hook.StreamHandler()
    # ch.setLevel(logging_exception_hook.WARNING)

    # create formatter and add it to the handlers
    # fhFormatter = logging_exception_hook.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fhFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - Line: %(lineno)d - %(message)s')
    chFormatter = logging.Formatter('%(levelname)s - %(filename)s - Line: %(lineno)d - %(message)s')
    fh.setFormatter(fhFormatter)
    # ch.setFormatter(chFormatter)
    if logger.hasHandlers():
        logger.handlers.clear()
    # add the handlers to logger
    # logger.addHandler(ch)
    logger.addHandler(fh)

    logger.info("-----------------------------------")
    logger.info("Log system successfully initialised")
    logger.info("-----------------------------------")

    return logger