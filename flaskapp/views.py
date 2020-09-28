from flask import render_template
from flaskapp import app
# from flaskapp.a_model import ModelIt
import pandas as pd
from flask import request
import folium
from flask import Flask, Markup


@app.route('/')
def homepage():
    start_coords = (-26.52, 153.09)
    folium_map = folium.Map(location=start_coords, zoom_start=13, width='80%')

    # Extract the components of the web map

    #
    #  The HTML to create a <div>  to hold the map
    #
    #  The header text to get styles, scripts, etc
    #
    #  The scripts needed to run

    # first, force map to render as HTML, for us to dissect
    _ = folium_map._repr_html_()

    # get definition of map in body
    map_div = Markup(folium_map.get_root().html.render())

    # html to be included in header
    hdr_txt = Markup(folium_map.get_root().header.render())

    # html to be included in <script>
    script_txt = Markup(folium_map.get_root().script.render())
    return render_template("model_page.html", map_div=map_div, hdr_txt=hdr_txt, script_txt=script_txt)



@app.route('/')
def index():
    start_coords = (46.9540700, 142.7360300)
    folium_map = folium.Map(location=start_coords, zoom_start=14)
    return folium_map._repr_html_()
