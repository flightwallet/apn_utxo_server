#!/usr/bin/env python
# -*- coding: utf-8 -*-
import config
from bd import redis, add_wallet_to_db
from pusher import create_apn_service, start_background_push_notifications
from flask import Flask, jsonify
from flask import request as frequest
import json

app = Flask(__name__)


@app.route('/subscribe', methods=['POST'])
def route_server():
    """
    Add new wallet with POST
    """
    wallet_raw = json.loads(frequest.data)
    wallet = {}
    try:
        wallet['address'] = wallet_raw['address']
        wallet['device_token'] = wallet_raw['deviceToken']
    except KeyError:
        pass
    add_wallet_to_db(wallet)
    return 'true'

def main():
    # init Apple Push Notification Client
    config.apns = create_apn_service()
    # background notifications
    start_background_push_notifications()
    # Flask server for registration
    app.run(host=config.HOST, port=config.PORT)

if __name__ == "__main__":
    main()