from flask import render_template
from flaskapp import app
# from flaskapp.a_model import ModelIt
import pandas as pd
from flask import request, redirect, url_for
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
    return render_template("index.html", map_div=map_div, hdr_txt=hdr_txt, script_txt=script_txt)

@app.route('/api/model_input', methods=['GET'])
def model_input():

    if request.method == 'GET':

        args = ['mindistance','maxdistance','minelevation','maxelevation',
                'maxgrade','backtrack']

        results = {}
        for k in args:
            results[k] = request.args.get(k, '-1.0')

        print(results)

        output = run_from_input(results)

        return redirect(request.referrer)


def run_from_input(results):
    """

    """
    from autotrail.autotrail.autotrail import TrailMap
    from autotrail.autotrail import process_gpx_data as gpx_process


    outname = '/home/aemerick/code/autotrail/autotrail/data/boulder_area_trail_processed'
    trailmap = gpx_process.load_graph(outname)
    trailmap.ensure_edge_attributes()

    m_in_mi = 1609.34

    distance = 0.5*(float(results['mindistance']) + float(results['maxdistance'])) * m_in_mi

    target_values = {'distance' : distance}


    totals, nodes = trailmap.find_route(1041,
                                  target_values,
                                  end_node=1762, reinitialize=True, reset_used_counter=True)

    return trailmap.route_properties(nodes=nodes)


#@app.route('/api/output')
