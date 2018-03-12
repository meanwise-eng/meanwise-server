import logging
import feedparser
import requests
import json
import uuid
import asyncio
from time import sleep
from typing import List, Type
from functools import wraps

logger = logging.getLogger('meanwise_backend.%s' % __name__)


class Event():

    def __init__(self, id, type, data={}, metadata=None):
        self.id = id
        self.type = type
        self.data = data
        self.metadata = metadata


def event_from_dict(event_dict, create_event_class):
    logger.info(event_dict)
    e = create_event_class(event_dict)(event_dict['eventId'], event_dict['eventType'], event_dict['data'])
    return e


def event_converter(events: List[Event], create_event_class):
    for event in events:
        yield event_from_dict(event, create_event_class)


class EventEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


class EventStoreClient():

    url = 'http://eventstore:2113'

    @classmethod
    def get_default_instance(cls):
        return EventStoreClient()

    def _request(self, path, headers):
        if not headers:
            headers = self._get_headers()
        r = requests.get(path, headers=headers)
        if r.status_code < 200 or r.status_code > 300:
            raise EventStoreClient.Exception("Error returned by server")

        return r

    def add_event(self, event, stream):
        headers = self._get_headers()
        url = '{}/streams/{}/'.format(self.url, stream)
        data = event
        events = [{'eventId': event.id, 'eventType': event.type, data: data}]
        headers = self._get_headers()
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/vnd.eventstore.events+json'
        response = requests.post(url, data=events, headers=headers)

        status_code = response.status_code
        if status_code >= 500:
            raise Exception("Unable to save event due to error on server")
        if status_code >= 400:
            raise Exception("Error sending data to server")

    def save(self, events: List[Event], stream) -> None:
        headers = self._get_headers()
        url = '{}/streams/{}/'.format(self.url, stream)

        logger.info(events)
        prepped_events = []
        for event in events:
            prepped_events.append({
                'eventId': uuid.uuid4(),
                'eventType': event.type,
                'data': event.data,
                'metadata': {
                    'aggregateId': event.id
                }
            })

        headers = self._get_headers()
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/vnd.eventstore.events+json'
        headers['ES-ExpectedVersion'] = '-2'
        response = requests.post(
            url,
            data=json.dumps(prepped_events, cls=EventEncoder),
            headers=headers
        )

        status_code = response.status_code
        response.raise_for_status()
        if status_code >= 500:
            raise Exception("Unable to save event due to error on server")
        if status_code >= 400:
            raise Exception("Error sending data to server")

        logger.info("Events saved succesfully")

    def _get_headers(self):
        return {'Authorization': 'Basic YWRtaW46Y2hhbmdlaXQ='}
    
    def _get_feed(self, feed_url):
        headers = self._get_headers()
        return feedparser.parse(feed_url, request_headers=headers)

    def get_all_events(self, stream):
        last_url = '%s/streams/%s/0/forward/20' % (self.url, stream)
        d = self._get_feed(last_url)

        for entry in d.entries:
            yield from self._get_entry(entry)

        if 'links' in d.feed:
            for link in d.feed.links:
                if link.rel == 'previous':
                    yield from self._get_previous(link.href, False)

    def get_new_events(self, stream, wait=True):
        last_url = '%s/streams/%s/0/forward/20' % (self.url, stream)
        d = self._get_feed(last_url)

        for entry in d.entries:
            yield from self._get_entry(entry)

        if 'links' in d.feed:
            for link in d.feed.links:
                if link.rel == 'previous':
                    yield from self._get_previous(link.href, wait)

    def _get_previous(self, href, wait=True):
        d = self._get_feed(href)

        for entry in d.entries:
            yield from self._get_entry(entry)

        for link in d.feed.links:
            if link.rel == 'previous':
                yield from self._get_previous(link.href)

        if wait:
            print("Waiting a second to check again")
            sleep(1)
            yield from self._get_previous(href, wait)

    def _get_entry(self, entry):
        headers = self._get_headers()
        headers['Accept'] = 'application/vnd.eventstore.event+json'
        res = self._request(entry.link, headers=headers)
        content = json.loads(res.content.decode('UTF-8'))

        yield content

    class Exception(Exception):
        pass


class EventSourced():

    def __init__(self):
        self._uncommitted_events = []
        self._aggregate_version = 0

    def _apply(self, event: Event):
        handler = getattr(self, '_apply_%s' % event.__class__.__name__)
        handler(event)
        
        self._uncommitted_events.append(event)

    def get_uncommitted_events(self):
        return self._uncommitted_events

    def _inject_events(self, events: List[Event]):
        for event in events:
            self._apply(event)
            self._aggregate_version += 1
        self._uncommitted_events = []


def handle_event(eventType: Type[Event], category: str):
    def real_decorator(fn):
        eventbus = EventBus.get_default_instance()
        eventbus.add_eventhandler(eventType.__name__, category, fn)
        print("%s registered as eventhandler for %s" % (fn.__name__, eventType.__name__))
        @wraps(fn)
        def wrapper(*args, **kwargs):
            fn(*args, **kwargs)
        return wrapper
    return real_decorator
        

eventstore = EventStoreClient.get_default_instance()

class EventBus():

    def __init__(self):
        self.eventhandlers = {}

    singleton = None

    @classmethod
    def get_default_instance(cls):
        if EventBus.singleton is None:
            EventBus.singleton = EventBus()
        return EventBus.singleton

    def add_eventhandler(self, eventName, category, handler):
        key = '%s' % (category,)
        if key not in self.eventhandlers:
            self.eventhandlers[key] = []
        self.eventhandlers[key].append({'eventName': eventName, 'handler': handler})

    async def run(self, loop):
        while True:
            print("Getting events")
            await self.get_events()
            await asyncio.sleep(1)

    async def get_events(self):
        print(self.eventhandlers)
        for category, handlers in self.eventhandlers.items():
            print("Getting events for %s" % category)
            stream = '$ce-%s' % category
            for event in eventstore.get_new_events(stream, wait=False):
                print("Handling event %s: %s" % (event['eventType'], event['eventId']))
                for handler in handlers:
                    if handler['eventName'] == event['eventType']:
                        handler['handler'](event)
                        print("Event handled successfully")
