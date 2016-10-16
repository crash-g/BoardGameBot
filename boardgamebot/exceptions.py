class GenericError(Exception):
    pass

# CONNECTION
class BggUnreachable(GenericError):
    def __init__(self, fatal):
        # fatal is just a hint to decide whether to retry the connection or not
        self.fatal = fatal

# RESULT OF BGG QUERY
class NoResultFound(GenericError):
    pass

class InvalidXmlStructure(GenericError):
    pass

# HISTORY
class ChatHistoryNotFound(GenericError):
    pass

class MissingFromChatHistory(GenericError):
    pass

class ListNavigationOutOfBound(GenericError):
    pass

class GameListIndexOutOfBound(GenericError):
    def __init__(self, index):
        self.index = index

class StaleListCallback(GenericError):
    pass

# CALLBACK
class BadCallbackData(GenericError):
    pass

# INTERNAL EXCEPTIONS (do not catch)
class TypeNotSupported(GenericError):
    def __init__(self, type_):
        self.type_ = type_
    
class BggObjectNotSupported(TypeNotSupported):
    pass

class FormatTypeNotSupported(TypeNotSupported):
    pass

class AnswerTypeNotSupported(TypeNotSupported):
    pass

class AnswerMethodNotSupported(TypeNotSupported):
    pass
