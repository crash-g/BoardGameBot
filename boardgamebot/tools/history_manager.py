"""This module is used to manage chat and user history.
"""
import logging

import exceptions
import constants
from objects import chat_history

logger = logging.getLogger("history_manager")

CHAT_HISTORY = {}
"""A dictionary where keys are chat IDs and values are
:class:`~.chat_history.ChatHistory` objects.
"""
USER_PRIVATE_CHAT = {}
"""A dictionary where keys are user IDs and values are chat IDs
(the private chat corresponding to the user).
"""

def _getOrCreateChatHistory(chatId):
    """Gets a specific chat history or creates an entry if not found.

    Args:
        chatId (int): The ID of the chat.

    Returns:
        .chat_history.ChatHistory: the history associated to the chat, or an
        empty history if none was associated.
    """
    if chatId not in CHAT_HISTORY:
        CHAT_HISTORY[chatId] = chat_history.ChatHistory()
    return CHAT_HISTORY[chatId]

def _retrieveChatHistory(chatId):
    """Gets a specific chat history, throwing an error if it is not found.

    Args:
        chatId (int): The ID of the chat.

    Returns:
        .chat_history.ChatHistory: the history associated to the chat.

    Raises:
        .exceptions.ChatHistoryNotFound: If there is no history associated.
    """
    if chatId not in CHAT_HISTORY:
        raise exceptions.ChatHistoryNotFound()
    return CHAT_HISTORY[chatId]

# UPDATE METHODS

def updateLastGame(game, formattedAnswer, chatId):
    """Updates the last game searched in a chat.
    
    Args:
        game (.game.Game): The last game searched.
        chatId (int): The ID of the relative chat.
    """
    chatHistory = _getOrCreateChatHistory(chatId)
    chatHistory.setLastGame(game, formattedAnswer)

def updateLastGameList(gameList, chatId):
    """Updates the last game list searched in a chat.

    Args:
        gameList (.game.GameList): The last game list searched.
        chatId (int): The ID of the relative chat.
    """
    chatHistory = _getOrCreateChatHistory(chatId)
    chatHistory.setLastGameList(gameList)

def addRecentGame(game, formattedGame, chatId):
    """Adds a game to the list of recent games.
    
    Args:
        game (.game.Game): A game to add to the list of recent searches.
        formattedGame (str): The formatted description of the game.
        chatId (int): The ID of the relative chat.
    """
    chatHistory = _getOrCreateChatHistory(chatId)
    chatHistory.addRecentGame(game, formattedGame)

def setMsgId(chatId, msgId):
    """Sets the message ID associated to the  most recent object inserted in the chat history.
    This has to be done in this way because the ID is only available after sending
    the answer.

    Args:
        chatId (int): The ID of a chat.
        msgId (int): The ID of the last sent message in the chat.
    """
    chatHistory = _retrieveChatHistory(chatId)
    if chatHistory.setMsgId is not None:
        chatHistory.setMsgId(msgId)

def setUserPrivateChat(userId, chatId):
    """Sets the ID of the private chat associated to a user.

    Args:
        userId (int): The ID of the user.
        chatId (int): The ID of the relative private chat.
    """
    if userId not in USER_PRIVATE_CHAT:
        USER_PRIVATE_CHAT[userId] = chatId
        logger.info("user: " + str(userId) + " has private chat " + str(chatId))

# GETTERS

def getLastGame(chatId):
    chatHistory = _retrieveChatHistory(chatId)
    game = chatHistory.lastGame
    if game is None:
        raise exceptions.MissingFromChatHistory()
    return game

def getLastGameMsgId(chatId):
    chatHistory = _retrieveChatHistory(chatId)
    game = chatHistory.lastGame
    if game is None:
        return None
    return game.msgId

def getGameIdFromRecentList(pos, chatId):
    """Gets the ID of a specific game in the list of recent games.
    
    Args:
        pos (int): The position of the game in the list.
        chatId (int): The ID of the chat.

    Returns:
        int: The ID of the game at the specified position in the list.

    Raises:
        .exceptions.MissingFromChatHistory: If the list of recent games is empty.
        .exceptions.GameListIndexOutOfBound: If the given position is not valid.
    """
    chatHistory = _retrieveChatHistory(chatId)
    gameList = chatHistory.lastGameList
    if gameList is None:
        raise exceptions.MissingFromChatHistory()
    if int(pos) < 1 or int(pos) > gameList.length():
        raise exceptions.GameListIndexOutOfBound(pos)    
    return gameList.get(int(pos)-1).id_

def getLastGameList(chatId):
    """Gets the most recent list searched in the chat.

    Args:
        chatId (int): The ID of the chat.

    Returns:
        .game.GameList: An object with all the information on the list.

    Raises:
        .exceptions.MissingFromChatHistory: If there is no recent list in the history.
    """
    chatHistory = _retrieveChatHistory(chatId)
    gameList = chatHistory.lastGameList
    if gameList is None:
        raise exceptions.MissingFromChatHistory()
    return gameList

def getLastGameListMsgId(chatId):
    """Gets the ID of the most recent list searched in the chat.

    Args:
        chatId (int): The ID of the chat.

    Returns:
        int: The message ID of the list.

    Raises:
        .exceptions.MissingFromChatHistory: If there is no recent list in the history.
    """
    chatHistory = _retrieveChatHistory(chatId)
    gameList = chatHistory.lastGameList
    if gameList is None:
        raise exceptions.ChatHistoryNotFound()
    return gameList.msgId

def getRecentGames(userId):
    """Gets the list of recent games for a specific user.

    Args:
        userId (int): The ID of the user.

    Returns:
        .answer.TelegramInlineAnswerList: The list of recent games.

    Raises:
        .exceptions.ChatHistoryNotFound: If there is no entry for userId in :data:`~.USER_PRIVATE_CHAT`.
        .exceptions.MissingFromChatHistory: If the list of recent games is None.
    """
    chatId = USER_PRIVATE_CHAT[userId]
    if chatId is None:
        raise exceptions.ChatHistoryNotFound()
    chatHistory = _retrieveChatHistory(chatId)
    recentGames = chatHistory.recentGames
    if recentGames is None:
        raise exceptions. MissingFromChatHistory()
    return recentGames

