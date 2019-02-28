import requests
from os import getenv
import sys


def get_all_routes(sess):
    """
    Get data of all rail routes. Takes in the Session object, which is mostly used to track API key. Returns a dictonary
    mapping route IDs -> Route JSON.

    Route JSON Example:
    {'attributes':
        {'color': 'DA291C',
         'description': 'Rapid Transit',
         'direction_destinations': ['Ashmont/Braintree', 'Alewife'],
         'direction_names': ['South', 'North'],
         'fare_class': 'Rapid Transit',
         'long_name': 'Red Line',
         'short_name': '',
         'sort_order': 10010,
         'text_color': 'FFFFFF',
         'type': 1},
    'id': 'Red',
    'links':
        {'self': '/routes/Red'},
    'relationships':
        {'line':
            {'data':
                {'id': 'line-Red',
                'type': 'line'}}},
    'type': 'route'}

    :param sess: Session object containing API key
    :returns Dictonary of route IDs to route JSON.
    """
    route_url = "https://api-v3.mbta.com/routes"

    # I use a filter before sending a request to reduce unneeded bandwidth and to keep the
    # runtime of analysis down by reducing the time needed for that check.
    parameters = {"filter[type]":"0,1"} # Filter by rail only routes

    ret = sess.get(route_url, params = parameters)
    return format_data(ret.json())


def print_route_names(route_data):
    """
    Given formatted Route data, print out all the long names.
    :param route_data: A dictonary of route IDS mapped to JSON returned from routes request
    """
    print("===Long names for routes===")
    for route_id in route_data.keys():
        print(route_data[route_id]['attributes']['long_name'], "\n")
    print("===End of Print===")

def print_route_ids(route_json):
    print("===IDs for routes===")
    for route_data in route_json['data']:
        print(route_data['id'], "\n")
    print("===End of Print===")


def get_all_stops(route_ids, session):
    """
    Return a dict mapping ID -> stop JSON data. Includes all stops that are serviced by any routes within the given list
     of route_ids.

     Example of Stop JSON data:
        {'attributes':
            {'address': 'Commonwealth Ave and Lake St, Boston, MA 02135',
            'description': None,
            'latitude': 42.340081,
            'location_type': 1,
            'longitude': -71.166769,
            'name': 'Boston College',
            'platform_code': None,
            'platform_name': None,
            'wheelchair_boarding': 1},
        'id': 'place-lake',
        'links':
            {'self': '/stops/place-lake'},
        'relationships':
            {'child_stops': {},
            'facilities':
                {'links':
                    {'related': '/facilities/?filter[stop]=place-lake'}},
            'parent_station': {'data': None}},
        'type': 'stop'}

    :param route_ids: A list of route IDs
    :param session: Session object containing API key
    :return: Dictonary mapping stop ID to stop JSON data for all stops serviced by the routes in route_ids
    """
    stops_url = "https://api-v3.mbta.com/stops"

    route_id_string = ",".join(route_ids) # Convert list to comma separated string for API call
    if len(route_ids) == 1:
        route_id_string = route_ids[0]

    params = {"filter[route]": route_id_string}

    stop_ret = session.get(stops_url, params=params)

    return format_data(stop_ret.json())


def get_stops_per_route(route_data, session):
    """
    Return a dictionary that contains the route ID followed by a list of stop IDs serviced by that route.
    :param route_data: A dictionary of route IDS mapped to JSON returned from routes request
    :return A dictionary mapping route ID to a list of stop IDs serviced by that route.
    """
    stop_data = dict()
    for route_id in route_data.keys():
        stops_data = get_all_stops([route_id], session)

        stop_data[route_id] = stops_data.keys()

    return stop_data

def format_data(data_json):
    """
    Given JSON for a data object, either routes or stops, rework data to be a dictionary with the ID pointing to the
    JSON information, instead of a list of JSON dictionaries. This makes getting data by ID easier, rather than having
    to search through an entire list.

    For Example:
    [original data]
    {'data': [{'attributes':{'color':'red'}, 'id':'Red'}, {'attributes':{'color':'green'}, 'id':'Green-1'}]}

    [new data]
    {'Red':{'attributes':{'color':'red'}, 'id':'Red'}, 'Green-1':{'attributes':{'color':'green'}, 'id':'Green-1'}}

    :param data_json:
    :return:
    """
    data_dict = dict()
    for vals in data_json['data']:
        data_dict[vals['id']] = vals

    return data_dict


def get_routes_per_stop(routes_to_stops):
    """
    Given a dict matching Route IDS to Stop IDs, return a dictionary which maps Stop IDs to Route IDs.
    """
    stops_to_routes = dict()
    for route in routes_to_stops.keys():
        # TODO finish
        for stop in routes_to_stops[route]:
            if stop in stops_to_routes:
                stops_to_routes[stop].append(route)
            else:
                stops_to_routes[stop] = [route]

    return stops_to_routes


def get_routes(stop_id, session):
    """
    Given the stop ID or multiple stop IDs seperated by commas, return all the routes that service that stop in JSON
    format.
    :param stop_id:
    :param session:
    :return:
    """

def print_stops_data(stops_data, route_data, stops_to_routes, routes_to_stops):
    """
    Print out the route with the most stops, the route with the least, and all the stops that connect 2 or more routes.
    :param stops_data_json:
    :param route_data_json:
    :return:
    """
    # Start with a random route
    most_route = list(route_data)[0]
    least_route = list(route_data)[0]
    # Get routes with most and least stops
    for route in routes_to_stops.keys():
        if len(routes_to_stops[route]) > len(routes_to_stops[most_route]):
            most_route = route
        if len(routes_to_stops[route]) < len(routes_to_stops[least_route]):
            least_route = route

    print("Route with most stops: ", route_data[most_route]['attributes']['long_name'])
    print("Route with least stops: ", route_data[least_route]['attributes']['long_name'])



if __name__ == "__main__":
    test_url = "https://api-v3.mbta.com/routes?filter[type]=0,1"
    s = requests.Session()

    api_key = getenv("MBTA_KEY")
    if (api_key is not None):
        print("Api key found: ", api_key)
        s.headers.update({"x-api-key":
                      api_key})

    # This requests all the data before running anything to reduce the number of requests.
    all_routes = get_all_routes(s)
    all_stops = get_all_stops(all_routes.keys(),s)
    routes_to_stops = get_stops_per_route(all_routes, s)
    print("+++++++++")

    print(routes_to_stops)
    print("+++++++++")
    stops_to_routes = get_routes_per_stop(routes_to_stops)
    print(stops_to_routes)
    # routes_to_stops["test"] = ["test"]
    # print(routes_to_stops)
    # stops_to_routes = get_routes_per_stop(routes_to_stops)
    # print(all_stops)


    user_input = ""
    while user_input != "q\n":
        print("Welcome! Please make a selection:\n")
        print("To list off the long names of all subway routes, enter 1.")
        print("To list the routes with most and least stops and a list of stops that connect 2 or more routes, enter 2.")
        user_input = sys.stdin.readline()
        print(user_input)
        if user_input == "1\n":
            print_route_names(all_routes)
        if user_input == "2\n":
            print_stops_data(all_stops, all_routes, stops_to_routes, routes_to_stops)



    # r = s.get(test_url)

    # r.raise_for_status() or r.status_code to check for success
    # json = r.json()
    # print(json['data'])
    # print(json['data']['attributes'])

    