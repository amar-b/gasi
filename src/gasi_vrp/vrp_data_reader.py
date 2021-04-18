import sys
import random
import math
import csv
from typing import Tuple, List
from functools import reduce
from itertools import permutations
import xml.etree.ElementTree as ET

from location import Location

def _read_vehicle_capacity(root_node: ET.Element) -> float:
    return float(root_node.find('./fleet/vehicle_profile/capacity').text)

def _read_location_id(network_node: ET.Element) -> int:
    return int(network_node.attrib['id'])-1 # subtract 1 to create a zero based index

def _read_location_coords(network_node: ET.Element) -> Tuple[float, float]:
    x = float(network_node.find('./cx').text)
    y = float(network_node.find('./cy').text)

    return (x, y)

def _read_location_capacity(node_id: int, root_node: ET.Element) -> float:
    return float(root_node.find(f"./requests/request[@node='{node_id+1}']/quantity").text)

def _get_depot_loc(root_node: ET.Element) -> Location:
    net_node = root_node.find("./network/nodes/node[@type='0']")

    return Location(_read_location_id(net_node), _read_location_coords(net_node), 0, True)

def _get_destination_locs(root_node: ET.Element) -> List[Location]:
    dest_locs = []

    for network_node in root_node.findall("./network/nodes/node[@type='1']"):
        node_id = _read_location_id(network_node)
        dest_locs.append(Location(
            node_id, 
            _read_location_coords(network_node),
            _read_location_capacity(node_id, root_node),
            False))

    return dest_locs

def read_file(location_data_path: str) -> Tuple[int, List[Location]]:
    root = ET.parse(location_data_path).getroot()
    all_locs = []

    #Parse vehicle capacity
    capacity = _read_vehicle_capacity(root)

    # Parse depot and destination locs and sort by id
    non_depot_locs = all_locs.extend(_get_destination_locs(root))
    depot = all_locs.append(_get_depot_loc(root))

    return (capacity, all_locs)