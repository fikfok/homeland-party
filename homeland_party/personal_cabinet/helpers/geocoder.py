from functools import lru_cache

from dadata import Dadata
from homeland_party.const import DADATA_TOKEN


class Geocoder:
    WRONG_GEO_MSG = (
        'Нельзя определить адрес по данным координатам. '
        'Попробуйте, пожалуйста, выбрать координаты ближе к населённому пункту.'
    )

    def __init__(self):
        self.dadata = Dadata(DADATA_TOKEN)

    @lru_cache(maxsize=10000)
    def get_geo_data(self, geocode: str = None, latitude: float = None, longitude: float = None) -> dict:
        default_result = dict()
        lat = 0.0
        lon = 0.0
        if geocode:
            lon, lat = geocode.split(',')

        if latitude and longitude:
            lat = latitude
            lon = longitude

        raw_data = self.dadata.geolocate(name="address", lat=lat, lon=lon, radius_meters=1000)
        if raw_data:
            result = raw_data[0]['data']
        else:
            result = default_result
        return result
