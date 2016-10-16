"""This module is used to parse messages received through Telegram API.
"""
import re

import constants
import exceptions

def parseCommand(msg):
    """Parses a normal message.

    Args:
        msg (str): The message to parse.

    Returns:
        tuple: A tuple containing the command (or None) as first element
        and the rest of the message as second.

    :todo: throw exception if message is malformed.
    """
    msg = msg.strip()
    match = constants.QUERY_REGEXP.match(msg)
    if match:
        return (match.group(1), match.group(2))
    match = constants.QUERY_LIST_REGEXP.match(msg)
    if match:
        return ("L", match.group(1))
    else:
        return (None, msg)

def parseCallbackGameData(data):
    """Parses callback data associated to a game.

    Args:
        data (str): The data to parse.

    Returns:
        tuple: A tuple containing the type of action required (show more or show less)
        and the ID of the game.

    Raises:
        .exceptions.BadCallbackData: If data does not match the correct regexp.
    """
    match = constants.CALLBACK_GAME_DATA.match(data)
    if match:
        return match.group(1), match.group(2)
    else:
        raise exceptions.BadCallbackData()

def parseCallbackListData(data):
    """Parses callback data associated to a list of games.

    Args:
        data (str): The data to parse.

    Returns:
        tuple: A tuple containing the type of action required (show next page or show
        previous page), the original search string and the current offset.

    Raises:
        .exceptions.BadCallbackData: If data does not match the correct regexp.
    """
    match = constants.CALLBACK_LIST_DATA.match(data)
    if match:
        return match.group(1), match.group(2), match.group(3)
    else:
        raise exceptions.BadCallbackData()

def parseInlineCommand(msg):
    """Parses an inline message.

    Args:
        msg (str): The message to parse.

    Returns:
        tuple: A tuple containing the command (or None) as first element
        and the rest of the message as second.

    :todo: throw exception if message is malformed.
    """
    msg = msg.strip()
    match = constants.INLINE_QUERY_REGEXP.match(msg)
    if match:
        return (match.group(1), match.group(2))
    else:
        return (None, msg)
