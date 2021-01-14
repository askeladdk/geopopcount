import csv
import math
import typing
import pygeohash
import pygtrie
from .constants import EARTH_RADIUS_METERS
from .georadius import georadius

class Coord(typing.NamedTuple):
    """Coord is a geographical coordinate."""
    lat : float
    lng : float

    def hash(self, precision: int = 12) -> str:
        """Computes the geohash."""
        return pygeohash.encode(self.lat, self.lng, precision)

    def distance(self, other: 'Coord') -> float:
        """Computes the distance between two coordinates in metres."""
        # https://www.geeksforgeeks.org/haversine-formula-to-find-distance-between-two-points-on-a-sphere/
        dLat = (other.lat - self.lat) * math.pi / 180.0
        dLon = (other.lng - self.lng) * math.pi / 180.0
        lat1 = self.lat * math.pi / 180.0
        lat2 = other.lat * math.pi / 180.0
        a = pow(math.sin(dLat / 2), 2) +\
            pow(math.sin(dLon / 2), 2) * math.cos(lat1) * math.cos(lat2)
        return EARTH_RADIUS_METERS * 2 * math.asin(math.sqrt(a))


class Place(typing.NamedTuple):
    """Place is any place on Earth."""
    name: str
    coord: Coord
    population: int


# CSV columns:
#  0 geonameid         : integer id of record in geonames database
#  1 name              : name of geographical point (utf8) varchar(200)
#  2 asciiname         : name of geographical point in plain ascii characters, varchar(200)
#  3 alternatenames    : alternatenames, comma separated, ascii names automatically transliterated, convenience attribute from alternatename table, varchar(10000)
#  4 latitude          : latitude in decimal degrees (wgs84)
#  5 longitude         : longitude in decimal degrees (wgs84)
#  6 feature class     : see http://www.geonames.org/export/codes.html, char(1)
#  7 feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
#  8 country code      : ISO-3166 2-letter country code, 2 characters
#  9 cc2               : alternate country codes, comma separated, ISO-3166 2-letter country code, 200 characters
# 10 admin1 code       : fipscode (subject to change to iso code), see exceptions below, see file admin1Codes.txt for display names of this code; varchar(20)
# 11 admin2 code       : code for the second administrative division, a county in the US, see file admin2Codes.txt; varchar(80) 
# 12 admin3 code       : code for third level administrative division, varchar(20)
# 13 admin4 code       : code for fourth level administrative division, varchar(20)
# 14 population        : bigint (8 byte int) 
# 15 elevation         : in meters, integer
# 16 dem               : digital elevation model, srtm3 or gtopo30, average elevation of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in meters, integer. srtm processed by cgiar/ciat.
# 17 timezone          : the iana timezone id (see file timeZone.txt) varchar(40)
# 18 modification date : date of last modification in yyyy-MM-dd format


def read_places_from_csv(f):
    """Given a file-like object that encapsulates a CSV, returns a list of Places."""
    places = {}
    for row in csv.reader(f, delimiter='\t'):
        name = row[1]
        population = int(row[14])
        last_place = places.get(name)
        # disambiguate duplicate place names by keeping only the largest
        # we only care about the real amsterdam
        if last_place is None or population > last_place.population:
            places[name] = Place(
                name=name,
                coord=Coord(float(row[4]), float(row[5])),
                population=population,
            )
    return places.values()


class SpatialIndex(object):
    """
    SpatialIndex associates geographic coordinates with values and indexes them for quick lookups.

    The index is implemented as a prefix trie that stores geohashes of coordinates.
    This works because geohashes that share a common prefix are geographically nearby,
    and prefix tries are fast at enumerating elements that share a prefix.
    """
    def __init__(self, precision: int = 12):
        self._trie = pygtrie.Trie()
        self._precision = precision
    def add(self, coord: Coord, value: typing.Any):
        """Associates a coordinate with a value."""
        self._trie[coord.hash(self._precision)] = value
    def nearby(self, centre: Coord, radius: int, precision: int) -> typing.Generator[typing.Any, None, None]:
        """Given a centre coordinate and radius in metres,
        yields a generator of values that exist the approximate area."""
        for h in georadius(centre.lat, centre.lng, radius, precision):
            try:
                candidates = self._trie.values(h)
            except KeyError: # values throws if key does not exist
                continue
            for candidate in candidates:
                yield candidate


class PopulationCounter(object):
    """PopulationCounter encapsulates a set of Places and a SpatialIndex."""
    def __init__(self, cities: list[Place] = []):
        self._index = SpatialIndex(precision=5) # precision was experimentally determined
        self._places = {}
        for city in cities:
            self._index.add(city.coord, city)
            self._places[city.name.lower()] = city
    def locate(self, name: str) -> Place:
        """Given a place name, returns that Place or None if it is not found."""
        return self._places.get(name.lower(), None)
    def popcount(self, place: Place, radius: int) -> tuple[int, list[str]]:
        """Given a place and radius in metres, returns the approximate population count in the area."""
        # nearby sometimes does not return the centre place for some reason,
        # (maybe a bug in pygtrie?) so add it manually to ensure it is counted.
        population = place.population
        places = [place.name]
        for candidate in self._index.nearby(place.coord, radius, 4): # precision was experimentally determined
            if candidate is not place and place.coord.distance(candidate.coord) <= radius:
                population += candidate.population
                places.append(candidate.name)
        return population, places
