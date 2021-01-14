import math
import georaptor
import pygeohash
from .constants import EARTH_RADIUS_METERS, GRID_WIDTH, GRID_HEIGHT

# grabbed this code from here
# https://medium.com/@alexander.mueller/experiments-with-in-memory-spatial-radius-queries-in-python-e40c9e66cf63
# https://github.com/dice89/proximityhash

def _in_circle_check(lat: float, lng: float, centre_lat: float, centre_lng: float, radius: float) -> float:
    """Checks if given latng are within the circle."""
    x_diff = lng - centre_lng
    y_diff = lat - centre_lat
    return math.pow(x_diff, 2) + math.pow(y_diff, 2) <= math.pow(radius, 2)


def _get_centroid(lat: float, lng: float, height: float, width: float) -> tuple[float, float]:
    """Gets the centroid of a bounding box."""
    y_cen = lat + (height / 2)
    x_cen = lng + (width / 2)
    return x_cen, y_cen


def _convert_to_latlon(y: float, x: float, lat: float, lng: float) -> tuple[float, float]:
    """Converts a grid coordinate to a latlng."""
    lat_diff = (y / EARTH_RADIUS_METERS) * (180 / math.pi)
    lon_diff = (x / EARTH_RADIUS_METERS) * (180 / math.pi) / math.cos(lat * math.pi / 180)
    final_lat = lat + lat_diff
    final_lng = lng + lon_diff
    return final_lat, final_lng


def georadius(lat: float, lng: float, radius: float,
        precision: int, minlevel: int = 1, maxlevel: int = 12) -> set[str]:
    """Calculates a set of geohashes that cover a circular area
    around latlng of the given radius in metres."""
    height = (GRID_HEIGHT[precision - 1]) / 2
    width = (GRID_WIDTH[precision - 1]) / 2

    lat_moves = int(math.ceil(radius / height))
    lng_moves = int(math.ceil(radius / width))

    x = 0.0
    y = 0.0
    geohashes = set()

    for i in range(lat_moves):
        temp_lat = y + height * i
        for j in range(lng_moves):
            temp_lng = x + width * j
            if _in_circle_check(temp_lat, temp_lng, y, x, radius):
                # calc the coord of each corner of the rectangular grid cell
                x_cen, y_cen = _get_centroid(temp_lat, temp_lng, height, width)
                lat0, lng0 = _convert_to_latlon(y_cen, x_cen, lat, lng)
                lat1, lng1 = _convert_to_latlon(-y_cen, x_cen, lat, lng)
                lat2, lng2 = _convert_to_latlon(y_cen, -x_cen, lat, lng)
                lat3, lng3 = _convert_to_latlon(-y_cen, -x_cen, lat, lng)
                geohashes.add(pygeohash.encode(lat0, lng0, precision))
                geohashes.add(pygeohash.encode(lat1, lng1, precision))
                geohashes.add(pygeohash.encode(lat2, lng2, precision))
                geohashes.add(pygeohash.encode(lat3, lng3, precision))
    # optimisation step that minimises the number of geohashes
    # by reducing the precision when possible
    return georaptor.compress(geohashes, minlevel, maxlevel)
