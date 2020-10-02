"""
    Author  : Andrew Emerick
    e-mail  : aemerick11@gmail.com
    year    : 2020

    LICENSE :GPLv3

    Cache data associated with certain geotags returned from OSM.
    Cached files are saved in "cache" subdirectory of current working directory.
    Currently saved by bounding box lat long and within 25 miles of search area

    Auto-generated hiking and trail running routes anywhere where
    OSM has hiking data available. Optimized routes are
    based on given user-specified contraints.
"""
import os
import numpy as np
import osmnx.geocoder as geocoder


from planit.osm_data import osm_process

def cache_maps(locations = ['Boulder, CO'], radius = 40233.6):
    """
    Cheating a bit. Pre-caching maps within 50 miles of a geotag
    location
    """


    for name in locations:
        print("CACHING: ", name)
        lat, lng = geocoder.geocode(name)
        center_point = (lat,lng)

        tmap = osm_process.osmnx_trailmap(center_point = center_point,
                                  dist = radius)


    return


if __name__ == "__main__":

    locations = ['Boulder, CO',
                 "Mount Wilson California",
                 "Bear Mountain State Park, New York",
                 "Mount Washington, New Hampshire",
                 "Issaquah Washington",
                 "Boise Idaho",
                 "Yosemite National Park",
                 "Tegernsee Germany"]

    cache_maps(locations)
