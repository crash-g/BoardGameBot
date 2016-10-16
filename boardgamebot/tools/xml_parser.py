"""This module parses XML strings received from BGG.
"""
import defusedxml.ElementTree as ET
import logging

import exceptions
import constants
from objects.game import Game, GameList

logger = logging.getLogger("xml_parser")

def _getRoot(xmlString):
    """Gets the root of the XML document.

    Args:
        xmlString (str): The string to parse.

    Returns:
        defusedxml.ElementTree.Element: The root of the document.

    Raises:
        .exceptions.NoResultFound: If xmlString is None.
    """
    if xmlString is None:
        raise exceptions.NoResultFound()
    return ET.fromstring(xmlString)

def _parseThumbnail(thumb):
    """Parses the thumbnail string.

    Args:
        thumb: The string to parse.

    :todo: use regexp to parse.
    """
    return thumb[2:]

# PUBLIC

def parseGameList(xmlString):
    """Parses a string representing a list of games.

    Args:
        xmlString: The string to parse.

    Returns:
        .game.GameList: an object containing all the information on the list.

    Raises:
        .exceptions.InvalidXmlStructure: If there is an error while parsing.
        .exceptions.NoResultFound: If the list is empty.
    """
    root = _getRoot(xmlString)
    gameList = GameList()
    for elem in root.iter("item"):
        if "boardgame" == elem.get("type"):
            try:
                game = Game(id_=elem.get("id"))
                nameElem = elem.find("name")
                if nameElem is None:
                    raise exceptions.InvalidXmlStructure()
                game.setName(nameElem.get("value"))
                yearElem = elem.find("yearpublished")
                if yearElem is not None:
                    game.setYear(yearElem.get("value"))
                game.setLink(constants.BOARDGAMEGEEK_BASE_ADDRESS + game.id_)
                gameList.addGame(game)
            except ET.ParseError as err:
                logger.exception("Parse exception")
                raise exceptions.InvalidXmlStructure()
    if gameList.isEmpty():
        raise exceptions.NoResultFound()
    return gameList

def parseGame(xmlString):
    """Parses a string representing a game.

    Args:
        xmlString: The string to parse.

    Returns:
        .game.Game: an object containing all the information on the game.

    Raises:
        .exceptions.InvalidXmlStructure: If there is an error while parsing.
        .exceptions.NoResultFound: If the result is not a board game or an expansion.
    """
    root = _getRoot(xmlString)
    item = root.find("item")
    if item is None:
        raise exceptions.NoResultFound()
    game = None
    type_ = item.get("type")
    if "boardgame" == type_ or "boardgameexpansion" == type_:
        try:
            game = Game(id_=item.get("id"))
            for nameElem in item.findall("name"):
                if "primary" == nameElem.get("type"):
                    game.setName(nameElem.get("value"))
                    break;
            yearElem = item.find("yearpublished")
            if yearElem is not None:
                game.setYear(yearElem.get("value"))
            playingTimeElem = item.find("playingtime")
            if playingTimeElem is not None:
                game.setPlayingTime(playingTimeElem.get("value"))
            minPlayersElem = item.find("minplayers")
            if minPlayersElem is not None:
                game.setMinPlayers(minPlayersElem.get("value"))
            maxPlayersElem = item.find("maxplayers")
            if maxPlayersElem is not None:
                game.setMaxPlayers(maxPlayersElem.get("value"))
            for elem in item.findall("link"):
                if "boardgamecategory" == elem.get("type"):
                    game.addCategory(elem.get("value"))
                elif "boardgamemechanic" == elem.get("type"):
                    game.addMechanic(elem.get("value"))
                elif "boardgamedesigner" == elem.get("type"):
                    game.addDesigner(elem.get("value"))
                elif "boardgameartist" == elem.get("type"):
                    game.addArtist(elem.get("value"))
            descrElem = item.find("description")
            if descrElem is None or not descrElem.text:
                descr = "No description available."
            else:
                descr = descrElem.text
            game.setDescription(descr)
            thumbElem = item.find("thumbnail")
            if thumbElem is not None:
                game.setThumbnail(_parseThumbnail(thumbElem.text))
            game.setLink(constants.BOARDGAMEGEEK_BASE_ADDRESS + game.id_)
            # STATS
            statistics = item.find("statistics")
            if statistics is not None:
                ratings = statistics.find("ratings")
                if ratings is not None:
                    avg = ratings.find("average")
                    if avg is not None:
                        game.setAverage(avg.get("value"))
                    ranks = ratings.find("ranks")
                    if ranks is not None:
                        for rank in ranks.findall("rank"):
                            if "1" == rank.get("id"):
                                game.setRank(rank.get("value"))
        except ET.ParseError as err:
            logger.exception("Parse exception")
            raise exceptions.InvalidXmlStructure()
    if game is None:
        raise exceptions.NoResultFound()
    return game
