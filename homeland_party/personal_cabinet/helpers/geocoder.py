from functools import lru_cache

from dadata import Dadata
from homeland_party.const import DADATA_TOKEN


class Geocoder:
    def __init__(self):
        self.dadata = Dadata(DADATA_TOKEN)

    @lru_cache(maxsize=10000)
    def get_geo_data(self, geocode: str) -> dict:
        default_result = dict()
        lon, lat = geocode.split(',')
        raw_data = self.dadata.geolocate(name="address", lat=lat, lon=lon, radius_meters=1000)
        if raw_data:
            result = raw_data[0]['data']
        else:
            result = default_result
        return result
