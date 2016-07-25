#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

app = Flask(__name__)
#TODO: This should be much faster with a real database instead of sqlite.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///heatmap.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Location(db.Model):
    """ DB model for location data.

    Args:
        latitude (float): The latitude for this location.
        longitude (float): The longitude for this location.
        percent (float): Percent of all addresses assigned to this location.
    
    Notes: Initially the plan was to use a raw count of IP addresses at each
    location. However, those numbers proved to be entirely too large due to the
    size of the IPv6 space. My next plan was to divide each location by the size
    of the smallest block. However, that was 1, which did not help. Attempt #3,
    which solved the problem of how to accurately store the relative sizes
    without dealing with huge numbers was to calculate the order of magnitude
    for each location, then divide each row by the largest magnitude to get the
    intensity value for the map. Unfortunately this does not handle combining
    nearby locations easily, which will be necessary later. So, we now simply
    use the percentage of all IP addresses that are at the given location. This
    works well for combining them later, and also guarantees that they are less
    than 1, so we can use them for the intensity value without any further
    calculations in the API method or in the UI. If we wanted more variation in
    the intensity levels it would be possible to normalize these instead, but
    in my testing lowering minOpacity settings in leaflets aren't visible and
    with it set high the variation in intensity is minimal.
    """

    __tablename__ = 'location'
    __table_args__ = (db.UniqueConstraint('latitude', 'longitude'), {})

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    percent = db.Column(db.Float)

    def __init__(self, latitude, longitude, percent):
        self.latitude = latitude
        self.longitude = longitude
        self.percent = percent

    def to_json(self):
        """ Custom representation of object as dict for JSON serialization.
        TODO: The better way to handle this long term might be a custom class
              for JSON serialization. However, due to the amount of data this
              will eventually be replaced with Protocol Buffers instead.

        """
        return {'latitude': self.latitude,
                'longitude': self.longitude,
                'percent': self.percent}

    def __repr__(self):
        return '<Location (Latitude: %r, Longitude: %r, Percent: %r)>' % (
            self.latitude, self.longitude, self.percent)


@app.route('/locations', methods=['GET'])
def locations():
    """ Get all locations within a given area.

    Args:
        north: Latitude for northern border of the area.
        south: Latitude for southern border of the area.
        east: Longitude for eastern border of the area.
        west: Longitude for western border of the area.

    Returns:
        locations: List of all locations within the area.
    """

    north = float(request.args.get('north', 90))
    south = float(request.args.get('south', -90))
    east = float(request.args.get('east', 180))
    west = float(request.args.get('west', -180))
    # This query gets a full list of all the locations within the given area.
    # TODO: For better performance it may be useful to find a way to group the
    #       locations to return fewer results when viewing large areas. We are
    #       using percent rather than raw count or a pre-calculated intensity
    #       to allow for easier combinations of locations later.
    query = Location.query.filter(and_(Location.latitude <= north,
                                       Location.latitude >= south,
                                       Location.longitude <= east,
                                       Location.longitude >= west))
    # See TODO under Location.to_json for why this is currently using JSON. It
    # will be replaced with Protocol Buffers in the future.
    return jsonify(locations=[loc.to_json() for loc in query.all()])


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    db.create_all()
    app.run()
