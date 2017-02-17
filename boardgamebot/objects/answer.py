"""This module contains the classes that are used to communicate
between the core layer and the Telegram API.
"""

import exceptions
import constants

class Answer():
    """Base class shared by all the others. It does nothing on its own.

    Args:
        type_ (str): The type of an answer, used to obtain a specific instance without
            'casting'. Available types are the ones in :data:`.constants.ANSWER_METHOD_TYPES`.

    Raises:
        .exceptions.AnswerTypeNotSupported: If the type is not supported.
    """
    def __init__(self, type_):
        if type_ in constants.ANSWER_METHOD_TYPES:
            self.type_ = type_
        else:
            raise exceptions.AnswerTypeNotSupported(type_)

    def setType(self, type_):
        if type_ in constants.ANSWER_METHOD_TYPES:
            self.type_ = type_
        else:
            raise exceptions.AnswerTypeNotSupported(type_)
        
class TelegramAnswer(Answer):
    """This class is used to answer normal messages.

    Args:
        formattedAnswer (str): A formatted string which constitutes the body of the answer.
        replyKeyboardMarkup (dict): An optional dictionary describing a keyboard markup.
        inlineKeyboardMarkup (dict): An optional dictionary describing an inline keyboard markup.
        disableWebPagePreview (bool): Whether link previews should be visible in the answer or not.
    """
    def __init__(self, formattedAnswer, replyKeyboardMarkup=None, inlineKeyboardMarkup=None, disableWebPagePreview=None):
        super().__init__("n")
        self.formattedAnswer = formattedAnswer
        self.replyKeyboardMarkup = replyKeyboardMarkup
        self.inlineKeyboardMarkup = inlineKeyboardMarkup
        self.disableWebPagePreview = disableWebPagePreview

    def setReplyKeyboardMarkup(self, replyKeyboardMarkup):
        self.replyKeyboardMarkup = replyKeyboardMarkup

    def setInlineKeyboardMarkup(self, inlineKeyboardMarkup):
        self.inlineKeyboardMarkup = inlineKeyboardMarkup

    def disableWebPagePreview(self):
        self.disableWebPagePreview = True

class TelegramCallbackAnswer(Answer):
    """This class is used to answer callback messages.

    Args:
        formattedAnswer (str): A formatted string which constitutes the body of the answer.
    """
    def __init__(self, formattedAnswer):
        super().__init__("c")
        self.formattedAnswer = formattedAnswer        

class TelegramInlineAnswer():
    """This class is used as part of an answer to inline messages. It contains information about a specific game.

    Args:
        formattedAnswer (str): A formatted string which constitutes the body of the answer.
        id_ (int): The ID of the game.
        title (str): The title of the game.
        thumbUrl (str): An optional string with the thumbnail of the game.
    """
    def __init__(self, formattedAnswer, id_, title, thumbUrl=None):
        self.formattedAnswer = formattedAnswer
        self.id_ = id_
        self.title = title
        self.thumbUrl = thumbUrl

class TelegramInlineAnswerList(Answer):
    """This class is used to answer inline messages.

    Args:
        cacheTime (int): The time the result should be cached on Telegram servers.
        isPersonal (bool): Whether the result should be cached only for the current user or for everyone.
        answerList (list): A list of :class:`~TelegramInlineAnswer`.
    """
    def __init__(self, cacheTime, isPersonal, answerList=None):
        super().__init__("i")
        self.cacheTime = cacheTime
        self.isPersonal = isPersonal
        if answerList is None:
            self.answerList = []
        else:
            self.answerList = answerList
        self.nextOffset = ""
        # the value of the next_offset parameter, used to support pagination

    def addInlineAnswer(self, answer):
        self.answerList.append(answer)

    def prependInlineAnswer(self, answer):
        self.answerList.insert(0, answer)

    def removeLast(self):
        del self.answerList[-1]

    def size(self):
        return len(self.answerList)

    def setNextOffset(self, offset):
        self.nextOffset = offset
