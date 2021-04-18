from typing import Tuple, List

class Location:
    def __init__(self
        , identifier: int
        , coords: Tuple[int, int]
        , size: int
        , is_depot: bool):

        self.id = identifier
        self.coords = coords
        self.request_size = size
        self.is_depot = is_depot

    def __str__(self):
        return f"ID={self.id} | SIZE={self.request_size} | COORDS={self.coords} | IS_DEPOT={self.is_depot}"