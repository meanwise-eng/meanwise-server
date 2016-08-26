import json
import requests

from django.conf import settings
from django.http.request import QueryDict

from common.utils import slugify
from .models import City, Location

def get_places(q, types, lat_lon):

    query_data = {}
    if lat_lon:
        lat_lon = ['%.3f' % x for x in lat_lon]
        query_data['location'] = ','.join(lat_lon)
        query_data['radius'] = 1000000 # 1000Kms
    query_data['key'] = settings.GOOGLE_LOCATION_API_KEY
    query_data['input'] = q
    query_data['types'] = types
    query = QueryDict('', mutable=True)
    query.update(query_data)
    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json?" + query.urlencode()
    response = requests.get(url)
    content = json.loads(response.content)
    if not content['status'] == 'OK':
        return []
    predictions = content['predictions']
    return predictions

def get_cities(q, lat_lon):
    predictions = get_places(q, '(cities)', lat_lon)
    cities = []
    for prediction in predictions:
        data = {}
        place_id = prediction['place_id']
        data['description'] = prediction['description']
        try:
            data['city'] = prediction['terms'][0]['value']
            data['country'] = prediction['terms'][-1]['value']
            data['area'] = ','.join([x['value'] for x in  prediction['terms'][1:-1]])
        except Exception as e:
            print (e)
        else:
            data['slug'] = slugify(data['description'])
            city, created = City.objects.get_or_create(place_id=place_id, defaults = data)
            cities.append(city)
    return cities


def get_locations(q, lat_lon):
    predictions = get_places(q, 'establishment', lat_lon)
    locations = []
    for prediction in predictions:
        data = {}
        place_id = prediction['place_id']
        data['description'] = prediction['description']
        try:
            data['name'] = prediction['terms'][0]['value']
            data['country'] = prediction['terms'][-1]['value']
            data['area'] = ','.join([x['value'] for x in  prediction['terms'][1:-1]])
        except Exception as e:
            print (e)
        else:
            data['slug'] = slugify(data['description'])
            location, created = Location.objects.get_or_create(place_id=place_id, defaults = data)
            locations.append(location)
    return locations

