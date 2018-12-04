#!/usr/bin/env python
# -*- coding: utf-8 -*-

# node with bitcore-node and insight-api
BASE_URL = 'https://test-insight.swap.online/insight-api/addrs/utxo'

# parameters of server
HOST = '0.0.0.0'
PORT = '5000'

# parameters of push updates
KEY_FILE = 'aps_dev_key.p8'

EXPIRY = 60 * 60  # seconds
PRIORITY = 10
SYNC_PERIOD = 60  # minutes
ONLINE_SYNC_PERIOD = 5  # seconds
