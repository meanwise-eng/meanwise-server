import redis
import json
import logging
import uuid
import hashlib

from ecdsa import SigningKey, NIST192p
from ecdsa.util import randrange_from_seed__trytryagain
from iota.crypto.addresses import AddressGenerator
from iota import Iota, TryteString, ProposedTransaction, ProposedBundle, Tag

from meanwise_backend.eventsourced import Event, handle_event
from .wallet import (Wallet, WalletCreated, create_wallet, encode_tryte3_string_as_bytes,
                     encode_bytes_as_tryte3_string)
from userprofile.profile import ProfileCreated
from credits.critic import Criticized

from django.conf import settings

logger = logging.getLogger('meanwise_backend.%s' % __name__)


@handle_event(eventType=ProfileCreated, category='mw_profile_profile')
def handle_profile_created_create_wallet(event: ProfileCreated):
    create_wallet(event.metadata['aggregateId'])


@handle_event(eventType=WalletCreated, category='mw_iota_wallet')
def create_wallet_in_read_model(event: WalletCreated):
    r = redis.StrictRedis(host=settings.REDIS_HOST)
    wallet_id = event.metadata['aggregateId']
    aggregate_version = 1
    wallet = {
        'seed': event.data['seed'],
        'key_index': 0,
        'aggregate_version': 1
    }
    wallet_key = 'iota-wallet_%s' % wallet_id

    with r.pipeline() as pipe:
        retry_count = 0
        while True:
            try:
                pipe.watch(wallet_key)
                wallet_data = pipe.get(wallet_key)
                if wallet_data is not None:
                    wallet = json.loads(wallet_data.decode('UTF-8'))
                    if wallet['aggregate_version'] < aggregate_version -1:
                        raise Exception("Should retry later")
                    elif wallet['aggregate_version'] >= aggregate_version -1:
                        logger.info("Event already processed for read model")
                        return
                pipe.multi()
                pipe.set('iota-wallet_%s' % wallet_id, json.dumps(wallet))
                pipe.execute()
                break
            except redis.WatchError:
                if retry_count < 3:
                    continue

                raise Exception("Could not save wallet to read model")


#@handle_event(eventType=Criticized, category='mw_credits_credits')
def add_critic_to_tangle(event: Criticized):
    criticized = uuid.UUID(event.metadata['aggregateId'])
    criticizer = uuid.UUID(event.data['criticizer'])
    post_id = uuid.UUID(event.data['post_id'])

    criticized_wallet = get_wallet(event.metadata['aggregateId'])
    criticizer_wallet = get_wallet(event.data['criticizer'])
    sk = get_ecdsa_signing_key(criticizer_wallet)
    data = bytearray()

    data += b'\x01\x01'
    data += criticizer.int.to_bytes(16, byteorder='big')
    data += post_id.int.to_bytes(16, byteorder='big')
    data += criticized.int.to_bytes(16, byteorder='big')
    skill_b = event.data['skill'].encode()
    data += len(skill_b).to_bytes(1, byteorder='big')
    data += skill_b
    data += event.data['rating'].to_bytes(1, byteorder='big')

    sig = sk.sign(data, hashfunc=hashlib.sha1)
    msg = encode_bytes_as_tryte3_string(data+sig)
    
    to_address = get_address(criticized_wallet)
    logger.info("Address %s" % (to_address))
    from_address = get_address(criticizer_wallet)
    txn = ProposedTransaction(address=to_address, message=msg,
                              tag=Tag(b'MEANWISEB'), value=0)
    logger.info("Txn:")
    logger.info(txn)
    bundle = ProposedBundle(transactions=[txn])
    bundle.finalize()
    bt = bundle.as_tryte_strings()
    logger.info(bt)

    api = Iota('http://54.173.49.102:15600', criticizer_wallet['seed'])
    res = api.send_trytes(trytes=bt, depth=3)
    logger.info(res)


def get_wallet(wallet_id):
    r = redis.StrictRedis(host=settings.REDIS_HOST)
    
    wallet_key = 'iota-wallet_%s' % wallet_id
    wallet_data = r.get(wallet_key)
    if wallet_data is None:
        raise Exception("Wallet doesn't exist for wallet_id %s" % wallet_id)

    wallet = json.loads(wallet_data.decode('UTF-8'))
    return wallet


def get_ecdsa_signing_key(wallet):
    seed = encode_tryte3_string_as_bytes(wallet['seed'])
    secexp = randrange_from_seed__trytryagain(seed, NIST192p.order)
    sk = SigningKey.from_secret_exponent(secexp, curve=NIST192p)

    return sk


def get_address(wallet):
    generator = AddressGenerator(wallet['seed'].encode())
    addresses = generator.get_addresses(start=wallet['key_index'], count=1)

    return addresses[0]
