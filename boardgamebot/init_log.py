import logging
import logging.config

import constants

logging.config.fileConfig("logging.conf", defaults={"logfilename": constants.logfileName})
