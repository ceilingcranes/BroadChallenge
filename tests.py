import unittest
import main

class TestMBTA(unittest.TestCase):

    def test_find_connections_one(self):
        """
        Test one connection
        """
        test_connections = {"R2":"R1"}
        end = "R2"

        returned_connections = main.find_connections(test_connections, end)
        self.assertListEqual(returned_connections, ["R1", "R2"])

    def test_find_connections_multiple(self):
        """
        Test multiple connections
        """
        test_connections = {"R2": "R1",
                            "R3": "R2"}
        end = "R3"
        returned_connections = main.find_connections(test_connections, end)
        self.assertListEqual(returned_connections, ["R1", "R2", "R3"])

    def test_get_routes_per_stop(self):
        test_routes = {"R1":["S1","S2"],
                       "R2": ["S2", "S3"],
                       "R3": ["S3"]}

        stops = main.get_routes_per_stop(test_routes)

        expected = {"S1": ["R1"],
                    "S2": ["R1", "R2"],
                    "S3": ["R2", "R3"]}

        self.assertDictEqual(stops, expected)

    def test_find_path_same(self):
        """
        Find the path if the start and end are the same
        """
        test_routes = {"R1":["S1"],
                       "R2":["S1"]}
        test_stops = main.get_routes_per_stop(test_routes)

        test_connect = main.find_path("S1", "S1", test_stops, test_routes)
        self.assertEqual(test_connect, [])

    def test_find_path_one(self):
        test_routes = {
            "R1":["S1", "S2"]
        }
        test_stops = main.get_routes_per_stop(test_routes)
        test_connect = main.find_path("S1", "S2", test_stops, test_routes)

        self.assertListEqual(test_connect, ["R1"])

    def test_find_path_multiple(self):
        test_routes = {
            "R1": ["S1", "S2"],
            "R2": ["S2", "S3"]
        }
        test_stops = main.get_routes_per_stop(test_routes)
        test_connect = main.find_path("S1", "S3", test_stops, test_routes)

        self.assertListEqual(test_connect, ["R1", "R2"])

    def test_find_path_complicated(self):
        test_routes = {
            "R1": ["S0", "S1", "S2", "S3"],
            "R2": ["S0", "S6", "S7", "S2", 'S5'],
            'R3': ['S10', 'S6', 'S7', 'S8', 'S9'],
            'R4': ['S10', 'S11', 'S12', 'S13'],
            'R5': ['S8', 'S14', 'S12'],
            'R6': ['S6', 'S11'],
            'R7': ['S13']
        }
        test_stops = main.get_routes_per_stop(test_routes)
        test_connect = main.find_path("S0", "S13", test_stops, test_routes)

        self.assertListEqual(test_connect, ["R2", "R3", "R4"])



if __name__ == "__main__":
    unittest.main()