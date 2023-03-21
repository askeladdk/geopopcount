# Geospatial population count service

This project implements a service that answers the question

*"How many people live in the area around (city), approximately?"*

The service covers cities all over the world. Requests are handled within milliseconds unless the radius is extremely large (> 10000km). Scroll down for implementation details.

To run it in Docker, do this:

    ./update.sh
    ./build.sh
    ./run.sh

You will be redirected to the browser.

When you are done, run:

    ./stop.sh

If you don't want to run Docker, do this:

    ./update.sh
    pip install -r requirements.txt
    flask run

Note that this runs Flask's builtin HTTP server which is not suited for production. [Read this](https://flask.palletsprojects.com/en/1.1.x/deploying/) for instructions on how to deploy in production.


## Scripts

There are several scripts that control the deployment of the service.
They are pretty simple and take no arguments so there is nothing to mess up.

### ./build.sh

Builds the Docker image.

### ./run.sh

Runs the geopopcountd service in a container.

Will automatically open the browser on OSX.
Otherwise it will print a URL in the console.

Run it after the build script.

### ./stop.sh

Stops a running geopopcountd container.

### ./update.sh

Run this script to download the latest cities500.txt file.

You should run the build script again to update the docker image.

### ./tests.py

Runs unit tests.

Install the requirements first:

    pip install -r requirements.txt

### ./bench.py

Runs benchmarks.


## API

Documentation of the API.

### /api/v1/popcount?place=PLACE&radius=RADIUS

This endpoint calculates the total population count of `place` and all surrounding places within `radius` metres. The place name is case-insensitive. The response is a JSON object.

**Example request**

    http://localhost:5000/api/v1/popcount?place=taipei&radius=10000

**Example response**

    {
        "nearby": ["Banqiao", "Taipei"],
        "place": "Taipei",
        "population": 8415242,
        "radius": 10000
    }


## Implementation details

The `cities500.txt` downloaded from geoplaces.org contains a list of world-wide places, their latitude and longitude and their population count. The service reads this list, keeping only the most populated place when multiple places share the same name.

For each place coordinate, we calculate its [geohash](https://en.wikipedia.org/wiki/Geohash). Geohashes have the useful property that a common prefix indicates geographic proximity. The geohashes are inserted in a [prefix trie](https://en.wikipedia.org/wiki/Trie), which is a data structure that efficiently finds strings that share a common prefix. The trie effectively becomes a spatial index. When a request comes, we calculate a set of geohashes around the requested coordinate that roughly covers the requested radius. Each calculated geohash is essentially a bucket that contains zero or more places. This drastically reduces the number of places that we must consider to be inside the radius. The final step compares the coordinates of all remaining places to the centre coordinate using the [haversine distance formula](https://www.geeksforgeeks.org/haversine-formula-to-find-distance-between-two-points-on-a-sphere). Only those places that are within the radius are part of the result set.
