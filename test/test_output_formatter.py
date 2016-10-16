import os
import sys
sys.path.insert(0, os.path.abspath("../boardgamebot"))
import html

from tools import output_formatter
import test_xml_parser

game = test_xml_parser.parseGame()
print(output_formatter.formatGame(game).formattedAnswer)

gameList = test_xml_parser.parseGameList()
print(output_formatter.formatGameList(gameList).formattedAnswer)
