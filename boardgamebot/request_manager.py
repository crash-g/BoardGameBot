"""This module is the core of the bot. It communicates with all the other parts of the application.
"""

import sys
import logging

import exceptions
import constants
from tools import input_parser
from tools import history_manager
from tools import http
from tools import output_formatter
from objects import chat_history
from objects import answer

logger = logging.getLogger("request_manager")

# reraises BggUnreachable, NoResultFound and InvalidXmlStructure
def _searchByName(name, chatId):
    """Searches for a boardgame using part of the name.

    Args:
        name (str): Part of the name of the game.
        chatId (int): The ID of the chat where the request came from.

    Returns:
        .answer.TelegramAnswer: An object containing all the information to be sent.
    """
    return _searchList(name, http.searchByName, chatId)

# reraises BggUnreachable, NoResultFound and InvalidXmlStructure
def _searchByNameExact(name, chatId):
    """Searches for a boardgame by name,  trying to match the name exactly.

    Args:
        name (str): The name of the game.
        chatId (int): The ID of the chat where the request came from.

    Returns:
        .answer.TelegramAnswer: An object containing all the information to be sent.
    """
    return _searchList(name, http.searchByNameExact, chatId)

# reraises BggUnreachable, NoResultFound and InvalidXmlStructure all 
def _searchList(searchString, httpSearch, chatId):
    """Called by all functions that expect a list of games as result. If the match
    is unique, the result of :func:`_searchById` is returned instead.

    Args:
        searchString (str): The string to pass to the search function.
        httpSearch (Callable[[str],game.gameList]): The function to use to search.
        chatId (int): The ID of the chat where the request came from.

    Returns:
        .answer.TelegramAnswer: An object containing all the information to be sent.
    """
    gameList = httpSearch(searchString)
    gameList.setOriginalSearch(searchString)
    if (1 == gameList.length()):
        id_ = gameList.get(0).id_
        return _searchById(id_, chatId)
    history_manager.updateLastGameList(gameList, chatId)
    return output_formatter.formatGameList(gameList)

# reraises BggUnreachable, NoResultFound and InvalidXmlStructure
def _searchById(id_, chatId, more=False):
    """Searches for a boardgame by ID.
    
    Args:
        id_ (int): The ID of the game to search.
        chatId (int): The ID of the chat where the request came from.
        more (bool): True if the answer should show additional info.

    Returns:
        .answer.TelegramAnswer: An object containing all the information to be sent.

    Raises:
        .exceptions.NoResultFound: If no game corresponds to the ID.
    """
    game = http.searchById(id_)
    formattedGame = output_formatter.formatGame(game, more)
    history_manager.updateLastGame(game, formattedGame.formattedAnswer, chatId)
    return formattedGame

# reraises BggUnreachable, NoResultFound and InvalidXmlStructure
# It cannot be private because it is called from init_inline_default.py
def searchByIdInline(id_, cacheTime, isPersonal):
    """Searches for a game by ID and returns an inline answer.

    Args:
        id_ (int): The ID of the game to search.
        cacheTime (int): The time the result should be cached on Telegram server.
        isPersonal (bool): Whether the result should be cached only for the user that made
            the request.

    Returns:
        answer.TelegramInlineAnswerList: An object containing all the information
            to be sent to answer the inline query.
    """
    game = http.searchById(id_)
    formattedInlineGame = output_formatter.formatInlineGame(game)
    inlineList = answer.TelegramInlineAnswerList(cacheTime, isPersonal)
    inlineList.addInlineAnswer(formattedInlineGame)
    return inlineList

def _gameFromList(pos, chatId):
    """Returns a game from the most recent search list of the chat.

    Args:
        pos (int): The position of the game in the list.
        chatId (int): The ID of the chat where the request came from.

    Returns:
        .game.Game: The game at the given position in the list.
    """
    id_ = history_manager.getGameIdFromRecentList(pos, chatId)
    return _searchById(id_, chatId)

# CALLBACK METHODS

def _processGameCallback(data, chatId, msgId):
    """Processes the press of a callback button associated to a game.

    Args:
        data (str): The callback data associated to the button.
        chatId (int): The ID of the chat that originated the query.
        msgId (int): The ID of the message associated to the callback button.

    Returns:
        .answer.TelegramAnswer: An object containing all the information to be sent.
    """
    firstChar, id_ = input_parser.parseCallbackGameData(data)
    more = "m" == firstChar
    if msgId != history_manager.getLastGameMsgId(chatId):
        answer = _searchById(id_, chatId, more)
        history_manager.setMsgId(chatId, msgId)
    else:
        game = history_manager.getLastGame(chatId)
        answer = output_formatter.formatGame(game, more)
    answer.setType("e")
    return answer
    
def _processListCallback(data, chatId, msgId):
    """Processes the press of a callback button associated to a list of games.

    Args:
        data (str): The callback data associated to the button.
        chatId (int): The ID of the chat that originated the query.
        msgId (int): The ID of the message associated to the callback button.

    Returns:
        .answer.TelegramAnswer: An object containing all the information to be sent.
    """
    firstChar, searchString, offset = input_parser.parseCallbackListData(data)
    if msgId != history_manager.getLastGameListMsgId(chatId):
        gameList = http.searchByName(searchString)
        gameList.setOriginalSearch(searchString)
        gameList.setOffset(int(offset))
        history_manager.updateLastGameList(gameList, chatId)
        history_manager.setMsgId(chatId, msgId)
    else:
        gameList = history_manager.getLastGameList(chatId)        
    if "n" == firstChar:
        newOffset = gameList.offset + constants.LIST_PAGE_SIZE
    else:
        newOffset = gameList.offset - constants.LIST_PAGE_SIZE
    return _changePage(gameList, newOffset)

def _changePage(gameList, offset):
    """Change the page in a list of results.

    Args:
        gameList (.game.GameList): the list of games to display.
        offset (int): The new offset of the list.

    Returns:
        .answer.TelegramAnswer: an object containing all the information to be sent.

    Raises:
        .exceptions.ListNavigationOutOfBound: If for some reason the position is out of bound.
    """
    if offset < 0 or offset >= gameList.length():
        logger.error("New offset is out of bound, this should not happen.")
        raise exceptions.ListNavigationOutOfBound()
    gameList.setOffset(offset)
    answer = output_formatter.formatGameList(gameList)
    answer.setType("e")
    return answer    

# PUBLIC

def processCommand(command, msg, chatId=None):
    """Entry point of this module for normal queries.
    This is used to process user input in the form of a command string
    and a message body.

    Args:
        command (str): The command to process.
        msg (str): An optional argument to the command. May be None.
        chatId (int): The ID of the chat that sent the message.
            It is used to update the chat history.

    Returns:
        .answer.TelegramAnswer: An answer to the message, containing the required
        info or an error message.
    """
    try:
        # start and help are default telegram commands
        if "start" == command:
            logger.info("start")
            return output_formatter.formatHelp()
        elif "help" == command:
            logger.info("help")
            return output_formatter.formatHelp()
        elif "i" == command or "id" == command:
            logger.info("id")
            return _searchById(msg, chatId)
        elif "b" == command or "boardgame" == command:
            logger.info("boardgame")
            return _searchByName(msg, chatId)
        elif "e" == command or "exact" == command:
            logger.info("exact")
            return _searchByNameExact(msg, chatId)
        elif "L" == command:
            logger.info("gameFromList")
            return _gameFromList(msg, chatId)
        else:
            return output_formatter.formatCommandNotSupported(command)
    except exceptions.NoResultFound:
        return output_formatter.formatNoResultFound()
    except (exceptions.BggUnreachable, exceptions.InvalidXmlStructure): # TODO differentiate?
        return output_formatter.formatBggUnreachable()
    except (exceptions.ChatHistoryNotFound, exceptions.MissingFromChatHistory):
        return output_formatter.formatHistoryNotFound()
    except exceptions.GameListIndexOutOfBound as err:
        return output_formatter.formatGameListIndexNotValid(err.index)

def processCallback(data, chatId, msgId):
    """Entry point of this module for callback queries.
    This is used to process user input in the form of a data string associated to the
    callback button.

    Args:
        data (str): The data associated to the callback button.
        chatId (int): The ID of the chat where the query originated.
            It is used to update the chat history.
        msgId (int): The ID of the message associated to the callback buttons.

    Returns:
        .answer.TelegramAnswer: An answer to the message, containing the required
        info or an error message.
    """
    try:
        firstChar = data[:1]
        if 'g' ==  firstChar:
            return _processGameCallback(data[1:], chatId, msgId)
        elif 'l' == firstChar:
            return _processListCallback(data[1:], chatId, msgId)
        else:
            return output_formatter.formatBadCallbackData()
    except (exceptions.ChatHistoryNotFound, exceptions.MissingFromChatHistory):
        return output_formatter.formatHistoryNotFoundCallback()
    except exceptions.StaleListCallback:
        return output_formatter.formatStaleList()
    except (exceptions.ListNavigationOutOfBound, exceptions.BadCallbackData):
        return output_formatter.formatBadCallbackData()

def processInline(command, msg, userId):
    """Entry point of this module for inline queries.
    This is used to process user input in the form of a command string
    and a message body.

    Args:
        command (str): The command to process.
        msg (str): An optional argument to the command. May be None.
        userId (int): The ID of the user that sent the message.
            It is used to retrieve the user history.

    Returns:
        .answer.TelegramAnswer: An answer to the message, containing the required
        info or an error message.
    """
    try:
        if "i" == command:
            if msg is not None:
                logger.info("ByIdInline")
                return searchByIdInline(msg, 3600, False)
            else:
                logger.error("ID is required in inline 'i' queries")
        elif "r" == command:
            logger.info("Inline recent games")
            return history_manager.getRecentGames(userId)
        else: # default result
            logger.info("Inline default")
            return constants.INLINE_DEFAULT
    except: # in case of any problem, send default result
        logger.exception("Error in inline query.")
        return processInline("default", None, None)
