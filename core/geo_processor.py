import math
from core import Geolocation
from typing import List, Optional
from geopy.geocoders import Nominatim

class GeoProcessor:
    def __init__(self):
        self.earth_raidus = 6371.0
        self.geolocator = Nominatim(user_agent="geoapi")

    def get_country_code(self, location: Geolocation) -> Optional[str]:
        try:
            geopoint = self.geolocator.reverse(location.to_tuple(), language="en")
            country_code = geopoint.raw["address"]["country_code"]
            return country_code
        except:
            return None

    def get_haversine_distance(self, location1: Geolocation, location2: Geolocation) -> float:
        lat1, lon1 = math.radians(location1.latitude), math.radians(location1.longitude)
        lat2, lon2 = math.radians(location2.latitude), math.radians(location2.longitude)

        lat_diff = lat2 - lat1
        lon_diff = lon2 - lon1

        a = math.sin(lat_diff / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(lon_diff / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        haversine_distance = self.earth_raidus * c

        return haversine_distance
    
    def aggregate_geolocations(self, geolocations: List[Geolocation], locations_to_consider: int = 2) -> Geolocation:
        locs_count = len(geolocations)

        if locs_count == 0: raise Exception("No geolocations provided.")
        if locs_count == 1: return geolocations[0]
        if locs_count < locations_to_consider:
            raise Exception(f"{locs_count} geolocations provided but at least {locations_to_consider} required for aggregation.")
        if locations_to_consider < 2: raise Exception("Aggregation requires at least 2 locations to be considered.")

        locs = geolocations.copy()

        while len(locs) > locations_to_consider:
            max_total_dist = -1
            index_to_remove = -1

            for i, loc in enumerate(locs):
                others = locs[:i] + locs[i+1:]
                total_dist = sum(self.get_haversine_distance(loc, other) for other in others)
                if total_dist > max_total_dist:
                    max_total_dist = total_dist
                    index_to_remove = i

            del locs[index_to_remove]

        lat = sum([c.latitude for c in locs]) / len(locs)
        lng = sum([c.longitude for c in locs]) / len(locs)
        return Geolocation(lat, lng)