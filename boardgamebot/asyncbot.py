"""This module is the front-end of the bot and serves as a gateway between Telegram API
and the rest of the application.

:todo:
    1. Timestamp su history e clean old entries
    2. Use coroutines in request_manager in order to communicate with asyncbot
"""
import sys
import random
import logging
import telepot
import telepot.aio
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent

import request_manager
import constants
from objects import answer as ans
from tools import history_manager
from tools import input_parser

logger = logging.getLogger("async")

class BggBot(telepot.aio.Bot):
    """This class implements the mehods that are called by telepot upon retrieving a
    message. The mapping of the methods is the default one.

    Args:
        ANSWER_METHODS (dict): Dictionary with appropriate methods to send a particular
            type of answer.
            The keys must correspond to :data:`.constants.ANSWER_METHOD_TYPES`.
    """
    def __init__(self, *args, **kwargs):
        super(BggBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.aio.helper.Answerer(self)
        self._message_with_inline_keyboard = None
        self.ANSWER_METHODS = {"n": self.sendNormalMessage, "c": self.sendCallbackAnswer, "i": self.sendInlineAnswer, "e": self.editMessage}

    async def setBotName(self):
        """Used to set bot name at startup. It is necessary because the bot must be able to
        parse user messages containing its name.
        """
        botDetails = await self.getMe()
        constants.botUsername = botDetails["username"]
        constants.botName = botDetails["first_name"]
        constants.defineREGEXPs()
        logger.info("QUERY_REGEXP: " + constants.COMMAND_REGEXP + constants.ARGUMENT_REGEXP)

    async def on_chat_message(self, msg):
        """Processes a normal chat message.

        Args:
            msg (str): The message to process.
        """
        contentType, chatType, chatId = telepot.glance(msg)

        if "private" == chatType:
            userId = msg["from"]["id"]
            history_manager.setUserPrivateChat(userId, chatId)

        if contentType != 'text':
            # we only accept text, so print help
            answer = request_manager.processCommand("help", None)
        else:
            msgText = msg["text"]
            command, msgText = input_parser.parseCommand(msgText)

        if command:
            if msgText is not None:
                logger.debug("Processing command " + command + " and message: " + msgText)
            else:
                logger.debug("Processing command " + command)
            answer = request_manager.processCommand(command, msgText, chatId)            
        else:
            return

        id_ = {"chat_id": chatId}
        await self.sendAnswer(id_, answer)

    async def on_callback_query(self, msg):
        """Processes a callback query.

        Args:
           msg (str): The message to process.
        """
        queryId, fromId, data = telepot.glance(msg, flavor='callback_query')
        
        if "message" in msg:
            msgId = {
                "chat_id": msg["message"]["chat"]["id"],
                "message_id": msg["message"]["message_id"],
                "query_id": queryId
            }
            answer = request_manager.processCallback(data, msgId["chat_id"], msgId["message_id"])
            if answer is not None: # may be None if multiple people are pressing buttons at the same time
                await self.sendAnswer(msgId, answer)
        else:
            logger.error("Message field not found in query")

    def on_inline_query(self, msg):
        """Processes an inline query.

        Args:
            msg (str): The message to process.
        """
        def compute():
            logger.debug("Computing inline")
            queryId, fromId, queryString, offset = telepot.glance(msg, 'inline_query', True)
            offset = int(offset) if offset else 0
            command, msgText = input_parser.parseInlineCommand(queryString.lower())

            answer = request_manager.processInline(command, msgText, fromId, offset)
            resultList = []
            for inlineAnswer in answer.answerList:
                resultList.append(dict(type="article", title=inlineAnswer.title, id=inlineAnswer.id_, input_message_content=dict(message_text=inlineAnswer.formattedAnswer, parse_mode="HTML"), thumb_url=inlineAnswer.thumbUrl))
            return {"results": resultList, "cache_time": answer.cacheTime, "is_personal": answer.isPersonal, "next_offset": answer.nextOffset}
 
        self._answerer.answer(msg, compute)

    def on_chosen_inline_result(self, msg):
        resultId, fromId, queryString = telepot.glance(msg, flavor='chosen_inline_result')
        logger.info('Chosen Inline Result:', resultId, fromId, queryString)

    def on_edited_chat_message(self, msg):
        logger.info("Message edited")

    async def sendAnswer(self, id_, answer):
        """This method selects the appropriate method to send an answer by examining its type.
    
        Args:
            id_ (dict): A dictionary containing various IDs, as needed.
            answer (.answer.Answer): The answer to send.
        """
        answerType = answer.type_
        if answerType in self.ANSWER_METHODS:
            await self.ANSWER_METHODS[answerType](id_, answer)
        else:
            raise exceptions.AnswerMethodNotSupported()
            
    async def sendNormalMessage(self, id_, answer):
        """Formats and sends a chat message.

        Args:
            id_ (dict): A dictionary containing the ID of the chat where the message
                should be sent.
            answer (.answer.Answer): The answer to send.
        """
        chatId = id_["chat_id"]
        if answer.replyKeyboardMarkup is not None:
            markup = ReplyKeyboardMarkup(keyboard = answer.replyKeyboardMarkup)
        elif answer.inlineKeyboardMarkup is not None:
            markup = InlineKeyboardMarkup(inline_keyboard = answer.inlineKeyboardMarkup)
        else:
            markup = None
        sentMessage = await self.sendMessage(chatId, answer.formattedAnswer, parse_mode="HTML", reply_markup=markup, disable_web_page_preview=answer.disableWebPagePreview)
        history_manager.setMsgId(chatId, sentMessage["message_id"])

    async def sendCallbackAnswer(self, id_, answer):
        """Sends a callback message.

        Args:
            id_ (dict): A dictionary containing the ID of the callback query.
            answer (.answer.Answer): The answer to send.
        """
        queryId = id_["query_id"]
        await self.answerCallbackQuery(queryId, text=answer.formattedAnswer)

    async def editMessage(self, id_, answer):
        """Formats and edits a chat message.

        Args:
            id_ (dict): A dictionary containing the ID of the chat where the message
                should be sent and the ID of the message to edit.
            answer (.answer.Answer): The answer to send.
        """
        msgId = (id_["chat_id"], id_["message_id"])
        markup = InlineKeyboardMarkup(inline_keyboard = answer.inlineKeyboardMarkup)
        await self.editMessageText(msgId, answer.formattedAnswer, parse_mode="HTML", reply_markup=markup, disable_web_page_preview=answer.disableWebPagePreview)

    def sendInlineAnswer(self, id_, answer):
        pass # TODO implement or remove?
