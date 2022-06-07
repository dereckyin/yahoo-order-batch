from requests import Request, Session, exceptions
import os
import json
import time
import hmac
import hashlib
import sys
import requests
import linecache
import logging


class ShopeeApiUtils:
    SHOP_ID = os.getenv("SHOP_ID")
    PARTNER_ID = os.getenv("PARTNER_ID")
    SECRET_KEY = os.getenv("SECRET_KEY")
    UNLIST_URL = 'https://partner.shopeemobile.com/api/v1/items/unlist'

    def __init__(self):
        super().__init__()

    def unlist_batch_items(self, items):
        body = self.get_default_body()
        body['items'] = items
        headers = self.get_headers(self.UNLIST_URL, body)
        
        response = requests.post(self.UNLIST_URL, data=json.dumps(body), headers=headers)
        return response.json()

    def get_headers(self, url, body):
        return {
            'Content-Type' : 'application/json',
            'Authorization' : self._sign(url, json.dumps(body))
        }

    def get_default_body(self):
        return {
            'partner_id': self.PARTNER_ID,
            'shopid': self.SHOP_ID,
            'timestamp': self._get_timestamp()
        }

    # Generates the authentication hash verification code
    def _sign(self, url, body):
        bs = url + "|" + body
        dig = hmac.new(self.SECRET_KEY.encode(), msg=bs.encode(),
                       digestmod=hashlib.sha256).hexdigest()
        return dig

    def _get_timestamp(self):
        timestamp = int(time.time())
        return timestamp
