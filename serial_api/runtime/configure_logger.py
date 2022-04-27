import sys
import logging
import DateTime
import os
import colorama

LOG_DIR = os.path.join(os.path.dirname(sys.argv[0]), "log")

FILE_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s: %(message)s"
STREAM_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s: %(message)s"
COLOR_LIST = [colorama.Fore.MAGENTA, colorama.Fore.CYAN,
              colorama.Fore.GREEN, colorama.Fore.YELLOW,
              colorama.Fore.BLUE, colorama.Fore.RED]
COLOR_INDEX = 0

def configure_logger(log_level, device_name):
    global COLOR_INDEX

    if log_level >= 0 and not os.path.exists(LOG_DIR):
        print("Creating log directory: {}".format(os.path.abspath(LOG_DIR)))
        os.mkdir(LOG_DIR)

    logger = logging.getLogger(device_name)
    logger.setLevel(logging.DEBUG)

    stream_formatter = logging.Formatter(
        COLOR_LIST[COLOR_INDEX % len(COLOR_LIST)] + colorama.Style.BRIGHT
        + STREAM_LOG_FORMAT
        + colorama.Style.RESET_ALL)
    COLOR_INDEX = (COLOR_INDEX + 1) % len(COLOR_LIST)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(stream_formatter)
    stream_handler.setLevel(log_level)
    logger.addHandler(stream_handler)

    if log_level >= 0:
        dt = DateTime.DateTime()
        logfile = "{}_{}-{}-{}_{}-{}_output.log".format(
            device_name, dt.yy(), dt.mm(), dt.dd(), dt.hour(), dt.minute())
        logfile = os.path.join(LOG_DIR, logfile)
        fh = logging.FileHandler(logfile)
        fh.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(FILE_LOG_FORMAT)
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)

    return logger
