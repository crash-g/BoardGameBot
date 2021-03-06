"""This module contains methods to produce a formatted string to be sent through the Telegram API.
"""
import math
import html
import itertools
import logging

import exceptions
import constants
from objects.answer import TelegramAnswer
from objects.answer import TelegramCallbackAnswer
from objects.answer import TelegramInlineAnswer

logger = logging.getLogger("output_formatter")

def _escapeHtml(text):
    text = text.replace("&", "&amp;")
    text = text.replace("<","&lt;")
    text = text.replace(">", "&gt;")
    return text

def _bold(text):
    return "<b>" + text + "</b>"

def _italic(text):
    return "<i>" + text + "</i>"

def _link(link, label):
    return "<a href=\"" + link + "\">" + label + "</a>"

def _appendList(originalString, listToAppend, separator, ending):
    for elem in listToAppend:
        originalString += _escapeHtml(elem) + separator
    offset = len(separator)
    originalString = originalString[:-offset]
    originalString += ending
    return originalString

def _formatGameTitle(game):
    s = _bold(_escapeHtml(game.name.title()))
    if game.year is not None:
        s += " (" + game.year + ")"
    s += "\n"
    return s

def _formatGameInfo(game):
    s = ""
    if game.numDesigners() > 0:
        if 1 == game.numDesigners():
            s += _italic("Designer: ")
        else:
            s += _italic("Designers: ")
        s = _appendList(s, game.getDesigners(), ", ", ".\n")
    if game.numArtists() > 0:
        if 1 == game.numArtists():
            s += _italic("Artist: ")
        else:
            s += _italic("Artists: ")
        s = _appendList(s, game.getArtists(), ", ", ".\n")
    if game.average is not None:
        try:
            rating = str(round(float(game.average), 1))
            if "." in rating:
                rating = rating.rstrip("0").rstrip(".")
                # remove decimal part if zero
            s += _italic("Rating: ") + rating + "\n"
        except ValueError:
            # just skip the average, which is likely not available
            logger.info("Game average is not a number: " + game.average)
    if game.rank is not None:
        s += _italic("Rank: ") + game.rank + "\n"
    if game.playingTime is not None and "0" != game.playingTime:
        s += _italic("Playing time: ") + game.playingTime + " minutes.\n"
    if game.minPlayers is not None:
        s += _italic("Players: ") + game.minPlayers
    if game.maxPlayers is not None:
        if game.minPlayers is None:
            s += _italic("Players: ") + game.maxPlayers
        elif game.maxPlayers > game.minPlayers:
            s += " - " + game.maxPlayers
    return s + "\n"

def _formatGameDescription(game):
    if len(game.description) > 800:
        return _escapeHtml(html.unescape(game.description[:800])) + "...\n"
    else:
        return _escapeHtml(html.unescape(game.description)) + "\n"

def _formatGameThumbnail(game):
    if game.thumbnail is not None:
        return _link(game.thumbnail, "Cover") + "\n"
    return ""

def _formatGameLink(game):
    return _link(game.link, "Read on BoardGameGeek.") + "\n"

def _formatGameBodyLess(game):
    """Formats the body of an answer containing a game, inserting only basic info.

    Args:
        game (game.Game): an object containing all the information on the game.

    Returns:
        str: a formatted string with the information to be sent.
    """
    s = _formatGameTitle(game) + "\n"
    s += _formatGameInfo(game)
    s += _formatGameThumbnail(game)
    s += _formatGameLink(game)
    return s

def _formatGameBodyMore(game):
    """Formats the body of an answer containing a game, inserting additional info.

    Args:
        game (game.Game): an object containing all the information on the game.

    Returns:
        str: a formatted string with the information to be sent.
    """
    s = _formatGameTitle(game) + "\n"
    s += _formatGameDescription(game)
    s += _formatGameLink(game)
    return s

def _formatGameListBody(gameList):
    """Formats the body of an answer containing a game list.

    Args:
        gameList (game.GameList): an object containing all the information on the game list.

    Returns:
        str: a formatted string with the information to be sent.
    """    
    s = ""
    offset = gameList.offset
    limit = offset + constants.LIST_PAGE_SIZE
    count = offset + 1
    for game in itertools.islice(gameList.gameList, offset, limit):
        s += u"&#x25BA"  # Unicode symbol to indicate element in list
        s += " " + str(count) + "."  # element number
        s += " " + _bold(_escapeHtml(game.name.title()))
        if game.year is not None:
            s += " (" + game.year + ")"
        s += " - ID: /" + game.id_ + "\n"
        count += 1
    return s

def formatGame(game, more=False):
    """Formats an answer containing a game, creating the body and attaching the markup.

    Args:
        game (game.Game): an object containing all the information on the game.
        more (bool): True if the answer should show additional info.

    Returns:
        .answer.TelegramAnswer: an object containing all the information to be sent.
    """
    if(more):
        formattedGameBody = _formatGameBodyMore(game)
        disableWebPagePreview = True
        text = "Game Info"
        callback_data = "gl" + str(game.id_)
    else:
        formattedGameBody = _formatGameBodyLess(game)
        disableWebPagePreview = False
        text = "Description"
        callback_data = "gm" + str(game.id_)
    keyboard = [[dict(text=text, callback_data=callback_data), dict(text="Share", switch_inline_query="i " + game.id_)]]
    return TelegramAnswer(formattedGameBody, inlineKeyboardMarkup=keyboard, disableWebPagePreview=disableWebPagePreview)

def formatInlineGame(game):
    """Formats an answer containing a game to be sent inline.

    Args:
        game (game.Game): an object containing all the information on the game.

    Returns:
        .answer.TelegramInlineAnswer: an object containing all the information to be sent.
    """
    formattedGameBody = _formatGameBodyLess(game)
    return TelegramInlineAnswer(formattedGameBody, game.id_, game.name.title(), game.thumbnail)

def formatGameList(gameList):
    """Formats an answer containing a game list, creating the body and attaching the markup.

    Args:
        gameList (game.GameList): an object containing all the information on the game list.

    Returns:
        .answer.TelegramAnswer: an object containing all the information to be sent.
    """
    formattedGameListBody = _formatGameListBody(gameList)
    keyboard = []
    offset = gameList.offset
    totalSize = len(gameList.gameList)
    callback_data = gameList.originalSearch + constants.CALLBACK_DATA_SEPARATOR + str(offset)
    buttonList = []
    if offset > 0:
        entry = dict(text="Back", callback_data="lp" + callback_data)
        buttonList.append(entry)
    if offset + constants.LIST_PAGE_SIZE < totalSize:
        entry = dict(text="Next", callback_data="ln" + callback_data)
        buttonList.append(entry)
    if buttonList:
        keyboard.append(buttonList)
    return TelegramAnswer(formattedGameListBody, inlineKeyboardMarkup=keyboard if keyboard else None)

"""Following methods format various error messages."""
def formatNoResultFound():
    return TelegramAnswer("No result found!")

def formatBggUnreachable():
    return TelegramAnswer("Sorry, it was not possible to contact Boardgamegeek servers. Try again later!")

def formatCommandNotSupported(command):
    return TelegramAnswer("Sorry, " + _bold("/" + command) + " is not a valid command.")

def formatHistoryNotFound():
    return TelegramAnswer("Sorry, last search not found in the history. Try to start a new search.")

def formatHistoryNotFoundCallback():
    return TelegramCallbackAnswer("Sorry, last search not found in the history. Try to start a new search.")

def formatGameListIndexNotValid(index):
    return TelegramAnswer("Error, " + index + " is not a valid search index (out of bound).")

def formatStaleList():
    return TelegramCallbackAnswer("The inline keyboard only works with the most recent searches.")

def formatBadCallbackData():
    return TelegramCallbackAnswer("This callback action is not supported, please try to start a new search.")

def formatHelp():
    """Formats a description of this bot usage.

    Returns:
        .answer.TelegramAnswer: The description of how to use this bot.
    """
    s = "This bot brings the power of " + _link("https://boardgamegeek.com/", "BoardGameGeek") + " into Telegram. The sky's the limit now."
    s += "\n\n" + _bold("Commands:") + "\n"
    for c in constants.COMMAND_DESCRIPTIONS:
        s += c + " - " + constants.COMMAND_DESCRIPTIONS[c] + "\n"
    s += "\n" + _bold("Inline Commands:") + "\n"
    for c in constants.INLINE_COMMAND_DESCRIPTIONS:
        s += c + " - " + constants.INLINE_COMMAND_DESCRIPTIONS[c] + "\n"
    s += "\nFor info about how inline mode works, see" + _link("https://telegram.org/blog/inline-bots", " the official guide") + "."
    return TelegramAnswer(s)
