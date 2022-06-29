# -*- coding:utf-8 -*-
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import json
import requests
from datetime import datetime, timedelta
import logging
import sys
import linecache
import os
import cx_Oracle
import uvicorn
import hashlib 
from enum import Enum
import re
from fastapi.middleware.cors import CORSMiddleware

from public.yahoo_api_utils import YahooApiUtils as yh_utils
from public.yahoo_api_dao import YahooApiDao
from public.custom_exceptions import *
from public.project_variables import *

from models.product_factory import ProductFactory
import math
from linebot import LineBotApi
from linebot.models import TextSendMessage

#from opentelemetry import trace
#from opentelemetry.exporter import jaeger
#from opentelemetry.sdk.trace import TracerProvider
#from opentelemetry.sdk.trace.export import BatchExportSpanProcessor

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
trace.set_tracer_provider(
   TracerProvider(
       resource=Resource.create({SERVICE_NAME: "yahoo-order-service"})
   )
)
jaeger_exporter = JaegerExporter(
   agent_host_name=os.getenv("AGENT_HOST"),
   agent_port=int(os.getenv("AGENT_HOST_PORT")),
)
trace.get_tracer_provider().add_span_processor(
   BatchSpanProcessor(jaeger_exporter)
)
tracer = trace.get_tracer(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_BOT_KEY"))

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Object:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
# line api key

def batchfailnotify(message):
	#push message to dereck
	line_bot_api.push_message(os.getenv("LINE_BOT_ID"), TextSendMessage(text=message))

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    logging.error('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def settingLog():
    # 設定
    datestr = datetime.today().strftime('%Y%m%d')
    if not os.path.exists("log/" + datestr):
        os.makedirs("log/" + datestr)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S',
                        handlers = [logging.FileHandler('log/' + datestr + '/yahoo_sp.log', 'a', 'utf-8'),])

    
    # 定義 handler 輸出 sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # 設定輸出格式
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # handler 設定輸出格式
    console.setFormatter(formatter)
    # 加入 hander 到 root logger
    logging.getLogger('').addHandler(console)

def save_response(file_name, resp):
    datestr = datetime.today().strftime('%Y%m%d')
    if not os.path.exists("log/" + datestr):
        os.makedirs("log/" + datestr)

    filename = "log/" + datestr + "/" + file_name + ".txt"
    with  open(filename, 'w') as file_object:
        file_object.write(str(resp._content))

def save_json(file_name="", txt=""):
    datestr = datetime.today().strftime('%Y%m%d')
    if not os.path.exists("log/" + datestr):
        os.makedirs("log/" + datestr)

    filename = "log/" + datestr + "/" + file_name + ".json"
    with  open(filename, 'w') as file_object:
        file_object.write(txt)

def total_count_by_transaction(r):
    with tracer.start_as_current_span("total_count_by_transaction"):
        total_cnt = 0
        if r['Response']['@Status'] == "ok":
            total_cnt = r['Response']['TransactionList']["@TotalCount"]
        return int(total_cnt)

def order_master(order_list):
    with tracer.start_as_current_span("order_master"):
        master = []
        for order in order_list:
            receipt = yh_utils.order_query_master(order['@Id'])
            logging.info('order_master_store:' + order['@Id'] + ' ' + str(receipt))
            if receipt['Response']['@Status'] == "ok":
                master.append(receipt['Response']['Transaction'])
        return master

def order_detail(master):
    with tracer.start_as_current_span("order_detail"):
        detail = []
        for order in master:
            od = []
            if not isinstance(order['OrderList']['Order'], (list)):
                od.append(order['OrderList']['Order'])
                receipt = yh_utils.order_query_detail(order['@Id'], od)
            else:
                receipt = yh_utils.order_query_detail(order['@Id'], order['OrderList']['Order'])
            logging.info('order_detail_store:' + order['@Id'] + ' ' + str(receipt))
            if receipt['Response']['@Status'] == "ok":
                detail.append(receipt['Response']['Transaction'])
        return detail

def save_order(master, detail):
    with tracer.start_as_current_span("save_order"):
        with YahooApiDao() as operations_dao:
            try:
                operations_dao.order_main_store(master, detail)
                operations_dao.order_master_store(master, detail)
                operations_dao.order_detail_store(master, detail)
                operations_dao.commit_changes()
            except Exception as e:
                batchfailnotify("Yahoo error save_order")

def cancel_order(master):
    with tracer.start_as_current_span("cancel_order"):
        with YahooApiDao() as operations_dao:
            operations_dao.order_master_cancel(master)
            operations_dao.commit_changes()

def transfer_order():
    with tracer.start_as_current_span("transfer_order"):
        with YahooApiDao() as operations_dao, YahooApiDao() as main_loop_dao, YahooApiDao() as detail_dao:
            # yahoo order main = 'A'
            main_loop_dao.get_orders_to_transfer("A")
            while True:
                main_data = main_loop_dao.fetchone()
                if not main_data:
                    break
                detail_dao.get_order_detail_to_transfer(main_data['TRANSACTIONID'])
                detail_data = detail_dao.fetchall()
                if not detail_data:
                    continue
                # initiate order data
                revName = detail_data[0]["RECEIVERNAME"]
                revPhone = detail_data[0]["RECEIVERMOBILE"].replace("#", "-")
                revTel = detail_data[0]["RECEIVERPHONE"].replace("#", "-")
                revAddr = detail_data[0]["RECEIVERADDRESS"]
                revZip = detail_data[0]["RECEIVERZIPCODE"]
                revEmail = "www_taaze_tw@yahoo.com.tw"
                js = {}

                js['orderComm'] = '1'
                js['masNo'] = ''
                js['revName'] = revName
                js['revPhone'] = revPhone
                js['revEmail'] = revEmail
                js['revTel'] = revTel
                if main_data['SHIPPINGTYPE'] == 'HomeDelivery':
                    js['revAddr'] = revAddr
                    js['distNo'] = 'H'
                    js['revStno'] = ''
                    js['stName'] = ''
                    js['pmMethod'] = 'C'
                else:
                    storeInfo = revAddr.split('｜')
                    js['revAddr'] = storeInfo[2]
                    if main_data['STORETYPE'] == 'Family':
                        js['distNo'] = 'F'
                    if main_data['STORETYPE'] == 'HiLife':
                        js['distNo'] = 'L'
                    js['revStno'] = storeInfo[0]
                    js['stName'] = storeInfo[1]
                    js['pmMethod'] = 'A'
                js['reSellerId'] = 'www_taaze_tw@yahoo.com.tw'
                js['ecCode'] = ''
                js['ecPrice'] = ''
                js['invTitle'] = ''
                js['invVatNo'] = ''
                js['rcvCityId'] = ''
                js['rcvTownId'] = ''
                js['rcvZip'] = revZip
                js['mallFreSoNo'] = ''
                js['freight'] = '0'
                
                ja = []

                for detail in detail_data:
                    jo = {}

                    if('物流服務費' in detail['PRODUCTNAME']):
                        js['mallFreSoNo'] = detail['ORDERID']
                        #js['freight'] = detail['SUBTOTAL'] if detail['SUBTOTAL'] != 0 else  detail['ORIGINALPRICE']
                        js['freight'] = detail['SUBTOTAL']
                    else:
                        salePrice = math.floor(int(detail["LISTPRICE"]) / int(detail["AMOUNT"]))
                        
                        jo['prodId'] = detail['PROD_ID']
                        jo['salePrice'] = salePrice
                        jo['saleCount'] = detail["AMOUNT"]
                        if detail['JOINFLG'] == 1:
                            jo['jointFlg'] = 'N'
                        else:
                            jo['jointFlg'] = 'Y'
                        jo['mallSoNo'] = detail['ORDERID']
                        jo['chkSalePriceFlg'] = 'N'

                        ja.append(jo)
                
                js['orderItems'] = ja

                save_json(main_data['TRANSACTIONID'], json.dumps(js))

                headers = {'Content-Type': 'application/json'}
                r = requests.post('http://192.168.100.10/api/saveOrderForYahoo.html', headers=headers, data=json.dumps(js))
                
                try:
                    save_response(main_data['TRANSACTIONID'], r)
                except:
                    logging.info('transfer_order_store:' + main_data['TRANSACTIONID'] + ' ' + str(r))

                if r.status_code == 200:
                    if r.json()['returnCode'] == '1000':
                        operations_dao.update_order_transfer_status(main_data['TRANSACTIONID'], 'B')
                    else:
                        batchfailnotify("Yahoo error order" + main_data['TRANSACTIONID'])
                        operations_dao.update_order_transfer_status(main_data['TRANSACTIONID'], 'C')
                else:
                    batchfailnotify("Yahoo error order" + main_data['TRANSACTIONID'])
                    operations_dao.update_order_transfer_status(main_data['TRANSACTIONID'], 'D')
                    
                operations_dao.commit_changes()


def query_order(datestr : str):
    with tracer.start_as_current_span("query_order_StoreDelivery"):
        # 超取
        r = yh_utils.order_query(datestr=datestr, position="1", count="1", order_type="StoreDelivery")
        cnt = total_count_by_transaction(r)

        if cnt > 0:
            for i in range(1,cnt,100):
                orders = yh_utils.order_query(datestr=datestr, position=i, count=100, order_type="StoreDelivery")
                master = order_master(orders['Response']['TransactionList']['Transaction'])
                detail = order_detail(master)

                save_order(master, detail)
                #transfer_order()

    with tracer.start_as_current_span("query_order_HomeDelivery"):
        # 宅配
        r = yh_utils.order_query(datestr=datestr, position="1", count="1", order_type="HomeDelivery")
        cnt = total_count_by_transaction(r)

        if cnt > 0:
            for i in range(1,cnt,100):
                orders = yh_utils.order_query(datestr=datestr, position=i, count=100, order_type="HomeDelivery")
                master = order_master(orders['Response']['TransactionList']['Transaction'])
                detail = order_detail(master)

                save_order(master, detail)
                #transfer_order()

@app.get('/query_cancel')
def query_cancel(sDay : int = 0):
    with tracer.start_as_current_span("query_cancel"):
        today = datetime.now()
        start =  today - timedelta(days=sDay * 1)
        end =  today - timedelta(days=sDay * 1 + 6)

        start_date = start.strftime("%Y/%m/%d")
        end_date = end.strftime("%Y/%m/%d")
        # 先查全部筆數
        r = yh_utils.order_cancel(datestr_s=start_date, datestr_e=end_date, position="1", count="1")
        cnt = total_count_by_transaction(r)

        if cnt > 0:
            for i in range(1,cnt,100):
                orders = yh_utils.order_cancel(datestr_s=start_date, datestr_e=end_date, position=i, count=100)
                master = orders['Response']['TransactionList']['Transaction']
                #logging.info('order_cancel:' + str(master))
    
                cancel_order(master)

@app.get('/order_query_yesterday')
async def order_query():
    with tracer.start_as_current_span("order_query_yesterday"):
        today = datetime.now()
        start =  today - timedelta(days=1)
        start_date = start.strftime("%Y/%m/%d")

        query_order(start_date)

@app.get('/order_query')
async def order_query(order_date: str = ""):
    with tracer.start_as_current_span("order_query"):
        if not order_date:
            order_date = datetime.today().strftime('%Y/%m/%d')

        query_order(order_date)

#if __name__ == '__main__':
settingLog()

#    datestr = ""
#    if len(sys.argv) > 1 and datestr == "":
#        datestr = sys.argv[1]

#    if not datestr:
#        datestr = datetime.today().strftime('%Y/%m/%d')
    #uvicorn.run(app, host='127.0.0.1', port=8000)
#    query_order(datestr)
    #query_cancel(0)
    #query_cancel(7)
    #query_cancel(14)
    #query_cancel(21)
    #transfer_order()