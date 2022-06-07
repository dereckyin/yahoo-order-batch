import time
import json
import hmac
import hashlib
import os

class ShopeePayload:
    SHOP_ID = os.getenv("SHOP_ID")
    PARTNER_ID = os.getenv("PARTNER_ID")
    SECRET_KEY = os.getenv("SECRET_KEY")
    UNLIST_URL = 'https://partner.shopeemobile.com/api/v1/items/unlist'
    UPDATE_STOCK_URL = 'https://partner.shopeemobile.com/api/v1/items/update_stock'
    GET_CATEGORIES_URL = 'https://partner.shopeemobile.com/api/v1/item/categories/get'
    GET_ATTRIBUTES_URL = 'https://partner.shopeemobile.com/api/v1/item/attributes/get'
    GET_ITEM_DETAIL_URL = 'https://partner.shopeemobile.com/api/v1/item/get'
    ADD_ITEM_URL = 'https://partner.shopeemobile.com/api/v1/item/add'

    def __init__(self):
        self.partner_id = ShopeePayload.PARTNER_ID
        self.shopid = ShopeePayload.SHOP_ID

    def get_default_body(self):
        return {
            'partner_id': self.partner_id,
            'shopid': self.shopid,
            'timestamp': self.get_timestamp()
        }

    def get_headers(self, url, body):
        return {
            'Content-Type' : 'application/json',
            'Authorization' : self.sign(url, json.dumps(body))
        }

    def sign(self, url, body):
        bs = url + "|" + body
        dig = hmac.new(ShopeePayload.SECRET_KEY.encode(), msg=bs.encode(),
                       digestmod=hashlib.sha256).hexdigest()
        return dig

    def get_timestamp(self):
        timestamp = int(time.time())
        return timestamp
