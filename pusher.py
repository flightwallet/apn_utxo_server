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
import json
import time
import requests

def create_apn_service(cert_file, key_file):
    apns = APNsClient(
        team_id="AE86HBQRXP",
        bundle_id="org.flightwallet.flight-wallet",
        auth_key_id="U23QG89AKK",
        auth_key_filepath="aps_dev_key.p8",
        use_sandbox=False
    )
    return apns


def update_wallets_states(force_update=False):
    wallets = get_wallets_from_db()
    addresses = [wallet['address'] for wallet in wallets]
    address_to_device_token = {wallet['address']: wallet['device_token'] for wallet in wallets}
    device_token_to_address = {wallet['device_token']: wallet['address'] for wallet in wallets}
    addresses_unspent_outputs = return_unspent_outputs(addresses)

    expiry = time.time() + config.EXPIRY
    priority = config.PRIORITY
    for address, utxos in addresses_unspent_outputs.items():
        previous_state_of_address = redis.get(address)
        current_state_of_address = gen_hash_for_dict(utxos)
        print(address, previous_state_of_address, current_state_of_address)
        if force_update or (current_state_of_address != previous_state_of_address):
            print('Sending...')
            unspent = 0
            for unspent_output in addresses_unspent_outputs[address]:
                unspent += unspent_output['value']
            apns.send_message(address_to_device_token[address], "Unspent balance: {}".format(unspent))
        redis.set(address, current_state_of_address)
        

def start_background_push_notifications():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=partial(update_wallets_states, force_update=True), trigger='interval', minutes=config.SYNC_PERIOD)

    scheduler.add_job(func=partial(update_wallets_states, force_update=False), trigger='interval', seconds=config.ONLINE_SYNC_PERIOD)
    log = logging.getLogger('apscheduler.executors.default')
    log.setLevel(logging.WARNING)  # DEBUG

    fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    h = logging.StreamHandler()
    h.setFormatter(fmt)
    log.addHandler(h)
    scheduler.start()
    return scheduler