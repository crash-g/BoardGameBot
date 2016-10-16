"""This module is used to start the bot. It expects the bot API key as command-line argument.
"""
import sys
import asyncio
import threading
import logging
import signal

import init_log
# the init_log must be the first import in order to initialize the log for all modules
import asyncbot
import constants
from tools import persistence_unit
from tools import history_manager
from objects import background_task

def cleanUp(loop, stopSavingTask, logger):
    loop.stop()
    stopSavingTask.set()
    logger.info("Saving history...")
    persistence_unit.saveHistory()
    logger.info("Bye!")

# This check is due to the fact that Sphinx autodoc needs to execute the module
# in order to generate the documentation.
if __name__ == "__main__":
    logger = logging.getLogger("run_bot")

    TOKEN = sys.argv[1]  # get token from command-line

    bot = asyncbot.BggBot(TOKEN)
    loop = asyncio.get_event_loop()

    # set bot name at startup
    loop.run_until_complete(bot.setBotName())

    loop.create_task(bot.message_loop())

    # retrieves history and inline default from disk
    persistence_unit.getHistory()
    persistence_unit.getInlineDefault()
    # start background thread to backup history
    stopSavingTask = threading.Event()
    savingTask = background_task.Historian(stopSavingTask)
    savingTask.start()

    # registers a listener for the TERM signal, in order to clean up before exiting
    def cleanUpTERM(signal, frame):
        cleanUp(loop, stopSavingTask, logger)
        sys.exit(0)
    signal.signal(signal.SIGTERM, cleanUpTERM)
    
    logger.warning("Listening...")

    try:
        loop.run_forever()
    except KeyboardInterrupt: 
        cleanUp(loop, stopSavingTask, logger)
