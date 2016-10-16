"""This module saves and retrieves user and chat history.
"""
import os
import pickle
import logging

import constants
from tools import history_manager

logger = logging.getLogger("persistence_unit")

def saveHistory():
    """Saves the history on file.
    """
    try:
        with open(constants.CHAT_HISTORY_PATH, "wb") as chatHistory:
            pickle.dump(history_manager.CHAT_HISTORY, chatHistory, -1)
    except:
        logger.error("Cannot save chat history!")
    try:
        with open(constants.USER_HISTORY_PATH, "wb") as userHistory:
            pickle.dump(history_manager.USER_PRIVATE_CHAT, userHistory, -1)
    except:
        logger.error("Cannot save user history!")
    statinfo = os.stat(constants.CHAT_HISTORY_PATH)
    if(statinfo.st_size > constants.HISTORY_WARNING_SIZE):
        logger.error("Very large chat history size!")
    statinfo = os.stat(constants.USER_HISTORY_PATH)
    if(statinfo.st_size > constants.HISTORY_WARNING_SIZE):
        logger.error("Very large user history size!")

def getHistory():
    """Retrieves the history from file.
    """
    try:
        with open(constants.CHAT_HISTORY_PATH, 'rb') as chatHistory:
            history_manager.CHAT_HISTORY = pickle.load(chatHistory)
    except:
        logger.warning("Cannot read chat history")
    try:
        with open(constants.USER_HISTORY_PATH, 'rb') as userHistory:
            history_manager.USER_PRIVATE_CHAT = pickle.load(userHistory)
    except:
        logger.warning("Cannot read user history")

def getInlineDefault():
    """Loads the default inline result from file.
    """
    try:
        with open(constants.INLINE_DEFAULT_PATH, 'rb') as inlineDefault:
           constants.INLINE_DEFAULT = pickle.load(inlineDefault)
    except:
        logger.error("Cannot read inline default")
