from requests import Request, Session, exceptions
import requests
import hmac
import hashlib
import base64
import json
import time
import sys
import datetime
import urllib
import tempfile
import os

SHARED_SECRET = os.getenv("SHARED_SECRET")
API_KEY = os.getenv("API_KEY")
OFFLINE_URL = 'http://tw.ews.mall.yahooapis.com/stauth/v1/Product/Offline'
ONLINE_URL = 'http://tw.ews.mall.yahooapis.com/stauth/v1/Product/Online'
GET_ITEM_INFO_URL = 'https://tw.ews.mall.yahooapis.com/stauth/v3/Product/GetMain'
GET_ITEM_LIST_URL = 'https://tw.ews.mall.yahooapis.com/stauth/v1/Product/GetMainList'
UPDATE_ITEM_INFO_URL = 'https://tw.ews.mall.yahooapis.com/stauth/v1/Product/UpdateMain'
UPDATE_ITEM_ADDON_URL = 'https://tw.ews.mall.yahooapis.com/stauth/v1/Product/UpdateAddon'
GET_STORE_CATEGORY_LIST_URL = 'https://tw.ews.mall.yahooapis.com/stauth/v1/StoreCategory/Get'
UPDATE_ITEM_STOCK_URL = 'https://tw.ews.mall.yahooapis.com/stauth/v1/Product/UpdateStock'
UPDATE_MAIN_URL = 'https://tw.ews.mall.yahooapis.com/stauth/v1/Product/UpdateMain'
INSERT_MAIN_URL = 'https://tw.ews.mall.yahooapis.com/stauth/v2/Product/SubmitMain'
DELETE_MAIN_URL = 'https://tw.ews.mall.yahooapis.com/stauth/v1/Product/Delete'
UPDATE_IMAGE_URL = 'http://tw.ews.mall.yahooapis.com/stauth/v1/Product/UpdateImage'
UPLOAD_IMAGE_URL = "https://tw.ews.mall.yahooapis.com/stauth/v1/Product/UploadImage"
ORDER_QUERY_URL = "https://tw.ews.mall.yahooapis.com/stauth/v1/Order/Query"
CONFIRM_STORE_DELIVERY_URL = "https://tw.ews.mall.yahooapis.com/stauth/v1/OrderShipping/ConfirmStoreDelivery"
GET_STORE_DELIVERY_RECEIPT_DETAIL_URL = "https://tw.ews.mall.yahooapis.com/stauth/v1/OrderShipping/GetStoreDeliveryReceiptDetail"
CONFIRM_HOME_DELIVERY_URL = "https://tw.ews.mall.yahooapis.com/stauth/v2/OrderShipping/ConfirmHomeDelivery"
STORE_DELIVERY_CANCEL_URL = "https://tw.ews.mall.yahooapis.com/stauth/v1/OrderShipping/CancelStoreDeliveryReceipt"

ORDER_QUERY_MASTER_URL = "https://tw.ews.mall.yahooapis.com/stauth/v1/Order/GetMaster"
ORDER_QUERY_DETAIL_URL = "https://tw.ews.mall.yahooapis.com/stauth/v1/Order/GetDetail"
ORDER_QUERY_CANCEL_URL = "https://tw.ews.mall.yahooapis.com/stauth/v1/Cancel/Query"

TIMEOUT_10 = 10
TIMEOUT_20 = 20
TIMEOUT_30 = 30

class YahooApiUtils:

    def __init__(self):
        super().__init__()

    @staticmethod
    def store_delivery_cancel(receiptId):
        try:
            body = YahooApiUtils._get_default_body()
            body['DeliveryReceiptId'] = receiptId
 
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("GET", STORE_DELIVERY_CANCEL_URL + "?" + YahooApiUtils.data_to_string(body))
          
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def confirm_home_delivery(TransactionId, OrderId, ShippingSupplierCode, ShippingNumber):
        try:
            body = YahooApiUtils._get_default_body()
            body['TransactionId'] = TransactionId
            body['OrderId'] = OrderId
            body['ShippingSupplierCode'] = ShippingSupplierCode
            body['ShippingNumber'] = ShippingNumber

            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("GET", CONFIRM_HOME_DELIVERY_URL + "?" + YahooApiUtils.data_to_string(body))
          
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def get_store_delivery_receipt_detail(Id):
        try:
            body = YahooApiUtils._get_default_body()
            body['DeliveryReceiptId'] = Id

            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("GET", GET_STORE_DELIVERY_RECEIPT_DETAIL_URL + "?" + YahooApiUtils.data_to_string(body))
            # req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def confirm_store_delivery(TransactionId, OrderId):
        strOrderId = ""

        try:
            body = YahooApiUtils._get_default_body()
            body['TransactionId'] = TransactionId
          
            for id in OrderId:
                strOrderId += "OrderId" + '=' + id + '&'
            
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body) + "&" + strOrderId[:-1])

            req = Request("GET", CONFIRM_STORE_DELIVERY_URL + "?" + YahooApiUtils.data_to_string(body) + "&" + strOrderId[:-1])
    
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def order_cancel(datestr_s, datestr_e, position=1, count=1):
        try:
            body = YahooApiUtils._get_default_body()
            body['CancelReason'] = "All"
            body['DateType'] = "OrderDate"
            body['StartDate'] = datestr_e
            body['EndDate'] = datestr_s
            body['Position'] = str(position)
            body['Count'] = count
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", ORDER_QUERY_CANCEL_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def order_query(datestr, position=1, count=1, order_type="StoreDelivery"):
        try:
            body = YahooApiUtils._get_default_body()
            body['OrderType'] = "All"
            body['ShippingType'] = order_type
            body['DateType'] = "TransferDate"
            body['StartDate'] = datestr
            body['EndDate'] = datestr
            body['Position'] = str(position)
            body['Count'] = count
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", ORDER_QUERY_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def order_query_master(TransactionId):
        try:
            body = YahooApiUtils._get_default_body()
            body['TransactionId'] = TransactionId
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", ORDER_QUERY_MASTER_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def order_query_detail(TransactionId, OrderIds):
        try:
            body = YahooApiUtils._get_default_body()
            
            body['TransactionId'] = TransactionId

            string_data = ""
           
            for Order in OrderIds:
                string_data += 'OrderId' + '=' + str(Order['@Id']) + '&'

            body['Signature'] = YahooApiUtils._get_signature(string_data + YahooApiUtils.data_to_string(body))

            req = Request("POST", ORDER_QUERY_DETAIL_URL + "?" + string_data + YahooApiUtils.data_to_string(body))
            #req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def upload_images(prod_id_yh, image_no, is_purge, img_data):
        try:
           
            body = YahooApiUtils._get_default_body()
            body['ProductId'] = prod_id_yh
            # body['ImageName' + str(image_no)] = img_data
            body['MainImage'] = "ImageFile1"
            body['Purge'] = is_purge
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", UPLOAD_IMAGE_URL)

            headers = {'Content-Disposition': 'form-data', 'name':"ImageFile" + str(image_no), 'filename':img_data}
            req.headers = headers
            req.data = body
            
            files = {"ImageFile" + str(image_no): open(img_data,'rb')}
            
            req.files = files

            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def update_images(prod_id_yh, image_no, is_purge, img_data):
        try:
           
            body = YahooApiUtils._get_default_body()
            body['ProductId'] = prod_id_yh
            # body['ImageName' + str(image_no)] = img_data
            body['MainImage'] = "ImageFile" + str(image_no)
            body['Purge'] = is_purge
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", UPDATE_IMAGE_URL)

            headers = {'Content-Disposition': 'form-data', 'name':'"ImageFile" + str(image_no)', 'filename':img_data}
            req.headers = headers
            req.data = body
            
            files = {"ImageFile" + str(image_no): open(img_data,'rb')}
            
            req.files = files

            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def update_main_by_case_book(prod_id_yh, productName, category_id, shortDescript, longDescript, classificationName, classificationValue, prod_id, is_tax_free, list_price, sale_price):
        try:
            body = YahooApiUtils._get_default_body()
            body['ProductId'] = prod_id_yh
            body['ProductName'] = productName
            body['MallCategoryId'] = category_id
            body['ShortDescription'] = shortDescript
            body['LongDescription'] = longDescript
            body['Attribute.1.Name'] = classificationName
            body['Attribute.1.Value'] = classificationValue
            body['CustomizedMainProductId'] = prod_id
            body['IsTaxFree'] = is_tax_free
            body['MarketPrice'] = int(list_price)
            body['SalePrice'] = int(sale_price)
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", UPDATE_MAIN_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def insert_main_by_case_book(productName, catIdYho, shortDescript, longDescript, classificationName, classificationValue, prod_id, storeCategory, MarketPrice, SalePrice, is_tax_free):
        try:
            body = YahooApiUtils._get_default_body()
            body['SaleType'] = "Normal"
            body['ProductName'] = productName
            body['MallCategoryId'] = catIdYho
            body['MarketPrice'] = MarketPrice
            body['SalePrice'] = SalePrice
            body['MaxBuyNum'] = "100"
            body['ShortDescription'] = shortDescript
            body['LongDescription'] = longDescript
            body['PayTypeId'] = "13"
            body['ShippingId'] = "82"
            body['Attribute.1.Name'] = classificationName
            body['Attribute.1.Value'] = classificationValue
            body['Stock'] = "0"
            body['SaftyStock'] = "1"
            body['SpecTypeDimension'] = "0"
            body['CustomizedMainProductId'] = prod_id # + storeCategory
            body['IsTaxFree'] = is_tax_free
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", INSERT_MAIN_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def insert_main_by_case_bazzar(productName, catIdYho, shortDescript, longDescript, classificationName, classificationValue, prod_id, storeCategory, MarketPrice, SalePrice, is_tax_free):
        try:
            body = YahooApiUtils._get_default_body()
            body['SaleType'] = "Normal"
            body['ProductName'] = productName
            body['MallCategoryId'] = catIdYho
            body['MarketPrice'] = MarketPrice
            body['SalePrice'] = SalePrice
            body['MaxBuyNum'] = "100"
            body['ShortDescription'] = shortDescript
            body['LongDescription'] = longDescript
            body['PayTypeId'] = "13"
            body['ShippingId'] = "82"
            body['Attribute.1.Name'] = classificationName
            body['Attribute.1.Value'] = classificationValue
            body['Stock'] = "0"
            body['SaftyStock'] = "1"
            body['SpecTypeDimension'] = "0"
            body['CustomizedMainProductId'] = prod_id # + storeCategory
            body['IsTaxFree'] = is_tax_free
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", INSERT_MAIN_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def update_main_by_case_bazzar(prod_id_yh, productName, category_id, shortDescript, longDescript, classificationName, classificationValue, prod_id, is_tax_free, list_price, sale_price):
        try:
            body = YahooApiUtils._get_default_body()
            body['ProductId'] = prod_id_yh
            body['ProductName'] = productName
            body['MallCategoryId'] = category_id
            body['ShortDescription'] = shortDescript
            body['LongDescription'] = longDescript
            body['CustomizedMainProductId'] = prod_id
            body['Attribute.1.Name'] = classificationName
            body['Attribute.1.Value'] = classificationValue
            body['MarketPrice'] = int(list_price)
            body['SalePrice'] = int(sale_price)
            body['IsTaxFree'] = is_tax_free
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", UPDATE_MAIN_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def update_item_stock(item_id, qty):
        try:
            body = YahooApiUtils._get_default_body()
            body['ProductId'] = item_id
            body['Spec.1.Id'] = '1'
            body['Spec.1.Action'] = 'add' if qty >= 0 else 'del'
            body['Spec.1.Stock'] = abs(qty)
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", UPDATE_ITEM_STOCK_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response

        except Exception as e:
            raise e

    @staticmethod
    def update_item_price(item_id, list_price, sale_price):
        try:
            body = YahooApiUtils._get_default_body()
            body['ProductId'] = item_id
            body['MarketPrice'] = int(list_price)
            body['SalePrice'] = int(sale_price)
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", UPDATE_ITEM_INFO_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response

        except Exception as e:
            raise e

    @staticmethod
    def update_store_category(item_id, store_category):
        try:
            body = YahooApiUtils._get_default_body()
            body['ProductId'] = item_id
            body['StoreCategoryId'] = store_category
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", UPDATE_ITEM_INFO_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_10)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def get_item_list_by_store_category(store_category):
        try:
            body = YahooApiUtils._get_default_body()
            body['StoreCategoryId'] = store_category
            body['Position'] = 1
            body['Count'] = 1
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", GET_ITEM_LIST_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_20)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def get_item_list(product_status, order_by, position, count=100):
        try:
            body = YahooApiUtils._get_default_body()
            body['ProductStatus'] = product_status
            body['Position'] = position
            body['OrderBy'] = order_by
            body['Count'] = count
            body['Position'] = position
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", GET_ITEM_LIST_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def get_item_stock(product_id, spec_number=1):
        try:
            response = YahooApiUtils.get_item_info(product_id)
            spec_list = response['Response']['Product']['SpecList']['Spec']

            stock = [x['CurrentStock'] for x in spec_list if x['@Id'] == spec_number][0]
            return stock

        except Exception as e:
            raise e

    @staticmethod
    def get_store_category_list():
        try:
            body = YahooApiUtils._get_default_body()
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", GET_STORE_CATEGORY_LIST_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_20)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def get_item_info(item_id):
        try:
            body = YahooApiUtils._get_default_body()
            body['ProductId'] = item_id
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", GET_ITEM_INFO_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_10)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def unlist_batch_items(id_list):
        try:
            body = YahooApiUtils._get_default_body()
            body['ProductId'] = id_list
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", OFFLINE_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def delete_items(id_list):
        try:
            body = YahooApiUtils._get_default_body()
            body['ProductId'] = id_list
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", DELETE_MAIN_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def list_batch_items(id_list):
        try:
            body = YahooApiUtils._get_default_body()
            body['ProductId'] = id_list
            body['Signature'] = YahooApiUtils._get_signature(YahooApiUtils.data_to_string(body))

            req = Request("POST", ONLINE_URL)
            req.data = body
            prepped = req.prepare()

            s = Session()
            response = s.send(prepped, timeout=TIMEOUT_30)
            return response.json()

        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def data_to_string(data):
        string_data = ""
        try:
            for key, value in data.items():
                if type(value) == list:
                    for item in value:
                        string_data += str(key) + '=' + str(item) + '&'

                else:
                    string_data += str(key) + '=' + str(value) + '&'

        except Exception as e:
            print(e)

        return string_data[:-1]

    @staticmethod
    def _get_default_body():
        return {
            'ApiKey': API_KEY,
            'TimeStamp': time.time(),
            'Format': 'json',
        }

    @staticmethod
    def _get_signature(data):
        dig = hmac.new(SHARED_SECRET.encode(), msg=data.encode(), digestmod=hashlib.sha1).hexdigest()
        return dig

    @staticmethod
    def _get_timestamp():
        timestamp = int(time.time())
        return timestamp
