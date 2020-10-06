"""

    Author  : Andrew Emerick
    e-mail  : aemerick11@gmail.com
    year    : 2020

    Front-end for auto-generated hiking and trail running routes
    based on known trail data and given user-specified contraints.

    This is still a large work in progress and code needs heavy cleaning.
    Not the best code I've written. First time building a web app -- (Sep 2020)

"""

from flaskapp import app
from flask import request, redirect, url_for, jsonify, render_template, session, send_file
from flask import Flask, Markup, Response
from flask_session import Session

import bokeh.plotting as bokeh
from bokeh.embed import components, json_item
#from bokeh.models.sources


import json
import ast
import uuid
import os
import numpy as np


SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

_m_in_mi = 1609.34
_m_in_ft = 0.3048

#from autotrail_app.run import GLOBAL_gpx_tracks


_all_session_vars = ['mapclat','mapclng','startlat','startlng','endlat','endlng',
                     'tmap','rr','ll','lname','possible_routes','route_properties',
                     'gpx_tracks','start_node','end_node','trailroutes','units']


#@app.route('/dev')
#def dev():
#    """
#    Hard-code user-input to make for a faster test run of the output.
#    """
#
#    string_args = ['units']
#
#    float_args = ['mindistance',
#                      'maxdistance',
#                      'minelevation',
#                      'maxelevation',
#                      'maxgrade',
#                      'backtrack',
#                      'numroutes','startlat','startlng','endlat','endlng']
#
#    results = {'units' : 'english',
#               'mindistance' : 5.0 * _m_in_mi,
#               'maxdistance' : 8.0 * _m_in_mi,
#               'minelevation' : 1000.0 * _m_in_ft,
#               'maxelevation' : 3000.0 * _m_in_ft,
#               'maxgrade' : 100.0,
#               'mingrade' : 0.0,
#               'backtrack' : 3,
#               'numroutes' : 2,
#               'startlng' :-105.27818,
#               'startlat' :  39.99855,
#               'endlng'   : -105.27818,
#               'endlat'   :  39.99855}
#
#    output, gpx_tracks = run_from_input(results,units =results['units'])
#    du = 'mi'
#    eu = 'ft'
#
#    return redirect( url_for('model_output',
#                 startlat=results['startlat'],startlng=results['startlng'],
#                 trailroutes=json.dumps(output),
#                 du = du, eu = eu))


@app.route('/button/reset_session', methods=['GET'])
def button_reset_session():
    """
    Probably NOT the best way to do this, but reset and clear
    all prior session data. Hard reset.
    """

    if request.method == 'GET':
        for k in _all_session_vars:
            if k in session.keys():
                session[k] = None

        print('reset: ', session)


        return  redirect(url_for("homepage"))


@app.route('/button/display_route', methods=["POST"])
def button_display_route(val=0):

    if request.method == 'POST':
        val = json.loads(request.data)['val']
        array = session['gpx_tracks'][val-1]

        return json.dumps(array)

@app.route('/button/display_trails', methods=["POST"])
def button_display_trails():

    if request.method == 'POST':
        print("gathering trail data ")
        # need to gather ALL gpx tracks into an array
        array = []
        for (u,v,d) in session['tmap'].edges(data=True):
           array.append( [(c[1],c[0]) for c in d['geometry'].coords])

        print("done, ", np.shape(array))
        return json.dumps(array)

@app.route('/button/geocode', methods=['GET'])
def geocode():

    if request.method == 'GET':
        import osmnx.geocoder as geocoder
        lname = request.args.get('lname','')
        lat, lng = geocoder.geocode(lname)

        session['mapclat']=lat
        session['mapclng']=lng

        print("GEOCODING")
        generate_map(lat,lng)
        print("DONE GEOCODING")

        return redirect(url_for('homepage', mapclat=lat, mapclng=lng))

@app.route('/button/dowload_gpx', methods=['GET'])
def button_download_gpx():

    if request.method == 'GET':

        val = int(request.args.get('val','')) - 1

        print("Downloading : ",val)

        if not ('possible_routes' in session.keys()):
            raise RuntimeError


        outname = os.getcwd() + "/outputs/route_" + str(uuid.uuid4()) + ".xml"
        session['tmap'].write_gpx_file(outname, nodes = session['possible_routes'][val])

        filename = "PlanIt_route_" + str(val) + ".xml"

        return send_file(outname,
                         mimetype='text/xml',
                         attachment_filename = filename)


@app.route('/',  methods=["GET","POST"])
def homepage():

    print('homepage requests: ' ,request.args, request.args.get('reset_start',''))
    #print('homepage session: ', session)


    # this is kinda a bad way to do all of this but just trying to
    # get something that works:
    if 'reset_start' in request.args:
        session['startlat'] = None
        session['startlng'] = None

    if 'reset_end' in request.args:
        session['endlat'] = None
        session['endlng'] = None

    lname    = request.args.get('lname',session.get('lname',''))

    mapclat  = request.args.get('mapclat',session.get('mapclat',''),type=float)
    mapclng  = request.args.get('mapclng',session.get('mapclng',''),type=float)

    error    = request.args.get('error','')
    startlat = request.args.get('startlat', session.get('startlat',''), type=float)
    startlng = request.args.get('startlng', session.get('startlng',''), type=float)
    endlat   = request.args.get('endlat', session.get('endlat',''), type=float)
    endlng   = request.args.get('endlng', session.get('endlng',''), type=float)

    session['mapclat']  = mapclat
    session['mapclng']  = mapclng
    session['startlat'] = startlat
    session['startlng'] = startlng
    session['endlat']   = endlat
    session['endlng']   = endlng

    print("HOME PAGE:   ", session['mapclat'], session['mapclng'], session['startlat'],session['startlng'],session['endlat'],session['endlng'])



    return render_template("index.html", startlat=startlat,startlng=startlng,
                                         endlat=endlat, endlng=endlng,
                                         lname=lname,
                                         mapclat=mapclat, mapclng=mapclng,
                                         error=error)



@app.route('/model_input', methods=['POST'])
def model_input():

    if request.method == 'POST':
        print('model_input request.form = ',request.form)

        string_args = ['units']
        float_args = ['mindistance',
                      'maxdistance',
                      'minelevation',
                      'maxelevation',
                      'maxgrade',
                      'backtrack',
                      'numroutes','startlat','startlng','endlat','endlng']

        results = {}

        for k in float_args:
            results[k] = request.form.get(k, '')
            print(k,results[k])
            if (results[k] == '') or (results[k] == None) or (results[k] == 'None'):
                results[k] = None
            else:
                print(k,results[k])
                results[k] = float(results[k])

        for k in string_args:
            results[k] = request.form.get(k, '')

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

            # need to convert to m and km
            for k in ['mindistance','maxdistance']:
                if results[k] is None:
                    continue
                results[k] *= _m_in_mi

            for k in ['minelevation','maxelevation']:
                if results[k] is None:
                    continue
                results[k] *= _m_in_ft

            du = 'mi'
            eu = 'ft'
        else:
            du = 'km'
            eu = 'm'

        session['units'] = results['units']

        output, gpx_tracks = run_from_input(results,units =results['units'])


        trailroutes = []
        dform = '{:5.1f}'
        eform = '{:6.1f}'
        for i, rp in enumerate(output):
            trailroutes.append({'route':i+1,
                           'distance':dform.format(rp['distance']),
                           'elevation_gain':eform.format(rp['elevation_gain']),
                           'elevation_loss':eform.format(rp['elevation_loss']),
                           'repeated_percent':'{:4.2f}'.format(rp['repeated_percent']),
                           'max_altitude':eform.format(rp['max_altitude']),
                           'min_altitude':eform.format(rp['min_altitude']),
                           'min_grade':'{:3.1f}'.format(rp['average_min_grade']),
                           'max_grade':'{:3.1f}'.format(rp['average_max_grade'])})

        print("output in model_input:", output)
        print("trailroutes in model_input:", trailroutes)


        session['trailroutes'] = trailroutes


        #profile_plot = [make_plot(session['tmap'], session['possible_routes'], results['units'])]

        return redirect( url_for('model_output',
                         startlat=session['startlat'],startlng=session['startlng'],
                         numroutes=len(output),
                         trailroutes= json.dumps(trailroutes), # json.dumps(output),
                         #profile_plot=profile_plot,
                         #gpx_tracks = json.dumps(gpx_tracks),
                         #gpx_tracks=json.dumps(gpx_tracks),
                         du = du, eu = eu))



@app.route('/model_output/<startlat>/<startlng>/<numroutes>/<trailroutes>/<du>/<eu>', methods=['GET','POST'])
def model_output(startlat, startlng, numroutes, trailroutes, du, eu):
    """
    Prepare and render the results
    """

    if request.method == 'GET':
        return render_template("model_output.html", startlat=startlat,startlng=startlng,
                                                    numroutes=numroutes,
                                                    trailroutes=ast.literal_eval(trailroutes),
                                                    #profile_plot=profile_plot,
                                                    du=du,
                                                    eu=eu)


@app.route('/mapclick')
def mapclick():
    """
    Map click action button. grab lat / long coordinates of start and end points
    """

    lname    = request.args.get('lname',session.get('lname',''))

    mapclat  = request.args.get('mapclat',session.get('mapclat',''),type=float)
    mapclng  = request.args.get('mapclng',session.get('mapclng',''),type=float)

    startlat = request.args.get('startlat', session.get('startlat',''), type=float)
    startlng = request.args.get('startlng', session.get('startlng',''), type=float)
    endlat   = request.args.get('endlat', session.get('endlat',''), type=float)
    endlng   = request.args.get('endlng', session.get('endlng',''), type=float)

    for k in ['startlng','startlat','endlng','endlat']:
        session[k] = request.args.get(k,'',type=float)

        return redirect(url_for('homepage', startlat=startlat,
                                            startlng=startlng,
                                            endlat=endlat, endlng=endlng,
                                            lname=lname, mapclat=mapclat, mapclng=mapclng))
  #return render_template("form.html", longitude=longitude, latitude=latitude)



def generate_map(mapclat, mapclng,
                 radius = 40233.6): # 50 miles (in m)
    """
    Download and set up map from osmnx. If the trail map object or the OSM
    object associated with the bounding box exists on file already, loads
    this instead.
    """

    from planit.osm_data import osm_process

    # outname = '/home/aemerick/code/planit/autotrail/data/boulder_area_trail_processed'
    # tmap = gpx_process.load_graph(outname)

    # hard code for now
#    place_name = "Boulder, CO"
#
#    if place_name == 'Boulder, CO':
#        north = 40.100141
#        west  = -105.408908
#        south = 39.841447
#        east  = -105.163064
#    elif place_name == 'Pasadena, CA':
#        north = 34.305256
#        west  = -118.139268
#        south = 34.166495
#        east  = -117.862647
#    elif place_name == 'VT':
#        center = (44.524050, -72.821687)
    #    north = center[0] + 0.075
    #    south = center[0] - 0.075
    #    east  = center[1] + 0.075
    #    west  = center[1] - 0.075
    #
    #ll = (south,west)
    #rr = (north,east)


    tmap = None
#    if 'll' in session.keys() and 'rr' in session.keys():
#        if ll == session['ll'] and rr == session['rr'] and 'tmap' in session.keys():
#            if ll == session['tmap'].ll and rr == session['tmap'].rr:
#                tmap = session['tmap']
#                print("map already found with ", tmap.ll, tmap.rr)

    if tmap is None:
        center_point = (session['mapclat'], session['mapclng'])
        print("Making map with center: ", center_point)
        tmap = osm_process.osmnx_trailmap(center_point = center_point,
                                          dist=radius)

        session['tmap'] = tmap
        session['ll']   = tmap.ll
        session['rr']   = tmap.rr

        print("map made with: ", tmap.ll, tmap.rr)

    tmap.ensure_edge_attributes()

    tmap._default_weight_factors = {'distance'          : 1,
                                    'elevation_gain'    : 0,
                                    'elevation_loss'    : 0,      # off
                                    'average_grade'     : 0,
                                    'average_max_grade' : 0,
                                    'average_min_grade' : 0,
                                    'min_grade'         : 0,           # off
                                    'max_grade'         : 0,           # off
                                    'traversed_count'   : 100,    # very on
                                    'in_another_route'  : 2}

    return

def run_from_input(results, units='english'):
    """
    This needs to be moved to a compute.py (or something) file. Actually runs
    the backend from the user input.
    """

    if not ('tmap' in session.keys()):
        print("TMAP NOT FOUND - RUNNING FROM INPUT FAILING")
        raise RuntimeError
    else:
        tmap = session['tmap']

    if not (session.get('start_node',None) is None):
        start_node = session['start_node']
    else:
        start_node = tmap.nearest_node(results['startlng'], results['startlat'])[1]
        start_node = start_node[0]
        session['start_node'] = start_node
        session['startlng'] = results['startlng']
        session['startlat'] = results['startlat']

    if not (session.get('end_node',None) is None):
        end_node = session['end_node']
    else:
        if (results['endlat'] in [None,'']) or (not (type(results['endlat']) in [float,int])):
            end_node = start_node
        else:
            end_node = tmap.nearest_node(results['endlng'], results['endlat'])[1]
            end_node = end_node[0]

        session['end_node'] = end_node
        session['endlng'] = results['endlng']
        session['endlat'] = results['endlat']

    print("CHOSEN NODES: ", start_node, end_node)

    if (start_node == None) or (end_node == None):
        print("Cannot find a node!!")
        raise RuntimeError

    distance = 0.5*(float(results['mindistance']) + float(results['maxdistance']))

    n_routes = int(results['numroutes'])

    target_values = {'distance' : distance}

    print('---', results)
    print("---", start_node, end_node, target_values)

    _, possible_routes, scores = tmap.multi_find_route(start_node,
                                                                target_values,
                                                                n_routes=n_routes,
                                                                end_node = end_node,
                                                                reinitialize=True,
                                                                reset_used_counter=True)

    # get the dictionary of route statistics
    route_properties = [ tmap.route_properties(nodes=nodes,
                                                   verbose=True,
                                                   units=units) for nodes in possible_routes]
    for i in range(len(scores)):
        route_properties[i]['score'] = scores[i]

    gpx_tracks = [tmap.get_route_coords(nodes=nodes, coords_only=True) for nodes in possible_routes]

    session['possible_routes']  = possible_routes
    session['route_properties'] = route_properties
    session['gpx_tracks']       = gpx_tracks

    return route_properties, gpx_tracks


@app.route("/model_output/profile_plot")
def bokeh_plot():

    p = make_plot(session['tmap'],session['possible_routes'], session['units'])

    return json.dumps(json_item(p,'profile_plot'))

def make_plot(tmap, possible_routes, units):

    num_routes = len(possible_routes)

    if num_routes <= 3:
        height = 200
    elif num_routes <= 5:
        height = 250
    elif num_routes > 5:
        height = 325

    plot = bokeh.figure(plot_height=height,
                        plot_width=750)
                        #sizing_mode='scale_width')

    if units == 'english':
        dconv = _m_in_mi
        econv = _m_in_ft
        dlabel = 'mi'
        elabel = 'ft'
    else:
        dconv = 1.0
        econv = 1.0
        dlabel = 'km'
        elabel = 'm'


    line_colors = ['#1f78b4', '#33a02c', '#e31a1c','#ff7f00','#6a3d9a',
                   '#a6cee3', '#b2df8a', '#fb9a99', '#fdbf6f','#cab2d6']

    for i in range(len(possible_routes)):
        dists = np.cumsum(tmap.reduce_edge_data('distances',nodes=possible_routes[i],function=None)) / dconv
        alts  = tmap.reduce_edge_data('elevations',nodes=possible_routes[i],function=None) / econv

        ech = alts[1:] - alts[:-1]
        eg = np.sum(ech[ech>0])
        el = np.sum(ech[ech<0])
        print("Route %i gain / loss "%(i),np.sum(eg),np.sum(el))

        plot.line(dists,alts,line_width=4,legend_label='Route %i'%(i+1), color = line_colors[i])

    plot.xaxis.axis_label = 'Distance (%s)'%(dlabel)
    plot.yaxis.axis_label = 'Elevation (%s)'%(elabel)
    plot.legend.location = "top_left"
    plot.legend.background_fill_alpha = 0.0

    return plot
#    script, div = components(plot)
#    return script, div
