import sys
sys.path.insert(0, "../boardgamebot")

from tools import http
import exceptions

try:
    print(http.searchByName("Pandemic Iberia").toString())
    print(http.searchByNameExact("Pandemic").toString())
    print(http.searchById(131691).toString())
except exceptions.BggUnreachable:
    print("Bgg unreachable")
except exceptions.NoResultFound:
    print("No result found")
