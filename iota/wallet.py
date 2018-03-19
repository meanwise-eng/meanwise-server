from meanwise_backend.eventsourced import EventSourced, EventRepository, Event


class WalletCreated(Event):
    pass


class Wallet(EventSourced):

    @classmethod
    create(profile_id, seed):
        event = WalletCreated(profile_id, data={'seed': seed})
        return Wallet(profile_id, [event])
