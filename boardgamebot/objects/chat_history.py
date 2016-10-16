"""This module contains the class that models an entry in the history.
"""

import constants
from objects import answer

class ChatHistory():
    """This class contains all the information about the history in a single chat.
    """
    def __init__(self):
        self.lastGame = None
        """The most recent game searched in a chat.
        """
        self.lastGameList = None
        """The most recent game list searched in a chat.
        """
        self.recentGames = answer.TelegramInlineAnswerList(5, True)
        """The list of most recent games searched in a chat.
        """
        self.setMsgId = None  # function to use when setting msgId
        """This contains the function to call to set the message ID.
        The function should correspond to the most recent variable set
        (:attr:`~.lastGame` or :attr:`~.lastGameList`).
        """
    def setLastGame(self, game, formattedAnswer):
        self.lastGame = game
        self.setMsgId = self.setLastGameMsgId
        self.addRecentGame(game, formattedAnswer)

    def setLastGameMsgId(self, msgId):
        self.lastGame.setMsgId(msgId)
        
    def setLastGameList(self, gameList):
        self.lastGameList = gameList
        self.setMsgId = self.setLastGameListMsgId

    def setLastGameListMsgId(self, msgId):
        self.lastGameList.setMsgId(msgId)

    def addRecentGame(self, game, formattedAnswer):
        for g in self.recentGames.answerList:
            if g.id_ == game.id_:
                return
        inlineAnswer = answer.TelegramInlineAnswer(formattedAnswer, game.id_, game.name.title(), game.thumbnail)
        self.recentGames.prependInlineAnswer(inlineAnswer)
        if self.recentGames.size() > constants.RECENT_GAMES_LIMIT:
            self.recentGames.removeLast()
