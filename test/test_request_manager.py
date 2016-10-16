import pickle
import sys
sys.path.insert(0, "../boardgamebot")

import request_manager
from tools import history_manager
from tools import persistence_unit

history_manager.setUserPrivateChat(4, 12)
print(request_manager.processCommand("help", None, 12))

print(request_manager.processCommand("i", 1456542332, 12))
print(request_manager.processCommand("i", 145654, 12))

print(request_manager.processCommand("b", "Pandemic yoh yoh yoh", 12))

print(request_manager.processCommand("e", "invaders armageddon", 12))

print(request_manager.processCommand("b", "/bniopgvpo", 12))

print(request_manager.processCommand("L", "2", 12))

history_manager.setMsgId(12, 1)
request_manager.processCallback("next", 12, 1)

print(request_manager.processCallback("next", 12, 2))
print(request_manager.processCallback("nextr", 12, 2))

print(request_manager.processInline("i", "145654", 4))
print(request_manager.processInline("r", "145654", 4))

try:
    with open('../boardgamebot/resources/inline_default.dat', 'rb') as inlineDefault:
        inlineDefault = pickle.load(inlineDefault)
except:
    print("Cannot read inline default")
print(inlineDefault.answerList[0].formattedAnswer)
