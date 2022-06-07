import cx_Oracle
from .oracle_utils import OracleUtils

class YahooApiDao(OracleUtils):
    READY_TO_SHIP_STATUS = 'READY_TO_SHIP'

    def __enter__(self):
        self.initiate_connection()
        print('initiating connection')
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print('terminating connection')
        self.terminate_connection()

    def execute_custom_query(self, query):
        result = None
        try:
            result = self.execute_query(query)
            self.con.commit()
            return result

        except cx_Oracle.DatabaseError as e:
            self.con.rollback()
            print(e)
            raise e

    def execute_custom_non_query(self, query):
        try:
            self.execute_non_query(query)
            self.con.commit()

        except Exception as e:
            self.con.rollback()
            raise e

    def get_orders_to_transfer(self, status_flg = 'A'):
        sql = """
            SELECT TRANSACTIONID, STATUSFLG, PAYTYPE, SHIPPINGTYPE, STORETYPE 
                FROM 
            APP_YAHOO_OD_MAIN WHERE STATUSFLG = '%s' 
        """
        
        self.execute_query(query=sql % (status_flg),  as_dict=True)

    def get_order_detail_to_transfer(self, TRANSACTIONID = ''):
        sql = """
            SELECT 
                OI.ORDERID AS ORDERID, 
                OD.RECEIVERNAME AS RECEIVERNAME, 
                OD.RECEIVERMOBILE AS RECEIVERMOBILE, 
                OD.RECEIVERPHONE AS RECEIVERPHONE, 
                OD.RECEIVERADDRESS AS RECEIVERADDRESS, 
                OD.RECEIVERZIPCODE AS RECEIVERZIPCODE, 
                OI.PRODUCTID AS PRODUCTID, 
                OI.PRODUCTTYPE AS PRODUCTTYPE, 
                OI.PRODUCTNAME AS PRODUCTNAME, 
                OI.AMOUNT AS AMOUNT, 
                OI.ORIGINALPRICE AS ORIGINALPRICE, 
                OI.LISTPRICE AS LISTPRICE, 
                OI.SUBTOTAL AS SUBTOTAL, 
                OI.JOINFLG AS JOINFLG, 
                (SELECT TP.CITY_ID FROM TOWN_PAMT TP WHERE TP.ZIP = OD.RECEIVERZIPCODE AND ROWNUM = 1) AS CITY_ID, 
                (SELECT TP.TOWN_ID FROM TOWN_PAMT TP WHERE TP.ZIP = OD.RECEIVERZIPCODE AND ROWNUM = 1) AS TOWN_ID, 
                (SELECT P.PROD_ID FROM APP_YAHOO_PRODUCT P WHERE P.PROD_ID_YHO = SUBSTR(OI.PRODUCTID,0,(LENGTH(OI.PRODUCTID)-2))) AS PROD_ID, 
                OD.ORDERSTATUS AS ORDERSTATUS 
                FROM APP_YAHOO_OD_DETAIL OI, APP_YAHOO_OD_MASTER OD 
            WHERE 
                OI.ORDERID = OD.ORDERID 
                AND OD.ORDERSTATUS = 'NEW' 
                AND OI.TRANSACTIONID = '%s'
        """
        
        self.execute_query(query=sql % (TRANSACTIONID),  as_dict=True)

    def is_order_detail_exists(self, TRANSACTIONID, ORDERID, PRODUCTID):
        sql = """
            SELECT
                *
            FROM
                APP_YAHOO_OD_DETAIL
            WHERE
                TRANSACTIONID = '%s' AND ORDERID = '%s' AND PRODUCTID = '%s'
        """

        return self.is_record_exists(sql % (TRANSACTIONID, ORDERID, PRODUCTID))

    def is_order_master_exists(self, TRANSACTIONID, ORDERID):
        sql = """
            SELECT
                *
            FROM
                APP_YAHOO_OD_MASTER
            WHERE
                TRANSACTIONID = '%s' AND ORDERID = '%s'
        """

        return self.is_record_exists(sql % (TRANSACTIONID, ORDERID))


    def is_order_main_exists(self, TRANSACTIONID):
        sql = """
            SELECT
                *
            FROM
                APP_YAHOO_OD_MAIN
            WHERE
                TRANSACTIONID = '%s'
        """

        return self.is_record_exists(sql % TRANSACTIONID)

    def insert_order_main(self, master, detail):
        sql = f"""INSERT INTO APP_YAHOO_OD_MAIN(
                    TRANSACTIONID, 
                    BUYERNAME, 
                    BUYERPHONE, 
                    ISACTIVITY, 
                    ISUSECOUPON, 
                    PAYTYPE, 
                    INSTALLMENT, 
                    SHIPPINGTYPE, 
                    STORETYPE, 
                    STORESHIPPINGTYPE, 
                    TRANSACTIONREMARK, 
                    TRANSACTIONPRICE, 
                    CREATEDATE, 
                    MODIFYDATE, 
                    STATUSFLG)
                VALUES('{master['@Id']}',
                        '{master['_BuyerName']}',
                        '{master['_BuyerPhone']}',
                        '{master['IsActivity']}',
                        '{master['IsUseCoupon']}',
                        '{master['PayType']}',
                        '{master['Installment']}',
                        '{master['ShippingType']}',
                        '{master['StoreType']}',
                        '{master['_StoreShippingType']}',
                        '{master['_TransactionRemark']}',
                        {master['TransactionPrice']},
                        sysdate,
                        sysdate,
                        'A')"""

        try:
            self.execute_non_query(sql)
        except Exception as e:
            self.con.rollback()
            raise e

    def update_order_transfer_status(self, TRANSACTIONID, STATUSFLG):
        sql = """
            UPDATE APP_YAHOO_OD_MAIN SET STATUSFLG = '%s', MODIFYDATE = SYSDATE WHERE TRANSACTIONID = '%s'
        """

        try:
            self.execute_non_query(sql % (STATUSFLG, TRANSACTIONID))
        except Exception as e:
            self.con.rollback()
            raise e

    def update_order_main(self, master, detail):
        sql = f"""UPDATE APP_YAHOO_OD_MAIN SET
                    BUYERNAME = '{master['_BuyerName']}',
                    BUYERPHONE = '{master['_BuyerPhone']}',
                    ISACTIVITY = '{master['IsActivity']}',
                    ISUSECOUPON = '{master['IsUseCoupon']}',
                    PAYTYPE = '{master['PayType']}',
                    INSTALLMENT = '{master['Installment']}',
                    SHIPPINGTYPE = '{master['ShippingType']}',
                    STORETYPE = '{master['StoreType']}',
                    STORESHIPPINGTYPE = '{master['_StoreShippingType']}',
                    TRANSACTIONREMARK = '{master['_TransactionRemark']}',
                    TRANSACTIONPRICE = {master['TransactionPrice']},
                    MODIFYDATE = sysdate
                WHERE TRANSACTIONID = '{master['@Id']}'"""

        try:
            self.execute_non_query(sql)
        except Exception as e:
            self.con.rollback()
            raise e

    def insert_order_master(self, master, receiver, detail):
        sql = f"""INSERT INTO APP_YAHOO_OD_MASTER(
                    TransactionId, 
                    OrderId,
                    ReceiverName, 
                    ReceiverPhone, 
                    ReceiverMobile, 
                    ReceiverZipcode, 
                    ReceiverAddress, 

                    OrderStatus, 
                    OrderStatusDesc, 

                    TransferDate, 
                    LastShippingDate, 
                    OrderShippingDate, 
                    OrderCloseDate, 
                    BuyerConfirmDate, 
                    EntryAccountDate, 
                    PickingDate, 
                    OrderPackageDate, 
                    LastDeliveryDate, 

                    OrderShippingId, 

                    InvoiceNo, 
                    InvoiceDate, 

                    DeliverType, 
                    OrderNote,
                    Createdate,
                    Modifydate,
                    Statusflg)
                VALUES('{master['@Id']}',
                        '{detail['@Id']}',

                        '{receiver['_ReceiverName']}',
                        '{receiver['_ReceiverPhone']}',
                        '{receiver['_ReceiverMobile']}',
                        '{receiver['_ReceiverZipcode']}',
                        '{receiver['_ReceiverAddress']}',

                        '{detail['OrderStatus']}',
                        '{detail['_OrderStatusDesc']}',

                        TO_DATE('{detail['TransferDate'][:10]}', 'YYYY/MM/DD'),
                        TO_DATE('{detail['LastShippingDate'][:10]}', 'YYYY/MM/DD'),
                        TO_DATE('{detail['OrderShippingDate'][:10]}', 'YYYY/MM/DD'),
                        TO_DATE('{detail['OrderCloseDate'][:10]}', 'YYYY/MM/DD'),
                        TO_DATE('{detail['BuyerConfirmDate'][:10]}', 'YYYY/MM/DD'),
                        TO_DATE('{detail['EntryAccountDate'][:10]}', 'YYYY/MM/DD'),
                        TO_DATE('{detail['PickingDate'][:10]}', 'YYYY/MM/DD'),
                        TO_DATE('{detail['OrderPackageDate'][:10]}', 'YYYY/MM/DD'),
                        TO_DATE('{detail['LastDeliveryDate'][:10]}', 'YYYY/MM/DD'),

                        '{detail['_OrderShippingId']}',

                        '{detail['InvoiceNo']}',
                        TO_DATE('{detail['InvoiveDate'][:10]}', 'YYYY/MM/DD'),
                        
                        '{detail['_DeliverType']}',
                        '{detail['_OrderNote']}',
                        sysdate,
                        sysdate,
                        'A'
                        )"""

        try:
            self.execute_non_query(sql)
        except Exception as e:
            self.con.rollback()
            raise e

    def update_order_master(self, master, receiver, detail):
        sql = f"""UPDATE APP_YAHOO_OD_MASTER SET
                    ReceiverName = '{receiver['_ReceiverName']}',
                    ReceiverPhone = '{receiver['_ReceiverPhone']}',
                    ReceiverMobile = '{receiver['_ReceiverMobile']}',
                    ReceiverZipcode = '{receiver['_ReceiverZipcode']}',
                    ReceiverAddress = '{receiver['_ReceiverAddress']}',
                    TransferDate = TO_DATE('{detail['TransferDate'][:10]}', 'YYYY/MM/DD'),
                    LastShippingDate = TO_DATE('{detail['LastShippingDate'][:10]}', 'YYYY/MM/DD'),
                    OrderShippingDate = TO_DATE('{detail['OrderShippingDate'][:10]}', 'YYYY/MM/DD'),
                    OrderCloseDate = TO_DATE('{detail['OrderCloseDate'][:10]}', 'YYYY/MM/DD'),
                    BuyerConfirmDate = TO_DATE('{detail['BuyerConfirmDate'][:10]}', 'YYYY/MM/DD'),
                    EntryAccountDate = TO_DATE('{detail['EntryAccountDate'][:10]}', 'YYYY/MM/DD'),
                    PickingDate = TO_DATE('{detail['PickingDate'][:10]}', 'YYYY/MM/DD'),
                    OrderPackageDate = TO_DATE('{detail['OrderPackageDate'][:10]}', 'YYYY/MM/DD'),
                    InvoiceNo = '{detail['InvoiceNo']}',
                    InvoiceDate = TO_DATE('{detail['InvoiveDate'][:10]}', 'YYYY/MM/DD'),
                    LastDeliveryDate = TO_DATE('{detail['LastDeliveryDate'][:10]}', 'YYYY/MM/DD'),
                    OrderStatus = '{detail['OrderStatus']}',
                    DeliverType = '{detail['_DeliverType']}',
                    OrderNote = '{detail['_OrderNote']}',
                    OrderStatusDesc = '{detail['_OrderStatusDesc']}',
                    OrderShippingId = '{detail['_OrderShippingId']}',
                    MODIFYDATE = sysdate
                WHERE TRANSACTIONID = '{master['@Id']}' AND ORDERID = '{detail['@Id']}'"""

        try:
            self.execute_non_query(sql)
        except Exception as e:
            self.con.rollback()
            raise e

    def update_order_master_cancel(self, master, detail):
        sql = f"""UPDATE APP_YAHOO_OD_MASTER SET
                    OrderStatus = '{detail['OrderStatus']}',
                    OrderStatusDesc = '{detail['_OrderStatusDesc']}',
                    StatusFlg = 'B',
                    MODIFYDATE = sysdate
                WHERE TRANSACTIONID = '{master['@Id']}' AND ORDERID = '{detail['@Id']}'"""

        try:
            self.execute_non_query(sql)
        except Exception as e:
            self.con.rollback()
            raise e

    def insert_order_detail(self, master, product, detail):
        sql = f"""INSERT INTO APP_YAHOO_OD_DETAIL(
                    TransactionId, 
                    OrderId,
                    ProductId, 
                    SaleType, 
                    ProductType, 
                    Amount, 
                    OriginalPrice, 
                    ListPrice, 
                    Subtotal, 
                    TaxType, 
                    CustomizedProductId, 
                    PRODUCTNAME,
                    Spec, 
                    JoinFlg,
                    createDate,
                    modifyDate,
                    statusFlg
                    )
                VALUES('{master['@Id']}',
                        '{detail['@Id']}',
                        '{product['@Id']}',
                        '{product['SaleType']}',
                        '{product['ProductType']}',
                        {product['Amount']},
                        {product['OriginalPrice']},
                        {product['ListPrice']},
                        {product['Subtotal']},
                        '{product['TaxType']}',
                        '{product['_CustomizedProductId']}',
                        '{product['_ProductName']}',
                        '{product['_Spec']}',
                        '1',
                        sysdate,
                        sysdate,
                        'A'
                        )"""
                      

        try:
            self.execute_non_query(sql)
        except Exception as e:
            self.con.rollback()
            raise e

    def update_order_detail(self, master, product, detail):
        sql = f"""UPDATE APP_YAHOO_OD_DETAIL SET
                    ProductId = '{product['@Id']}',
                    SaleType = '{product['SaleType']}',
                    ProductType = '{product['ProductType']}',
                    Amount = {product['Amount']},
                    OriginalPrice = {product['OriginalPrice']},
                    ListPrice = {product['ListPrice']},
                    Subtotal = {product['Subtotal']},
                    TaxType = '{product['TaxType']}',
                    CustomizedProductId = '{product['_CustomizedProductId']}',
                    PRODUCTNAME = '{product['_ProductName']}',
                    Spec = '{product['_Spec']}',
                    MODIFYDATE = sysdate
                WHERE TRANSACTIONID = '{master['@Id']}' AND ORDERID = '{detail['@Id']}' AND PRODUCTID = '{product['@Id']}'"""

        try:
            self.execute_non_query(sql)
        except Exception as e:
            self.con.rollback()
            raise e

    def order_detail_store(self, master, detail):
        try:
            for order in master:
                order_detail =  [x for x in detail if x['@Id'] == order['@Id']][0]

                od = []
                if not isinstance(order_detail['SuccessList']['OrderList']['Order'], (list)):
                    od.append(order_detail['SuccessList']['OrderList']['Order'])
                else:
                    od = order_detail['SuccessList']['OrderList']['Order']
               

                for _detail in od:
                    _product = _detail['OrderProductList']['Product']
                    if self.is_order_detail_exists(order['@Id'], _detail['@Id'], _product['@Id']):
                        self.update_order_detail(order, _product, _detail)
                    else:
                        self.insert_order_detail(order, _product, _detail)
        except Exception as e:
            self.con.rollback()
            raise e

    def order_master_store(self, master, detail):
        try:
            for order in master:
                order_detail =  [x for x in detail if x['@Id'] == order['@Id']][0]
                receiver = order_detail['Receiver']
           
                od = []
                if not isinstance(order_detail['SuccessList']['OrderList']['Order'], (list)):
                    od.append(order_detail['SuccessList']['OrderList']['Order'])
                else:
                    od = order_detail['SuccessList']['OrderList']['Order']
                    
                for _detail in od:
                    if self.is_order_master_exists(order['@Id'], _detail['@Id']):
                        self.update_order_master(order, receiver, _detail)
                    else:
                        self.insert_order_master(order, receiver, _detail)
        except Exception as e:
            self.con.rollback()
            raise e

    def order_master_cancel(self, master):
        try:
            for order in master:
         
                od = []
                if not isinstance(order['Order'], (list)):
                    od.append(order['Order'])
                else:
                    od = order['Order']
                    
                for _detail in od:
                    if self.is_order_master_exists(order['@Id'], _detail['@Id']):
                        self.update_order_master_cancel(order, _detail)
                    else:
                        continue
                        #raise Exception(f'Order {order["@Id"]} not found')
        except Exception as e:
            self.con.rollback()
            raise e

    def order_main_store(self, master, detail):
        try:
            for order in master:
                order_detail =  [x for x in detail if x['@Id'] == order['@Id']][0]
                if self.is_order_main_exists(order['@Id']):
                    self.update_order_main(order, order_detail)
                else:
                    self.insert_order_main(order, order_detail)
        except Exception as e:
            self.con.rollback()
            raise e


    def execute_and_retrieve_data(self, sql):
        result = None
        try:
            result = self.execute_query(sql)
            self.con.commit()

            return result

        except cx_Oracle.DatabaseError as e:
            self.con.rollback()
            raise e

    def is_record_exists(self, sql):
        result = None
        try:
            self.execute_query(sql, as_dict=True)
            #self.con.commit()

            result = self.fetchall()
            return len(result) > 0

        except cx_Oracle.DatabaseError as e:
            #self.con.rollback()
            raise e
