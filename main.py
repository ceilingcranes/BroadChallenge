import requests
from os import getenv
import sys

def get_all_lines(sess):
    """
    Return the decoded JSON object returned from requesting all rail lines. Takes in the Session object
    which is mostly used to track API key.
    """
    line_url = "https://api-v3.mbta.com/routes"

    # I use a filter before sending a request to reduce unneeded bandwidth and to keep the
    # runtime of analysis down by reducing the time needed for that check.
    parameters = {"filter[type]":"0,1"} # Filter by rail only routes

    ret = sess.get(line_url, params = parameters)
    return ret.json()

def print_line_names(line_json):
    """
    Given the JSON for Routes, print out the long names of all of them.
    :param line_json: Decoded JSON returned from routes request
    """
    print("===Long names for Lines===")
    for route_data in line_json['data']:
        print(route_data['attributes']['long_name'], "\n")
    print("===End of Print===")

def print_line_ids(line_json):
    print("===IDs for Lines===")
    for route_data in line_json['data']:
        print(route_data['id'], "\n")
    print("===End of Print===")

if __name__ == "__main__":
    test_url = "https://api-v3.mbta.com/routes?filter[type]=0,1"
    s = requests.Session()

    api_key = getenv("MBTA_KEY")
    if (api_key is not None):
        print("Api key found: ", api_key)
        s.headers.update({"x-api-key":
                      api_key})

    print_line_names(get_all_lines(s))
    print_line_ids(get_all_lines(s))

    user_input = ""
    while user_input != "q\n":
        print("Welcome! Please make a selection:\n")
        print("To list off the long names of all subway lines, enter 1.")

        user_input = sys.stdin.readline()
        print(user_input)
        if user_input == "1\n   ":
            print_line_names(get_all_lines(s))
    # r = s.get(test_url)

    # r.raise_for_status() or r.status_code to check for success
    # json = r.json()
    # print(json['data'])
    # print(json['data']['attributes'])

    