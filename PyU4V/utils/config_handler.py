try:
    import ConfigParser as Config
except ImportError:
    import configparser as Config

import logging.config


def set_logger_and_config(logger):
    CFG = None
    # register configuration file
    try:
        CONF_FILE = 'PyU4V.conf'
        logging.config.fileConfig(CONF_FILE)
        CFG = Config.ConfigParser()
        CFG.read(CONF_FILE)
        LOG = logging.getLogger(logger.__name__)
    except Exception:
        # Set logging handlers if there is no config file
        logger.setLevel(logging.INFO)
        # create console handler and set level to info
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # create file handler, set level to debug
        fh = logging.FileHandler('PyU4V.log')
        fh.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # add formatter to ch and fh
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        # add ch and fh to logger
        logger.addHandler(ch)
        logger.addHandler(fh)
        LOG = logger
    return LOG, CFG
