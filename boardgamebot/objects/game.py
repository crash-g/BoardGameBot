"""This module contains DTOs used to wrap the result of a query to BGG.
"""

import constants
import exceptions

class BggObject():
    """The base type shared by all the other objects in this module.

    Args:
        type_ (str): The type of a game, used to obtain a specific instance without
            'casting'. Available types are the ones in :data:`.constants.BGG_TYPES`.

    Raises:
        .exceptions.BggObjectNotSupported: If the type is not supported.
    """
    def __init__(self, type_):
        if type_ in constants.BGG_TYPES:
            self.type_ = type_
        else:
            raise exceptions.BggObjectNotSupported(type_)

class Game(BggObject):
    """This class models a game.
    """
    def __init__(self, id_, name=None, year=None):
        super().__init__("g")
        self.id_ = id_
        self.name = name
        self.year = year

        self.average = None
        self.rank = None
        self.playingTime = None
        self.minPlayers = None
        self.maxPlayers = None
        self.categories = []
        self.mechanics = []
        self.designers = []
        self.artists = []
        self.description = None
        self.thumbnail = None
        self.link = None

        self.msgId = None

    def setId(self, id_):
        self.id_ = id_
    def setName(self, name):
        self.name = name
    def setYear(self, year):
        self.year = year

    def setAverage(self, avg):
        self.average = avg
    def setRank(self, rank):
        self.rank = rank
    def setPlayingTime(self, time):
        self.playingTime = time
    def setMinPlayers(self, minP):
        self.minPlayers = minP
    def setMaxPlayers(self, maxP):
        self.maxPlayers = maxP
    def addCategory(self, category):
        self.categories.append(category)
    def numCategories(self):
        return len(self.categories)
    def getCategories(self):
        return self.categories
    def addMechanic(self, mechanic):
        self.mechanics.append(mechanic)
    def numMechanics(self):
        return len(self.mechanics)
    def getMechanics(self):
        return self.mechanics
    def addDesigner(self, designer):
        self.designers.append(designer)
    def numDesigners(self):
        return len(self.designers)
    def getDesigners(self):
        return self.designers
    def addArtist(self, artist):
        self.artists.append(artist)
    def numArtists(self):
        return len(self.artists)
    def getArtists(self):
        return self.artists
    def setThumbnail(self, thumb):
        self.thumbnail = thumb
    def setDescription(self, descr):
        self.description = descr
    def setLink(self, link):
        self.link = link
    def setMsgId(self, msgId):
        self.msgId = msgId

    # DEBUG
    def toString(self):
        s = self.name + " (" + self.id_ + ")"
        if self.year is not None:
            s += " - " + self.year
        return s

class GameList(BggObject):
    """This class models a game list.
    """
    def __init__(self, gameList=None, offset=0, originalSearch=None):
        super().__init__("l")
        if gameList is None:
            self.gameList = []
        else:
            self.gameList = gameList
        self.offset = offset
        self.originalSearch = originalSearch
        self.msgId = None

    def addGame(self, game):
        self.gameList.append(game)

    def setOffset(self, offset):
        self.offset = offset

    def setOriginalSearch(self, originalSearch):
        self.originalSearch = originalSearch

    def setMsgId(self, msgId):
        self.msgId = msgId

    def isEmpty(self):
        return 0 == len(self.gameList)

    def length(self):
        return len(self.gameList)

    def get(self, index):
        return self.gameList[index]

    # DEBUG
    def toString(self):
        s = ""
        for game in self.gameList:
            s += game.toString() + "\n"
        return s
