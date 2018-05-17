try:
    import ConfigParser as Config
except ImportError:
    import configparser as Config
import logging
import logging.config
import os


def set_logger_and_config(file_path=None):
    cfg, conf_file, set_null_logger = None, None, True
    # register configuration file
    conf_file_name = 'PyU4V.conf'
    if file_path is not None:
        if os.path.isfile(file_path):
            conf_file = file_path
    elif os.path.isfile(conf_file_name):
        conf_file = conf_file_name
    else:
        global_path = os.path.normpath('~/.PyU4V/PyU4V.conf')
        if os.path.isfile(global_path):
            conf_file = global_path
    if conf_file is not None:
        set_null_logger = False
        try:
            cfg = Config.ConfigParser()
            cfg.read(conf_file)
            logging.config.fileConfig(conf_file)
            logging.getLogger(__name__)
        except Exception:
            set_null_logger = True
    if set_null_logger is True:
        # Set default logging handler to avoid "No handler found" warnings.
        try:  # Python 2.7+
            from logging import NullHandler
        except ImportError:
            class NullHandler(logging.Handler):
                def emit(self, record):
                    pass

        logging.getLogger(__name__).addHandler(NullHandler())

    return cfg
