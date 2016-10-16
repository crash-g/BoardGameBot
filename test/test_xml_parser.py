import sys
sys.path.insert(0, "../boardgamebot")

from tools import xml_parser
from objects.game import Game

with open("game.xml", "r", encoding="utf-8") as myfile:
    data=myfile.read().replace("\n", "")
game = xml_parser.parseGame(data)
print(game.toString())
print(game.description)
print("\n")

with open("gameList.xml", "r", encoding="utf-8") as myfile:
    data = myfile.read().replace("\n", "")
gameList = xml_parser.parseGameList(data)
print(gameList.toString())

def parseGame():
    with open("game2.xml", "r", encoding="utf-8") as myfile:
        data=myfile.read().replace("\n", "")
        game = xml_parser.parseGame(data)
        return game

def parseGameList():
    with open("gameList.xml", "r", encoding="utf-8") as myfile:
        data = myfile.read().replace("\n", "")
        gameList = xml_parser.parseGameList(data)
        return gameList
