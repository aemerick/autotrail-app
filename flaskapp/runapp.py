from flask import render_template
from flaskapp import app
# from flaskapp.a_model import ModelIt
import pandas as pd
from flask import request, redirect, url_for
import folium
from flask import Flask, Markup

import json
from .forms import RouteProperties


@app.route('/')
def homepage():
    start_coords = (40.0150, -105.2705)
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


    error = request.args.get('error',None)
    return render_template("index.html", map_div=map_div,
                                         hdr_txt=hdr_txt,
                                         script_txt=script_txt,
                                         error=error)

@app.route('/api/model_input', methods=['GET'])
def model_input():

    if request.method == 'GET':

        string_args = ['units']
        float_args = ['mindistance',
                      'maxdistance',
                      'minelevation',
                      'maxelevation',
                      'maxgrade',
                      'backtrack',
                      'numroutes']

        results = {}

        for k in float_args:
            results[k] = request.args.get(k, '')
            if results[k] == '':
                results[k] = None
            else:
                results[k] = float(results[k])

        for k in string_args:
            results[k] = request.args.get(k, '')

        error = None
        if (results['mindistance'] is None) and (results['maxdistance'] is None):
            error = "Currently, both min and max distances MUST be provided. Please try again."
        elif (results['mindistance'] is None):
            results['mindistance'] = results['maxdistance']
        elif (results['maxdistance'] is None):
            results['maxdistance'] = results['mindistance']

        if not (error is None):
            return redirect(url_for('homepage', error=error)) # messages={'error':error}))

        if results['units'] == 'english':
            m_in_mi = 1609.34
            m_in_ft = 0.3048

            # need to convert to m and km
            for k in ['mindistance','maxdistance']:
                if results[k] is None:
                    continue
                results[k] *= m_in_mi

            for k in ['minelevation','maxelevation']:
                if results[k] is None:
                    continue
                results[k] *= m_in_ft

            du = 'mi'
            eu = 'ft'
        else:
            du = 'km'
            eu = 'm'

        output = run_from_input(results,units =results['units'])

        #model_output(results)
        return redirect( url_for('model_output',
                         trailroutes=json.dumps(output), du = du, eu = eu))

        #request.referrer)


@app.route('/api/model_output')
def model_output():

    all_rp = json.loads(request.args.get('trailroutes'))
    du = request.args.get('du')
    eu = request.args.get('eu')

    trailroutes = []
    #
    # for just one for now
    #

    dform = '{:5.1f}'
    eform = '{:6.1f}'
    for i, rp in enumerate(all_rp):
        trailroutes.append({'route':i+1,
                       'distance':dform.format(rp['distance']),
                       'elevation_gain':eform.format(rp['elevation_gain']),
                       'elevation_loss':eform.format(rp['elevation_loss']),
                       'repeated_percent':'{:4.2f}'.format(rp['repeated_percent']),
                       'max_altitude':eform.format(rp['max_altitude']),
                       'min_altitude':eform.format(rp['min_altitude']),
                       'min_grade':'{:3.1f}'.format(rp['min_grade']),
                       'max_grade':'{:3.1f}'.format(rp['max_grade'])})


    return render_template("model_output.html", trailroutes=trailroutes,
                                                eu = eu,
                                                du = du)


def run_from_input(results, units='english'):
    """
    move to a compute file
    """
    from autotrail.autotrail.autotrail import TrailMap
    from autotrail.autotrail import process_gpx_data as gpx_process

    outname = '/home/aemerick/code/autotrail/autotrail/data/boulder_area_trail_processed'
    trailmap = gpx_process.load_graph(outname)
    trailmap.ensure_edge_attributes()

    distance = 0.5*(float(results['mindistance']) + float(results['maxdistance']))

    n_routes = int(results['numroutes'])

    target_values = {'distance' : distance}

    start_node = 1041
    end_node   = 1762

    _, possible_routes, scores = trailmap.multi_find_route(start_node,
                                                                target_values,
                                                                n_routes=n_routes,
                                                                end_node = end_node,
                                                                reset_used_counter=False)

    # get the dictionary of route statistics
    route_properties = [ trailmap.route_properties(nodes=nodes, verbose=False, units=units) for nodes in possible_routes]
    for i in range(len(scores)):
        route_properties[i]['score'] = scores[i]

    return route_properties
