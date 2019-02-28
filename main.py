import requests
from os import getenv
import sys

def get_all_routes(sess):
    """
    Return the decoded JSON object returned from requesting all rail routes. Takes in the Session object
    which is mostly used to track API key.
    """
    route_url = "https://api-v3.mbta.com/routes"

    # I use a filter before sending a request to reduce unneeded bandwidth and to keep the
    # runtime of analysis down by reducing the time needed for that check.
    parameters = {"filter[type]":"0,1"} # Filter by rail only routes

    ret = sess.get(route_url, params = parameters)
    return ret.json()

def print_route_names(route_json):
    """
    Given the JSON for Routes, print out the long names of all of them.
    :param route_json: Decoded JSON returned from routes request
    """
    print("===Long names for routes===")
    for route_data in route_json['data']:
        print(route_data['attributes']['long_name'], "\n")
    print("===End of Print===")

def print_route_ids(route_json):
    print("===IDs for routes===")
    for route_data in route_json['data']:
        print(route_data['id'], "\n")
    print("===End of Print===")

def get_all_stops(route_ids, session):
    """
    Return a list of stop JSON data that is serviced by any routes within a list of route_ids.
    :param route_ids:
    :param session:
    :return:
    """
    stops_url = "https://api-v3.mbta.com/stops"
    route_id_string = ",".join(route_ids) # Convert list to comma separated string for API call
    params = {"filter[route]": route_id_string}

    stop_ret = session.get(stops_url, params=params)
    return stop_ret.json()

def get_stops_per_routes(route_json, session):
    """
    Return a dictionary that contains the route ID followed by a list of stop IDs serviced by that route.
    :param route_json:
    """
    stop_data = dict()
    for route_data in route_json['data']:
        route_id = route_data['id']
        stops_json = get_stops(route_id, session)

        stop_data[route_id] = [stop_data["id"] for stop_data in stops_json["data"]]

    return stop_data


def get_stops(route_id, session):
    """
    Given the route ID or multiple route IDs in one string divided by commas (like "id1,id2")
     and the requests Session object, make a request to get the JSON for all stops that
    service that route and return the results.
    :param route_id: R
    :param session:
    :return:
    """
    stops_url = "https://api-v3.mbta.com/stops"
    params = {"filter[route]": route_id}
    ret = session.get(stops_url, params=params)
    return ret.json()


def find_multiple_stops(routes_to_stops):
    """
    Given a dict matching Route IDS to Stop IDs, return a dictionary which maps Stop IDs to Route IDs.
    """
    stops_to_routes = dict()
    for route in routes_to_stops.keys():
        # TODO finish
        if route in stops_to_routes:
            stops_to_routes[route].append()


def get_routes(stop_id, session):
    """
    Given the stop ID or multiple stop IDs seperated by commas, return all the routes that service that stop in JSON
    format.
    :param stop_id:
    :param session:
    :return:
    """

def print_stops_data(stops_data_json, route_data_json):
    """
    Given a dictionary that maps route IDs to JSON of stops data and a list of route data JSON values,
    print out the route with the most stops, the route with the least, and all the stops that connect 2 or more routes.
    :param stops_data_json:
    :param route_data_json:
    :return:
    """



if __name__ == "__main__":
    # TODO: Either save data or make all requests early to avoid having to make an API call every time.
    test_url = "https://api-v3.mbta.com/routes?filter[type]=0,1"
    s = requests.Session()

    api_key = getenv("MBTA_KEY")
    if (api_key is not None):
        print("Api key found: ", api_key)
        s.headers.update({"x-api-key":
                      api_key})

    # print_route_names(get_all_routes(s))
    # print_route_ids(get_all_routes(s))
    all_routes = get_all_routes(s)
    routes_to_stops = get_stops_per_routes(all_routes, s)

    print(routes_to_stops)

    user_input = ""
    while user_input != "q\n":
        print("Welcome! Please make a selection:\n")
        print("To list off the long names of all subway routes, enter 1.")
        print("To list the routes with most and least stops and a list of stops that connect 2 or more routes, enter 2.")
        user_input = sys.stdin.readline()
        print(user_input)
        if user_input == "1\n":
            print_route_names(get_all_routes(s))
        # if user_input == "2\n":




    # r = s.get(test_url)

    # r.raise_for_status() or r.status_code to check for success
    # json = r.json()
    # print(json['data'])
    # print(json['data']['attributes'])

    