from django.contrib.gis.geoip2 import GeoIP2
from geoip2.errors import AddressNotFoundError


def get_lat_lon(ip):
    try:
        return GeoIP2().lat_lon(ip)
    except AddressNotFoundError as e:
        return None
