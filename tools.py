#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import hashlib
from schema import Schema, Use, Optional, Or
from collections import defaultdict
import time
import requests
import config

wallet_schema = Schema({
    'address': Or(str, unicode), 
    'device_token': Or(str, unicode)
})

wallets_schema = Schema([wallet_schema])

unspent_output_schema = Schema({
    'tx_hash': Or(str, unicode),
    'script': Or(str, unicode),
    'value': int,
    'vout': int,
})

unspent_outputs_schema = Schema({
    'timestamp': int,
    'outputs': [unspent_output_schema]
})

def preprocess_output(output):
    """
    Preprocessing raw output form insight-api
    """
    output_processed = {
        'value': output['satoshis'],
        'tx_hash': output['txid'],
        'script': output['scriptPubKey'],
        'vout': output['vout']
    }
    unspent_output_schema.validate(output_processed)
    return output_processed


def return_unspent_outputs(address):
    """
    Getting data from bitcore insight-api for one address
    """
    d = []
    r = requests.post(config.BASE_URL, data={'addrs': address})
    try:
        raw_unspent_outputs = r.json()
    except ValueError:
        return []

    for raw_unspent_output in raw_unspent_outputs:
        d.append(preprocess_output(raw_unspent_output))

    return d


def gen_hash_for_dict(d):
    return hashlib.sha1(json.dumps(d, sort_keys=True)).hexdigest()