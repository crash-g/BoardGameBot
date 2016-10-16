"""This module is only used to initialize a default inline result for inline queries.
"""
import pickle

import request_manager
import constants

if __name__ == "__main__":
    inlineList = request_manager.searchByIdInline("145654", 10, True)
    with open(constants.INLINE_DEFAULT_PATH, "wb") as inlineDefault:
        pickle.dump(inlineList, inlineDefault, -1)
        print("Success!")
