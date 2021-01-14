from flask import Flask, request, jsonify
from . import spatial

class ErrorResponse(Exception):
    """Raise ErrorResponse whenever a status error needs to be returned to the client."""
    message: str
    code: int
    def __init__(self, message: str, code: int = 400):
        super().__init__(self)
        self.message = message
        self.code = code

# read the cities file
with open('cities500.txt') as f:
    popcounter = spatial.PopulationCounter(spatial.read_places_from_csv(f))

app = Flask(__name__)

@app.errorhandler(ErrorResponse)
def error(exc: ErrorResponse):
    """Converts an ErrorResponse to a json response."""
    return jsonify({'message': exc.message, 'code': exc.code}), exc.code

@app.route('/')
def hello():
    """Just a default endpoint."""
    return 'hello world'

@app.route('/api/v1/popcount')
def popcount():
    """This endpoint is where the magic happens."""
    # input validation
    place_name = request.args.get('place', '')
    try:
        radius = int(request.args.get('radius'))
    except (TypeError, ValueError):
        raise ErrorResponse('radius is not an integer')
    if radius < 1:
        raise ErrorResponse('radius must be greater than zero')
    place = popcounter.locate(place_name)
    if place is None:
        raise ErrorResponse('place not in database', 404)
    # do the thing
    population, nearby = popcounter.popcount(place, radius)
    nearby.sort()
    return jsonify({
        'place': place.name,
        'radius': radius,
        'population': population,
        'nearby': nearby,
    })
