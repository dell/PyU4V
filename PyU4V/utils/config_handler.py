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
        LOG = logger
    return LOG, CFG
