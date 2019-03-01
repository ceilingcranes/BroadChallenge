"""
Methods to query and output data from the Boston transportation system.
"""

import requests
from os import getenv
import sys


def get_all_routes(sess):
    """
    Get data of all rail routes. Takes in the Session object, which is mostly used to track API key. Returns a
    dictionary mapping route IDs -> Route JSON.

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
    parameters = {"filter[type]": "0,1"}  # Filter by rail only routes

    ret = sess.get(route_url, params=parameters)
    return format_data(ret.json())


def print_route_names(route_data):
    """
    Given formatted Route data, print out all the long names.
    :param route_data: A dictionary of route IDS mapped to JSON returned from routes request
    """
    print("===Long names for routes===")
    for route_id in route_data.keys():
        print(route_data[route_id]['attributes']['long_name'], "\n")
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
    :return: Dictionary mapping stop ID to stop JSON data for all stops serviced by the routes in route_ids
    """
    stops_url = "https://api-v3.mbta.com/stops"
    route_id_string = ",".join(route_ids)  # Convert list to comma separated string for API call

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

    :param data_json: JSON object containing an "id" parameter for mapping
    :return: Dictionary mapping ids to json values.
    """
    data_dict = dict()
    for vals in data_json['data']:
        data_dict[vals['id']] = vals

    return data_dict


def get_routes_per_stop(routes_to_stops):
    """
    Given a dict matching Route IDS to Stop IDs, return a dictionary which maps Stop IDs to Route IDs.
    :param routes_to_stops: Dictionary that maps Route ID -> List of stop IDs.
    :return Dictionary that maps Stop ID -> List of route ID
    """
    stops_to_routes = dict()
    for route in routes_to_stops.keys():
        for stop in routes_to_stops[route]:
            if stop in stops_to_routes:
                stops_to_routes[stop].append(route)
            else:
                stops_to_routes[stop] = [route]

    return stops_to_routes


def print_stops_data(stops_data, route_data, stops_to_routes, routes_to_stops):
    """
    Print out the route with the most stops, the route with the least, and all the stops that connect 2 or more routes.
    :param stops_data: Dictionary with stop IDs matched with stops JSON data, which includes the long name.
    :param route_data: Dictionary with route IDs matched with route JSON data, which includes the long name.
    :param stops_to_routes: Dictionary mapping stop IDs to lists of Route IDs that service the stop.
    :param routes_to_stops: Dictionary mapping route IDs to lists of stops that the route stops on.
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
    print("")
    print("====Stops that connect 2 or more Routes====")
    # To print out all stops that connect 2 or more routes
    for stop in stops_to_routes.keys():
        if len(stops_to_routes[stop]) > 1:
            # Fancy way to access the long names for all the routes within stops_to_routes[stop]
            print("{}: {}".format(stops_data[stop]['attributes']['name'],
                ", ".join([route_data[route_id]['attributes']['long_name'] for route_id in stops_to_routes[stop]])))
    print("====End of Print====")


def find_path(start_stop, end_stop, stop_to_routes, route_to_stops):
    """
    Find the path of routes between start_stop and end_stop. Uses modified Dijkstra's algorithm to find path, and calls
    find_connections to convert result into an ordered list of routes.

    Example:
    If the path would need to take the Red line, then the Green Line, then the Blue Line, the return would be as follows:
    [red_line_id, green_line_id, blue_line_id]

    :param start_stop: Stop ID to start.
    :param end_stop: Stop ID to end.
    :param stop_to_routes: Dictionary mapping stop IDs to route IDs that stop there.
    :param route_to_stops: Dictionary mapping route IDs to stop IDs that the route services.
    :return: List of route IDs corresponding to the correct order of stops.
    """
    if start_stop == end_stop:
        return []

    queue = stop_to_routes[start_stop][:]  # End colon to copy instead of pass by reference
    end_routes = stop_to_routes[end_stop]  # All the routes that connect to the end stop

    # Checked routes maintains a list of routes that are already in the queue to keep from infinite loops
    checked_routes = stop_to_routes[start_stop][:]

    # Route connections keeps track of where the routes came on from - so basically, if the step entails switching
    # from route 1 to route 2, this dict will store Route2ID : Route1ID so you can trace backwards and get the full trip.
    route_connections = dict()

    while len(queue) > 0:
        check_route = queue.pop(0)
        if check_route in end_routes:
            # The route connects to the end stop, so end here and return the end list.
            return find_connections(route_connections, check_route)

        possible_stops = route_to_stops[check_route]
        for stop in possible_stops:
            for route in stop_to_routes[stop]:
                if route not in checked_routes:
                    queue.append(route)
                    checked_routes.append(route)
                    route_connections[route] = check_route


def find_connections(route_connections, end_route):
    """
    Convert a dictionary of route connections to a list of the correct order of connections
    :param route_connections: Dictionary mapping transfers, so if the move is to switch from Route1 to Route2, the
    dictionary entry would be {Route2: Route1}
    :param end_route: The end route, which indicates the direction of the trace back through different route changes.
    :return: List of route IDs in the correct order, as designated by the dictionary.
    """
    connections = [end_route]
    prev_r = end_route
    while prev_r in route_connections:
        prev_r = route_connections[prev_r]
        connections = [prev_r] + connections

    return connections


def find_stop_by_name(stop_data, stop_name):
    """
    Find the stop that has the name stop_name and return the ID. If there is no identical match, a list of stop names
    that contain stop_name is returned instead.
    :param stop_data: A dictionary mapping stop ID to stop JSON data
    :param stop_name: String of the stop name to search for
    :return: Either the stop ID matching stop_name or a list of possible names if there isn't a perfect match.
    """

    possible = []
    for stop_id in stop_data.keys():
        test_name = stop_data[stop_id]['attributes']['name']
        if stop_name.lower() == test_name.lower():
            return stop_id

        if stop_name.lower() in test_name.lower():
            possible.append(test_name)

    return possible


if __name__ == "__main__":
    test_url = "https://api-v3.mbta.com/routes?filter[type]=0,1"
    s = requests.Session()

    # Store API key as an environment variable named "MBTA_KEY". If there is no env variable, no API key will be used.
    api_key = getenv("MBTA_KEY")

    if api_key is not None:
        s.headers.update({"x-api-key": api_key})

    # This requests all the data before running anything to reduce the number of requests.
    all_routes = get_all_routes(s)
    all_stops = get_all_stops(all_routes.keys(),s)
    routes_to_stops = get_stops_per_route(all_routes, s)
    stops_to_routes = get_routes_per_stop(routes_to_stops)

    user_input = ""
    while user_input != "q\n":
        print("\n=================================")
        print("Welcome! Please make a selection:\n")
        print("To list off the long names of all subway routes, enter 1.")
        print("To list the routes with most and least stops and a list of stops that connect 2 or more routes, enter 2.")
        print("To find the routes connecting two stops, enter 3.")
        print("For help, enter help or h.")
        print("To end the program, enter q.")
        print("=================================")
        user_input = sys.stdin.readline().lower()
        print("")
        if user_input == "1\n":
            print_route_names(all_routes)
        if user_input == "2\n":
            print_stops_data(all_stops, all_routes, stops_to_routes, routes_to_stops)
        if user_input == "3\n":
            stop1_id = []
            while not isinstance(stop1_id, str):
                print("Enter the name of the first stop")
                stop1 = sys.stdin.readline()[:-1]
                stop1_id = find_stop_by_name(all_stops, stop1)
                if not isinstance(stop1_id, str):
                    print("ERROR: Name \"{}\" not allowed. Please enter the full name of the first stop.".format(stop1))
                    if len(stop1_id) > 0:
                        print("Suggested possibilities for names:")
                        print("\n".join(stop1_id))

            stop2_id = []
            while not isinstance(stop2_id, str):
                print("Enter the name of the second stop")
                stop2 = sys.stdin.readline()[:-1]
                stop2_id = find_stop_by_name(all_stops, stop2)
                if not isinstance(stop2_id, str):
                    print("ERROR: Name \"{}\" not allowed. Please enter the full name of the first stop.".format(stop2))
                    if len(stop2_id) > 0:
                        print("Suggested possibilities for names:")
                        print("\n".join(stop2_id))

            routes_between_stops = find_path(stop1_id, stop2_id, stops_to_routes, routes_to_stops)
            print("===Path from {} to {}=== ".format(all_stops[stop1_id]['attributes']['name'],
                                                     all_stops[stop2_id]['attributes']['name']))

            # If the two stops are the same or if there is no route found between them.
            if len(routes_between_stops) == 0:
                print("No path found.")
            else:
                print(" -> ".join(routes_between_stops))

        if user_input == "h\n" or user_input == "help\n":
            print("[Option 1] Print the full names for all rail routes. This includes Light Rail and Heavy Rail routes.")
            print("[Option 2] Print the full names of the rail route with the most stops, the least stops, and print ",
                  "any stops that have more than two routes servicing them. This will print off the name of the stop ",
                  "followed by a comma separated list of lines that service that stop.")
            print("[Option 3] This option takes in two stops and will return the routes that one would take to go from "
                  "one stop to the next. This will ask for user input for the stop names, but if no stop of the entered"
                  " name is found, it will print out any stops that contain the input. So, if you're uncertain of the "
                  "name of a route, you can search.")
