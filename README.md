# ipv6-heatmap

Use data from MaxMind GeoLite2 to visualize the locations of IPv6 addresses worldwide.

## Installing

1. Create a virtualenv and run `pip install -r requirements.txt` to install the required libraries.
2. Run `./heatmap.py` to start the server.

## Loading Data

In order to load the data you must first start up the web server to create the SQLite database.
Once that is complete click [here](https://dev.maxmind.com/geoip/geoip2/geolite2/) and download the GeoLite2 City data in CSV/zip format. Extract the files and copy the 'GeoLite2-City-Blocks-IPv6.csv' to the heatmap folder. Run `./load.py` to load the data into the database.
