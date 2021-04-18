import sys
import random
import math
import csv

from typing import Tuple, List
from functools import reduce
from itertools import permutations

from location import Location
from utils import euclidean_distance

class VRP:
    def __init__(self, vehicle_capacity: float, locs: List[Location]):
        sorted_locs = sorted(locs, key=lambda l: l.id)

        self.locs_dictionary = {l.id: l for l in sorted_locs}
        self.depot_id = next(l for l in sorted_locs if l.is_depot).id
        self.max_vehicle_capacity =  vehicle_capacity
        self.distance = self._get_distance_matrix(sorted_locs)

    def __str__(self) -> str:
        return f"VEHiCLE CAPACITY={self.max_vehicle_capacity}\n\nLOCATIONS:\n" + '\n'.join(str(l) for l in self.locs_dictionary.values())

    def _get_distance_matrix(self, sorted_locs: List[Location]) -> List[List[float]]:
        n = len(sorted_locs)
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                matrix[i][j] = euclidean_distance(sorted_locs[i], sorted_locs[j])
        return matrix

    def location_count(self):
        """ returns the number of locations (including depot)"""
        return len(self.distance)

    def decode_routes(self, encoded_routes):
        veh_route = [self.depot_id]   # current route, intialized with depot
        veh_capacity = 0              

        for loc in encoded_routes:
            loc_size = self.locs_dictionary[loc].request_size
            
            if veh_capacity + loc_size <= self.max_vehicle_capacity:
                veh_route.append(loc)
                veh_capacity += loc_size

            else:
                veh_route.append(self.depot_id)
                yield veh_route

                veh_route = [self.depot_id, loc]
                veh_capacity = loc_size
        
        if len(veh_route) > 0:
            veh_route.append(self.depot_id)
            yield veh_route

    def total_distance(self, encoded_routes):
        total_distance = 0
        for route in self.decode_routes(encoded_routes):
            route_distance = 0
            for j in range(1, len(route)):
                route_distance += self.distance[route[j-1]][route[j]]
            total_distance += route_distance
        return total_distance