"""This module is only used to initialize a default inline result for inline queries.
"""
import pickle

import constants

from tools import http
from tools import output_formatter
from objects import answer

def _searchByIdInline(id_, cacheTime, isPersonal):
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


if __name__ == "__main__":
    inlineList = _searchByIdInline("145654", 3600, True)
    with open(constants.INLINE_DEFAULT_PATH, "wb") as inlineDefault:
        pickle.dump(inlineList, inlineDefault, -1)
        print("Success!")

