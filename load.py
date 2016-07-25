#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script for loading latest IPv6 data into the database.

Note: If possible this should be moved to an upload method in the API. It's
just barely fast enough now to be feasible, but would need some performance
improvments to really be acceptable. That is why the file name is currently
hard coded, since it would eventually handle the zip file directly.

An even better method would be to pull directly from the geolite web service,
but that was outside the scope of the current project.

"""

from __future__ import division

from csv import DictReader
from collections import defaultdict
from decimal import Decimal

import iptools

import heatmap

# The DB update is a replace, so all the old data should be removed first.
heatmap.Location.query.delete()

# Using decimal.Decimal because IPv6 address space is huge, way bigger than
# sys.maxint.
counts = defaultdict(Decimal)

# Read in each line and update the IP address count for each location. Store
# them in the dict without updating the DB yet, so we can get the totals up
# front and avoid duplicates.
with open('GeoLite2-City-Blocks-IPv6.csv') as f:
    reader = DictReader(f)
    for row in reader:
        location = (float(row['latitude']), float(row['longitude']))
        counts[location] += Decimal(iptools.IpRange(row['network']).__len__())

# Get the total for all locations so we can calculate the percent of each.
total_count = Decimal(sum(x for x in counts.values()))

# Now we calculate the percentage for each location and add them all to the DB.
for (latitude, longitude), count in counts.iteritems():
    percent = count / total_count
    location = heatmap.Location(latitude, longitude, percent)
    heatmap.db.session.add(location)

# It'd be a shame to waste all that time by throwing everything away now...
heatmap.db.session.commit()
