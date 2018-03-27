import logging
import feedparser
import requests
import json
import uuid
import asyncio
import datetime
from time import sleep
from typing import List, Type, Dict
from functools import wraps

logger = logging.getLogger('meanwise_backend.%s' % __name__)


class Event():

    def __init__(self, id, data:Dict={}, metadata:Dict={}):
        self.id = id
        self.type = self.__class__.__name__
        self.data = data
        self.metadata = metadata
        self.metadata['timestamp'] = datetime.datetime.now()
        self.event_number = None

    @classmethod
    def load(cls, data):
        event = Event(data['metadata']['aggregateId'], data['data'], data['metadata'])
        event.type = data['eventType']
        return event


def event_from_dict(event_dict, create_event_class):
    logger.info("Event: %s", event_dict['eventType'])
    e = create_event_class(event_dict)(event_dict['eventId'], event_dict['eventType'], event_dict['data'])
    return e


def event_converter(events: List[Event], create_event_class):
    events_converted = []
    for event in events:
        print("Events")
        print(events)
        print(event)
        events_converted.append(event_from_dict(event, create_event_class))


class Storage():

    def __init__(self):
        self.data = {}

    def get(self, key):
        if key in self.data:
           return self.data[key]

    def set(self, key, value):
        self.data[key] = value


class EventStoreClient():

    url = 'http://eventstore:2113'

    def __init__(self, storage):
        self.storage = storage

    @classmethod
    def get_default_instance(cls):
        storage = Storage()
        return EventStoreClient(storage=storage)

    class EventEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.datetime):
                return str(obj)

            if isinstance(obj, uuid.UUID):
                return str(obj)
            return json.JSONEncoder.default(self, obj)

    def _request(self, path, headers):
        if not headers:
            headers = self._get_headers()
        r = requests.get(path, headers=headers)
        if r.status_code < 200 or r.status_code > 300:
            raise EventStoreClient.EventStoreException("Error returned by server")

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

    def save(self, events: List[Event], stream, aggregate_version) -> None:
        headers = self._get_headers()
        url = '{}/streams/{}/'.format(self.url, stream)

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
        expected_version = aggregate_version - 1
        if expected_version == 0:
            expected_version = -2
        headers['ES-ExpectedVersion'] = '%d' % (expected_version,)

        response = requests.post(
            url,
            data=json.dumps(prepped_events, cls=EventStoreClient.EventEncoder),
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
                    yield from self._get_previous(link.href, wait=False, store_state=False)

    def get_new_events(self, stream, wait=True):
        storage_key = 'previous-link-%s' % stream
        previous_link = self.storage.get(storage_key)
        if previous_link:
            print("Found previous link: %s" % previous_link)
            yield from self._get_previous(previous_link, wait, store_state=True,
                                          storage_key=storage_key)
            return

        last_url = '%s/streams/%s/0/forward/20' % (self.url, stream)
        d = self._get_feed(last_url)

        for entry in d.entries:
            yield from self._get_entry(entry)

        if 'links' in d.feed:
            for link in d.feed.links:
                if link.rel == 'previous':
                    self.storage.set(storage_key, link.href)
                    print("Saved %s: %s" % (storage_key, link.href))
                    yield from self._get_previous(link.href, wait, storage_key=storage_key)
    def _check_subscription(self, url):
        r = requests.get(url + '/info')
        if r.status_code == 404:
            self._create_subscription(url)
        else:
            r.raise_for_status()

    def _create_subscription(self, url):
        headers = self._get_headers()
        headers['Content-Type'] = 'application/json'
        data = {
            'extraStatistics': True,
            'checkpointAfterMilliseconds': 5000,
            'maxCheckPointCount': 100,
            'maxRetryCount': 3,
            'maxSubscriberCount': 3,
            'messageTimeoutMilliseconds': 10000,
            'minCheckPointCount': 5,
        }
        r = requests.put(url, data=json.dumps(data, cls=EventStoreClient.EventEncoder), headers=headers)
        r.raise_for_status()

    def _get_previous(self, href, wait=True, store_state=True, storage_key=''):
        d = self._get_feed(href)

        print("Getting event details")
        for entry in d.entries:
            yield from self._get_entry(entry)

        if 'links' in d.feed:
            for link in d.feed.links:
                if link.rel == 'previous':
                    if store_state:
                        self.storage.set(storage_key, link.href)
                        print("Saved %s: %s" % (storage_key, link.href))
                    yield from self._get_previous(link.href, wait, store_state,
                                                  storage_key=storage_key)
                    return
            print("previous link not in links for %s" % href)
        print("No links for %s" % href)

        if wait:
            print("Waiting a second to check again")
            sleep(1)
            yield from self._get_previous(href, wait)

    def _get_entry(self, entry):
        headers = self._get_headers()
        headers['Accept'] = 'application/vnd.eventstore.event+json'
        res = self._request(entry.id, headers=headers)
        content = json.loads(res.content.decode('UTF-8'))

        yield content

    def subscribe_to_stream(self, stream, wait=True):
        subscription = 'mw-eventhandler'
        url = '%s/subscriptions/%s/%s' % (self.url, stream, subscription)

        self._check_subscription(url)

        headers = self._get_headers()
        headers['Accept'] = 'application/vnd.eventstore.competingatom+xml'
        
        read_url = url + '/1?embed=body'
        d = feedparser.parse(read_url, request_headers=headers)

        if 'entries' not in d:
            raise Excpetion("No entries in subscription")

        for entry in d.entries:
            yield self._create_job(entry)

    def _create_job(self, entry):
        event = next(self._get_entry(entry))
        job = self.Job(entry, event, self)

        return job
    class Job():
        def __init__(self, entry, event, eventstore):
            self.entry = entry
            self.event = event
            self.eventstore = eventstore
        def get_event(self):
            return self.event
        def acknowledge(self):
            ack_url = self._get_url('ack')
            
            headers = self.eventstore._get_headers()
            r = requests.post(ack_url, headers=headers)
            r.raise_for_status()
            
        def not_acknowledge(self, action):
            nack_url = self._get_url('nack')
            nack_url += '?action=' + action
            
            headers = self.eventstore._get_headers()
            r = requests.post(nack_url, headers=headers)
            r.raise_for_status()

        def _get_url(self, rel):
            for link in self.entry.links:
                if link.rel == rel:
                    return link.href


    class EventStoreException(Exception):
        pass


class PartialEventSourced():

    def __init__(self):
        self._uncommitted_events = []
        self._aggregate_version = 0

    def _apply(self, event: Event):
        handler = getattr(self, '_apply_%s' % event.type)
        handler(event)
        
        self._uncommitted_events.append(event)
        self._aggregate_version += 1

    def get_uncommitted_events(self):
        return self._uncommitted_events

    def clear_uncommitted_events(self):
        self._uncommitted_events = []

    def _inject_events(self, events: List[Event]):
        if events is None:
            return
        for event in events:
            self._apply(event)
            self._aggregate_version += 1
        self._uncommitted_events = []


class EventSourced(PartialEventSourced):

    def __init__(self, id, events: List[Event], state=None, keep_events=True):
        super().__init__()
        self.id = id
        if state is not None:
            self._set_state(state)

        for event in events:
            self._apply(event)

        if not keep_events:
            self.clear_uncommitted_events()

    def _set_state(self, state):
        for key, value in state.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def _get_state(self):
        state = vars(self)
        return state

    def _new(self, events: List[Event]):
        return self.__class__(self.id, events, self._get_state())


def handle_event(eventType: Type[Event], category: str):
    def real_decorator(fn):
        eventbus = EventBus.get_default_instance()
        eventbus.add_eventhandler(eventType, category, fn)
        logger.info("%s registered as eventhandler for %s" % (fn.__name__, eventType.__name__))
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

    def add_eventhandler(self, eventType, category, handler):
        key = '%s' % (category,)
        if key not in self.eventhandlers:
            self.eventhandlers[key] = []
        self.eventhandlers[key].append({
            'eventName': eventType.__name__,
            'handler': handler,
            'class': eventType
        })

    async def run(self, loop):
        while True:
            logger.info("Getting events")
            events_processed = await self.get_events()
            if not events_processed:
                await asyncio.sleep(3)

    async def get_events(self):
        events_processed = False
        for category, handlers in self.eventhandlers.items():
            logger.info("Getting events for %s" % category)
            stream = '$ce-%s' % category
            for job in eventstore.subscribe_to_stream(stream, wait=False):
                events_processed = True
                event = job.get_event()
                logger.info("Handling event %s: %s" % (event['eventType'], event['eventId']))
                for handler in handlers:
                    if handler['eventName'] == event['eventType']:
                        event_obj = handler['class'](
                            event['metadata']['aggregateId'],
                            event['data'],
                            event['metadata']
                        )
                        event_obj.event_number = event['eventNumber']
                        logger.info("Running handler %s" % handler['handler'].__name__)
                        try:
                            handler['handler'](event_obj)
                            logger.info("Handler successfully executed")
                        except Exception as ex:
                            job.not_acknowledge('park')
                            logger.error(ex, exc_info=True)
                            logger.info("Job nacked")
                        else:
                            job.acknowledge()
                            logger.info("Job acknowledged")
                    else:
                        logger.info("No matching event handlers")
                        job.acknowledged()
                        logger.info("Job acknowledged")
                logger.info("Event handlers executed successfully")

        return events_processed


class EventRepository():

    stream_prefix = None # type: ClassVar[str]
    ar_class = None # type: ClassVar[Type[EventSourced]]
    
    def __init__(self, eventstore):
        self.eventstore = eventstore

    def get_stream(self, id):
        return '%s%s' % (self.stream_prefix, id)

    def get_events(self, id):
        events = self.eventstore.get_all_events(self.get_stream(id))

    def get(self, id):
        def convert_events(event):
            return Event.load(event)
        events = [convert_events(event) for event in self.eventstore.get_all_events(self.get_stream(id))]
        if len(events) == 0:
            raise Exception("No events for this ID")
        ar = self.ar_class(id, events, keep_events=False)
        return ar

    def save(self, ar: EventSourced):
        events = ar.get_uncommitted_events()
        ar_version = ar._aggregate_version - len(events)
        self.save_events(events, ar.id, ar_version)
        ar.clear_uncommitted_events()

    def save_events(self, events, id, aggregate_version):
        self.eventstore.save(events, self.get_stream(id), aggregate_version)


class Command():

    def __init__(self, command_name, *args, **kwargs):
        self.command_name = command_name
        self.handler = None
        self.repo = None
        self.args = args
        self.kwargs = kwargs

    @staticmethod
    def create(repo: Type[EventRepository]):
        def real_decorator(fn):
            def wrapper(*args, **kwargs):
                command = Command(fn.__name__, *args, **kwargs)
                command.handler = fn
                eventstore = EventStoreClient.get_default_instance()
                repository = repo(eventstore)
                command.repo = repository
                command_bus = CommandBus.get_default_instance()
                command_bus.run_command(command)
            return wrapper
        return real_decorator

    def __call__(self, *args, **kwargs):
        self.kwargs['repo'] = self.repo
        ar = self.handler(*self.args, **self.kwargs)


class CommandBus():

    instance = None

    def __init__(self):
        pass

    @classmethod
    def get_default_instance(cls):
        if CommandBus.instance is None:
            CommandBus.instance = CommandBus()

        return CommandBus.instance

    def run_command(self, command: Command):
        command()

