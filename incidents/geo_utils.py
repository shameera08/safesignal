"""
SafeSignal - incidents/geo_utils.py
Plain-Python distance calculation, no GDAL/PostGIS needed.
"""
from math import radians, cos, sin, asin, sqrt


def haversine_distance_meters(lat1, lon1, lat2, lon2):
    """Great-circle distance between two lat/lng points, in meters."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    earth_radius_m = 6371000
    return earth_radius_m * c
