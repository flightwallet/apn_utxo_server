#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bd import get_wallets_from_db
from gobiko.apns import APNsClient
from apscheduler.schedulers.background import BackgroundScheduler
from functools import partial
from tools import return_unspent_outputs, gen_hash_for_dict
from bd import redis
import config
import logging
logging.basicConfig()
import json
import time
import requests

silent_message = {'content_available': True, 'alert': None, 'badge': 0}

def create_apn_service():
    apns = APNsClient(
        team_id="AE86HBQRXP",
        bundle_id="org.flightwallet.flight-wallet",
        auth_key_id="U23QG89AKK",
        auth_key_filepath="aps_dev_key.p8",
        use_sandbox=False
    )
    return apns


def update_wallets_states(force_update=False):
    # all wallets are stored in MongoDB
    wallets = get_wallets_from_db()
    addresses = [wallet['address'] for wallet in wallets]
    address_to_device_token = {wallet['address']: wallet['device_token'] for wallet in wallets}
    addresses_unspent_outputs = {}
    # for each wallet address we make POST to get utox
    for address in addresses:
        addresses_unspent_outputs[address] = return_unspent_outputs(address)

    for address, utxos in addresses_unspent_outputs.items():
        # all states of wallets are stored in redis
        previous_state_of_address = redis.get(address)
        # in the form of hashes(for simplicity)
        current_state_of_address = gen_hash_for_dict(utxos)
        # send notifications in two cases
        # if we force it every 1 hour
        # if balance changed
        if force_update or (current_state_of_address != previous_state_of_address):
            print('Sending...')
            unspent = 0
            for unspent_output in addresses_unspent_outputs[address]:
                unspent += unspent_output['value']
            config.apns.send_message(address_to_device_token[address], "Unspent balance: {}".format(unspent))
            # update redis database on current states of wallets
            redis.set(address, current_state_of_address)
            # for each utox we send notification
            # with utox info, count of utox and total number of utox
            total_count = len(addresses_unspent_outputs[address])
            for i, unspent_output in enumerate(addresses_unspent_outputs[address]):
                silent_message['extra'] = {'data': json.dumps(unspent_output), 'count': i, 'total_count': total_count}
                config.apns.send_message(address_to_device_token[address], **silent_message)


def start_background_push_notifications():
    # do a job every X seconds/minutes
    scheduler = BackgroundScheduler()
    # every hour syncs
    scheduler.add_job(func=partial(update_wallets_states, force_update=True), trigger='interval', minutes=config.SYNC_PERIOD)
    # online(almost) syns
    scheduler.add_job(func=partial(update_wallets_states, force_update=False), trigger='interval', seconds=config.ONLINE_SYNC_PERIOD)

    # logger
    log = logging.getLogger('apscheduler.executors.default')
    log.setLevel(logging.WARNING)  # DEBUG
    fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    h = logging.StreamHandler()
    h.setFormatter(fmt)
    log.addHandler(h)
    scheduler.start()
    return scheduler
