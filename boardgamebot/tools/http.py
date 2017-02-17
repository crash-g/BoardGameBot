"""This module uses BGG API2 to retrieve data. It has the task to compose query strings and manage connections.
"""
import requests
import logging

import exceptions
import constants
from tools import xml_parser

logger = logging.getLogger("http")

def _sendAPI2Req(requestType, payload):
    """Sends a request to BoardGameGeek using the API.

    Args:
        requestType (str): The final part of the path for this type of request.
        payload (dict): The parameters of the request.

    Returns:
        str: the content of the response.

    Raises:
        .exceptions.BggUnreachable: If the connection fails for any reason.
    """
    path = constants.DEFAULT_API_PATH + requestType
    try:
        # TODO controlla cosa succede con query con caratteri speciali
        r = requests.get(path, params=payload, timeout=constants.DEFAULT_REQUEST_TIMEOUT)
        logger.debug(r.url)
        logger.debug(r.status_code)
        return r.text
    except (requests.exceptions.ConnectionError, requests.exceptions.TooManyRedirects) as err:
        logger.exception("Network error. Check connection.")
        raise exceptions.BggUnreachable(True)
    except requests.exceptions.Timeout as err:
        logger.warning("Http request timeout")
        raise exceptions.BggUnreachable(True) # TODO should be True of False?
    except requests.exceptions.HTTPError as err:
        logger.exception("Http status error")
        raise exceptions.BggUnreachable(False)

def _parseXml(xmlString, parseMethod):
    """Sends the response to :mod:`.xml_parser` to parse it.

    Args:
        xmlString (str): The response to parse.
        parseMethod (Callable[[str],object]): An appropriate method to parse the xml response.

    Returns:
        May be a :class:`.game.Game` object or a list of :class:`.game.GameList` objects,
        depending on the type of reponse.

    Raises:
        .exceptions.NoResultFound: If the xmlString is empty.
    """
    if xmlString is None:
        raise exceptions.NoResultFound()
    else:
        return parseMethod(xmlString)

# raises BggUnreachable, reraises NoResultFound
def _search(requestType, payload, parseMethod):
    """ Manages all kind of searches, retrying connection if there are problems
    and raising an exception if all attempts fail.

    Args:
        requestType (str): The final part of the path for this type of request.
        payload (dict): The parameters of the request.
        parseMethod (Callable[[str],object]): An appropriate method to parse the xml response.
    Returns:
        See ``Returns`` in :func:`~._parseXml`.

    Raises:
        .exceptions.BggUnreachable: If it is not possible to establish a connection.
    """
    retry = True
    attempts = 1
    while retry:
        try:
            queryResult = _sendAPI2Req(requestType, payload)
            return _parseXml(queryResult, parseMethod)
        except exceptions.BggUnreachable as err:
            if err.fatal:
                retry = False
            else:
                attempts += 1
                if attempts > constants.ATTEMPTS_LIMIT:
                    retry = False
    # if we get here, connection did not work
    raise exceptions.BggUnreachable(True)


# PUBLIC

def searchById(id_):
    """Searches a game using its ID.

    Args:
        id_ (str): The ID of the game to search.

    Returns:
        See ``Returns`` in :func:`~._parseXml`.        
    """
    payload = {"id": id_, "stats": 1}
    return _search(constants.REQUEST_KEYWORDS["id_search"], payload, xml_parser.parseGame)

def searchByName(name):
    """Searches a game using a part of its name.

    Args:
        name (str): A part of the name of the game to search.

    Returns:
        See ``Returns`` in :func:`~._parseXml`.        
    """
    payload = {"query": name}
    return _search(constants.REQUEST_KEYWORDS["name_search"], payload, xml_parser.parseGameList)

def searchByNameExact(name):
    """Searches a game using its name.

    Args:
        name (str): The exact name of the game to search.

    Returns:
        See ``Returns`` in :func:`~._parseXml`.        
    """
    payload = {"query": name, "exact": "1"}
    return _search(constants.REQUEST_KEYWORDS["name_search"], payload, xml_parser.parseGameList)
