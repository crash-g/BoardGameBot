"""This module contains threads that run in background.
"""
import threading

import logging
import constants
from tools import persistence_unit

logger = logging.getLogger("background_task")

class Historian(threading.Thread):
    """This thread regularly saves the history on file.
    """
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(constants.HISTORY_SAVING_INTERVAL):
            logger.warn("Saving history...")
            persistence_unit.saveHistory()
            logger.warn("History saved.")

            
