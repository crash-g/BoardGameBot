import sys
sys.path.insert(0, "../boardgamebot")
import pickle

import init_inline_default

with open('../boardgamebot/resources/inline_default.dat', 'rb') as inlineDefault:
    print(pickle.load(inlineDefault))

