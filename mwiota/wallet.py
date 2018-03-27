import math
from random import SystemRandom

from meanwise_backend.eventsourced import (EventSourced, EventRepository, Event, Command,)


class WalletCreated(Event):
    pass


class Wallet(EventSourced):

    @classmethod
    def create(cls, profile_id, seed):
        event = WalletCreated(profile_id, data={'seed': seed})
        return Wallet(profile_id, [event])

    def _apply_WalletCreated(self, event):
        pass


class WalletRepository(EventRepository):
    stream_prefix = 'mw_iota_wallet-'
    ar_class = Wallet


def _create_seed():
    generator = SystemRandom()
    alphabet = '9ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return u''.join(generator.choice(alphabet) for _ in range(81))


@Command.create(repo=WalletRepository)
def create_wallet(profile_id, repo: WalletRepository):
    try:
        wallet = repo.get(profile_id)
    except Exception:
        pass
    else:
        if wallet is not None:
            return

    seed = _create_seed()
    wallet = Wallet.create(profile_id, seed)
    repo.save(wallet)


def encode_tryte3_string_as_bytes(tryte3_str: str) -> bytes:
    tryte3_values = convert_tryte3_characters_to_values(tryte3_str)
    tryte5_values = _shift_trytes(tryte3_values, 3, 5)

    return bytes(tryte5_values)


def decode_tryte3_string_from_bytes(from_bytes: bytes) -> str:
    from_byte_values = list(from_bytes)
    tryte3_values = _shift_trytes(from_byte_values, 5, 3)
    tryte3_str = convert_tryte3_values_to_chars(tryte3_values)
    return tryte3_str

def encode_bytes_as_tryte3_string(from_bytes: bytes) -> str:
    from_byte_values = list(from_bytes)
    tryte3_values = _shift_trytes(from_byte_values, 6, 3)
    tryte3_str = convert_tryte3_values_to_chars(tryte3_values)
    return tryte3_str

def decode_bytes_from_tryte3_string(tryte3_str: str) -> bytes:
    tryte3_values = convert_tryte3_characters_to_values(tryte3_str)
    tryte6_values = _shift_trytes(tryte3_values, 3, 6)
    for tryte6_value in tryte6_values:
        if tryte6_value > 255:
            raise Exception("Tryte value higher than 255 cannot be converted.")

    return bytes(tryte6_values)


TRYTE_CHARS = '9ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def convert_tryte3_characters_to_values(tryte3_str):
    tryte3_values = []
    for tryte3_char in tryte3_str:
        value = TRYTE_CHARS.index(tryte3_char)
        if value < 0:
            return null
        tryte3_values.append(value)

    return tryte3_values


def convert_tryte3_values_to_chars(tryte3_values):
    tryte3_str = ''
    for value in tryte3_values:
        if value < 0 or value >= 27:
            return None
        tryte3_str += TRYTE_CHARS[value]

    return tryte3_str


def _shift_trytes(from_list, size_from, size_to):
    to_list = []
    trits = 0
    tmp_tryte = 0
    padding = 0

    from_value_max = 3**size_from
    to_value_max = 3**size_to

    for value in from_list:
        if value > from_value_max:
            padding = value
            break

        factor = 3**trits
        trits += size_from
        tmp_tryte += value * factor

        while trits >= size_to:
            tryte = tmp_tryte % to_value_max
            tmp_tryte = (tmp_tryte - tryte) / to_value_max
            trits -= size_to
            to_list.append(int(tryte))

    while trits > 0:
        new_tryte = tmp_tryte % to_value_max
        tmp_tryte = (tmp_tryte - new_tryte) / to_value_max
        trits -= size_to
        to_list.append(int(new_tryte))

    if size_to > size_from:
        if trits < 0:
            to_list.append(int(to_value_max - math.floor(trits / size_from)))
    else:
        if padding != 0:
            skip = padding - from_value_max
            to_list = to_list[0:-skip]

    return to_list
