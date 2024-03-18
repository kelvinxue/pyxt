import requests
import json
import time
import hashlib
import hmac
import logging
from copy import deepcopy
from typing import List, Dict

logger = logging.getLogger('xt4')

"""
curl --location --request POST 'http://sapi.xt-dev.com/spot/v4/order' \
--header 'accept: */*' \
--header 'Content-Type: application/json' \
--header 'xt-validate-appkey: 626fa1c2-94bf-4559-a3f2-c62897bc392e' \
--header 'xt-validate-timestamp: 1641446237201' \
--header 'xt-validate-signature: f24b67d42283feb4b405c59146ecfca4a48f64bccc33c05c33bcc73edad6b4db' \
--header 'xt-validate-recvwindow: 5000' \
--header 'xt-validate-algorithms: HmacSHA256' \
--data-raw '{"symbol": "BTC_USDT","clientOrderId": "16559390087220001","side": "BUY","type": "LIMIT","timeInForce": "GTC","bizType": "SPOT","price": 20,"quantity": 0.001}'
"""


class Spot:
    """
        xt api接口
        异常处理：
            未获得内容，返回None
            获得内容返回状态码非200，
    """

    # def __init__(self, host, account=None, user_id=None, account_id=None, access_key=None, secret_key=None):
    def __init__(self, host, user_id=None, access_key=None, secret_key=None):
        self.host = host
        # self.account = account
        self.user_id = user_id
        # self.account_id = account_id
        self.access_key = access_key
        self.secret_key = secret_key
        # self.anonymous = not(account and account_id and access_key and secret_key)
        self.anonymous = not (access_key and secret_key)
        self.timeout = 10  # 默认超时时间
        self.headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
        }

    @classmethod
    def underscore_to_camelcase(cls, name):
        parts = name.split('_')
        return parts[0] + ''.join(x.title() for x in parts[1:])

    @classmethod
    def create_sign(cls, url, method, headers=None, secret_key=None, **kwargs):
        path_str = url
        query = kwargs.pop('params', None)
        data = kwargs.pop('data', None) or kwargs.pop('json', None)
        query_str = '' if query is None else '&'.join(
            [f"{key}={json.dumps(query[key]) if type(query[key]) in [dict, list] else query[key]}" for key in
             sorted(query)])  # 没有接口同时使用query和body
        body_str = json.dumps(data) if data is not None else ''
        y = '#' + '#'.join([i for i in [method, path_str, query_str, body_str] if i])
        x = '&'.join([f"{key}={headers[key]}" for key in sorted(headers)])
        sign = f"{x}{y}"
        # print(sign)
        return hmac.new(secret_key.encode('utf-8'), sign.encode('utf-8'),
                        hashlib.sha256).hexdigest().upper()

    def gen_auth_header(self, url, method, **kwargs):
        headers = {}
        headers['xt-validate-timestamp'] = str(int((time.time() - 30) * 1000))
        headers['xt-validate-appkey'] = self.access_key
        headers['xt-validate-recvwindow'] = '60000'
        headers['xt-validate-algorithms'] = 'HmacSHA256'
        headers['xt-validate-signature'] = self.create_sign(url, method, headers, str(self.secret_key), **kwargs)
        headers_ = deepcopy(self.headers)
        headers_.update(headers)
        return headers

    def auth_req(self, url, method='GET', **params):  # 登录签名才可请求的接口
        if self.anonymous:
            raise XtCodeError('未正确提供xt登录账号')
        headers = self.gen_auth_header(url, method, **params)
        kwargs = {'headers': headers, 'timeout': self.timeout}
        kwargs.update(params)
        resp = None
        res = None
        try:
            # print(params)
            resp = requests.request(method, self.host + url, **kwargs)
            resp.raise_for_status()
            res = resp.json()
        except Exception as e:
            info = f'url:{url} method:{method} params:{params} exception:{e}'
            logger.error(info, exc_info=True)
            raise XtHttpError(e, info=info, request={'url': url, 'method': method, 'params': params},
                              response=resp, res=res)
        if res['rc'] != 0:
            if res['mc'] == 'AUTH_103':  # 签名错误时，在日志中提供出ak，url, headers, 以便校验。
                info = f'url:{url} method:{method} params:{params} headers:{json.dumps(headers)}'
                logger.error(info)
                raise XtBusinessError(res, info)
            info = f'url:{url} method:{method} params:{params} res:{res}'
            logger.debug(info)
            raise XtBusinessError(res, info)
        return res

    def req(self, url, method, **params):  # 公开接口
        kwargs = {'headers': self.headers, 'timeout': self.timeout}
        kwargs.update(params)
        resp = None
        res = None

        try:
            resp = requests.request(method, self.host + url, **kwargs)
            resp.raise_for_status()
            res = resp.json()
        except Exception as e:
            info = f'url:{url} method:{method} params:{params} exception:{e}'
            logger.error(info, exc_info=True)
            raise XtHttpError(e, info=info, response=resp, res=res)
        return resp.json()

    def req_get(self, url, params=None, auth=None):  # 通过接口名判定是否需登录提供签名
        auth = auth if auth is not None else '/v4/public' not in url
        if auth:
            return self.auth_req(url, "GET", params=params)
        return self.req(url, "GET", params=params)

    def req_post(self, url, params=None, auth=None):  # post请求 只支持json数据
        auth = auth if auth is not None else '/v4/public' not in url
        if auth:
            return self.auth_req(url=url, method="POST", json=params)
        return self.req(url=url, method="POST", json=params)

    def req_delete(self, url, params=None, json=None, auth=None):  # delete 请求 只支持json数据
        auth = auth if auth is not None else '/v4/public' not in url
        if auth:
            return self.auth_req(url, "DELETE", params=params, json=json)
        return self.req(url, "DELETE", params=params, json=json)

    # -----------------------------------市场数据-----------------------------------

    def get_time(self) -> int:
        """
            获取服务器时间戳 https://xt-com.github.io/xt4-api/#market_cn1serverInfo
        :return: 1662435658062  # datetime.datetime.fromtimestamp(1662435658062/1000)
        """
        return int(self.req_get("/v4/public/time")['result']['serverTime'])

    def get_symbol_config(self, symbol: str = None, symbols: list = None) -> dict:
        """
            获取交易对信息 https://xt-com.github.io/xt4-api/#market_cn2symbol
        :param symbol: 市场名 如btc_usdt
        :param symbols: 市场名数组
        :return: {}
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        elif symbols:
            params['symbols'] = symbols
        res = self.req_get("/v4/public/symbol", params=params)
        return res['result']['symbols']
        # return {s['symbol']: s for s in res['result']['symbols']}

    def get_depth(self, symbol: str, limit: int = None) -> dict:
        """
            获取深度数据 https://xt-com.github.io/xt4-api/#market_cn10depth
        :param symbol:
        :param limit: 数量 默认50 1到500
        :return: {
    "timestamp": 1662445330524,  //时间戳
    "lastUpdateId": 137333589606963580,  //最后更新记录
    "bids": [     //买盘([?][0]=价位;[?][1]=挂单量)
      [
        "200.0000",   //价位
        "0.996000"    //挂单量
      ],
      [
        "100.0000",
        "0.001000"
      ],
      [
        "20.0000",
        "10.000000"
      ]
    ],
    "asks": []    //卖盘([?][0]=价位;[?][1]=挂单量)
  }
        """
        params = {'symbol': symbol}
        if limit:
            params['limit'] = limit
        res = self.req_get('/v4/public/depth', params)
        return res['result']

    def get_kline(self, symbol: str, interval: str, start_time: int = None, end_time: int = None, limit: int = 100):
        """
            获取k线数据
        :param symbol:
        :param interval: 	K线类型 ,1m;3m;5m;15m;30m;1h;2h;4h;6h;8h;12h;1d;3d;1w;1M eg:1m
        :param start_time:
        :param end_time:
        :param limit: 限制数量 默认100
        :return: [
    {
      "t": 1662601014832,  //开盘时间(time)
      "o": "30000", //开盘价(open)
      "c": "32000",  //收盘价(close)
      "h": "35000",  //最高价(high)
      "l": "25000",  //最低价(low)
      "q": "512",  //成交量(quantity)
      "v": "15360000"    //成交额(volume)
    }
  ]
        """
        params = {'symbol': symbol, 'interval': interval}
        if start_time:
            params['start_time'] = start_time
        if end_time:
            params['end_time'] = end_time
        if limit:
            params['limit'] = limit
        res = self.req_get('/v4/public/kline', params)
        return res['result']

    def get_trade_recent(self, symbol, limit: int = None):
        """
            查询近期成交列表
        :param symbol:
        :param limit: 数量 默认200 取值1到1000
        :return:[
    {
      "i": 0,   //ID
      "t": 0,   //成交时间(time)
      "p": "string", //成交价(price)
      "q": "string",  //成交量(quantity)
      "v": "string",  //成交额(volume)
      "b": true   //方向(buyerMaker)
    }
  ]
        """
        params = {'symbol': symbol}
        if limit:
            params['limit'] = limit
        res = self.req_get('/v4/public/trade/recent', params)
        return res['result']

    def get_trade_history(self, symbol, limit: int = None, from_id: int = None):
        """
            查询历史成交列表
        :param symbol:
        :param limit: 数量，默认200，取值1到1000
        :param from_id: 起始id,eg 6216559590087220004
        :return:[
    {
      "i": 0,   //ID
      "t": 0,   //成交时间(time)
      "p": "string", //成交价(price)
      "q": "string",  //成交量(quantity)
      "v": "string",  //成交额(volume)
      "b": true   //方向(buyerMaker)
    }
  ]
        """
        params = {'symbol': symbol}
        if limit:
            params['limit'] = limit
        if from_id:
            params['fromId'] = from_id
        res = self.req_get('/v4/public/trade/history', params)
        return res['result']

    def get_tickers(self, symbol: str = None, symbols: list = None) -> dict:
        """

        :param symbol:
        :param symbols:
        :return:    [
            {
              "s": "btc_usdt",   //交易对(symbol)
              "p": "9000.0000",   //价格(price)
              "t": 1661856036925   //时间(time)
            }
          ]
        {
            <symbol>: {'price': float, }
        }
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        elif symbols:
            params['symbols'] = symbols
        res = self.req_get('/v4/public/ticker/price', params)
        return res['result']

    def get_tickers_book(self, symbol: str = None, symbols: list = None):
        """
            获取最优挂单ticker
        :param symbol:
        :param symbols:
        :return:  [
    {
      "s": "btc_usdt",  //交易对(symbol)
      "ap": null,  //asks price(卖一价)
      "aq": null,  //asks qty(卖一量)
      "bp": null,   //bids price(买一价)
      "bq": null    //bids qty(买一量)
    }
  ]
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        elif symbols:
            params['symbols'] = symbols
        res = self.req_get('/v4/public/ticker/book', params)
        return res['result']

    def get_tickers_24h(self, symbol: str = None, symbols: list = None):
        """
            获取24h统计ticker
        :param symbol:
        :param symbols:
        :return:  [
    {
      "s": "btc_usdt",   //交易对(symbol)
      "cv": "0.0000",   //价格变动(change value)
      "cr": "0.00",     //价格变动百分比(change rate)
      "o": "9000.0000",   //最早一笔(open)
      "l": "9000.0000",   //最低(low)
      "h": "9000.0000",   //最高(high)
      "c": "9000.0000",   //最后一笔(close)
      "q": "0.0136",      //成交量(quantity)
      "v": "122.9940"    //成交额(volume)
    }
  ]
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        elif symbols:
            params['symbols'] = symbols
        res = self.req_get('/v4/public/ticker/24h', params)
        return res['result']

    # -----------------------------------订单-----------------------------------

    def get_order(self, order_id=None, client_order_id=None) -> dict:
        """
            单笔获取
        :param order_id:
        :param client_order_id:
        :return:
        """
        params = {}
        if order_id:
            params['orderId'] = order_id
        elif client_order_id:
            params['clientOrderId'] = client_order_id
        res = self.req_get('/v4/order', params)
        return res['result']

    def order(self, symbol, side, type, biz_type='SPOT', time_in_force='GTC', client_order_id=None, price=None,
              quantity=None, quote_qty=None):
        """
            https://xt-com.github.io/xt4-api/#order_cnorderPost
            symbol	string	true		交易对
            clientOrderId	string	false		客户端ID(最长32位)
            side	string	true		买卖方向  BUY-买,SELL-卖
            type	string	true		订单类型  LIMIT-现价,MARKET-市价
            timeInForce	string	true		有效方式 GTC, FOK, IOC, GTX
            bizType	string	true		业务类型  SPOT-现货, LEVER-杠杆
            price	number	false		价格。现价必填; 市价不填
            quantity	number	false		数量。现价必填；市价按数量下单时必填
            quoteQty	number	false		金额。现价不填；市价按金额下单时必填
        :return:
        """
        params = {'symbol': symbol, 'side': side, 'type': type, 'bizType': biz_type,
                  'timeInForce': time_in_force}
        if client_order_id:
            params['clientOrderId'] = client_order_id
        if price:
            params['price'] = price
        if quote_qty:
            params['quoteQty'] = quote_qty
        if quantity:
            if type == "MARKET" and side == "BUY" and quote_qty is None:
                params['quoteQty'] = quantity * price
            else:
                params['quantity'] = quantity
        res = self.req_post("/v4/order", params)
        return res['result']

    def cancel_order(self, order_id):
        """
            单笔撤单
        :param order_id:
        :return:
        """
        res = self.req_delete(f'/v4/order/{order_id}')
        return res['result']

    def get_open_orders(self, symbol=None, page=1, page_size=300) -> list:
        """
            查询当前挂单
        :param symbol:
        :param page:
        :param page_size:
        :return:
        """
        params = {'symbol': symbol, 'page': page, 'pageSize': page_size, 'bizType': 'SPOT'}
        res = self.req_get("/v4/open-order", params)
        return res['result']

    def cancel_open_orders(self, symbol=None, biz_type='SPOT', side=None):
        """
            撤销当前挂单
        :param symbol:
        :param biz_type:
        :param side:
        :return:
        """
        params = {'bizType': biz_type}
        if symbol:
            params['symbol'] = symbol
        if side:
            params['side'] = side
        res = self.req_delete('/v4/open-order', json=params)
        return res['result']

    def cancel_orders(self, order_ids: list) -> None:
        """

        :param order_ids: 必须小于300
        :return:
        """
        params = {'orderIds': order_ids}
        res = self.req_delete("/v4/batch-order", json=params)
        return res['result']

    def batch_order(self, data, batch_id=None) -> List[Dict]:
        """
            批量挂单 一次至多100
        :param data: [{}]
        :param batch_id:
        :return:
        """
        """
            https://xt-com.github.io/xt4-api/#order_cnbatchOrderPost
            参考order方法，组装data这样的字典数组
            symbol, side, type, biz_type='SPOT', time_in_force='GTC', client_order_id=None, price=None, quantity=None, quote_qty=None
        :param data: {
  "clientBatchId": "51232",
  "items": [
    {
      "symbol": "BTC_USDT",
      "clientOrderId": "16559590087220001",
      "side": "BUY",
      "type": "LIMIT",
      "timeInForce": "GTC", # GTC,IOC,FOK,GTX 选一
      "bizType": "SPOT",
      "price": 40000,
      "quantity": 2,
      "quoteQty": 80000
    }
  ]
}
        :return: [{'index': 0, 'clientOrderId': 'batch_order1663857797612_1', 'orderId': '143259835441769153', 'rejected': False, 'reason': None}]
        """
        items = []
        for item in data:
            # item_ = {transfer_hump(k): v for k, v in item.items()}
            items.append(item)
        params = {"clientBatchId": batch_id, "items": items}
        res = self.req_post("/v4/batch-order", params)
        return res['result']

    def get_batch_orders(self, order_ids: list) -> list:
        """
        :param market: 交易对
        :param data:[161889118535516, 161889118535517] 不超过150个 否则可能触发get请求过大
        :return: 参考get_order 结果为字典数组
        """
        # if
        params = {'orderIds': ','.join(order_ids)}
        res = self.req_get("/v4/batch-order", params)
        return res['result']

    def get_all_orders(self, market: str):
        res = []
        orders_all = self.get_open_orders(market)
        order_ids_all = [i['orderId'] for i in orders_all]
        page = 0
        page_size = 150
        now_order_ids = order_ids_all[page_size * 0: (page + 1) * page_size]
        while now_order_ids:
            item = self.get_batch_orders(now_order_ids)
            res.extend(item)
            page += 1
            now_order_ids = order_ids_all[page_size * page: (page + 1) * page_size]
        return res

    def get_history_orders(self, symbol=None, biz_type=None, side=None, type=None, order_id=None, from_id=None,
                           direction=None, limit=None, start_time=None, end_time=None, hidden_canceled=None):
        """
            历史订单查询
        :param symbol:
        :param biz_type:
        :param side:
        :param type:
        :param order_id:
        :param from_id:
        :param direction:
        :param limit:
        :param start_time:
        :param end_time:
        :param hidden_canceled:
        :return:
        """
        vars = locals()
        params = {self.underscore_to_camelcase(k): v for k, v in vars.items() if k != 'self' and v is not None}

        res = self.req_get('/v4/history-order', params)
        return res['result']

    def get_trade(self, symbol=None, biz_type=None, side=None, type=None, order_id=None, from_id=None, direction=None,
                  limit=None, start_time=None, end_time=None):
        """
            默认一次查询20条数据
        :param symbol:
        :param biz_type:
        :param side:
        :param type:
        :param order_id:
        :param from_id:
        :param direction:
        :param limit:
        :param start_time:
        :param end_time:
        :return: {'hasPrev': False, 'hasNext': True, 'items': [
        {'symbol': 'people_usdt', 'tradeId': '139968422023832642', 'orderId': '139968399989795073', 'orderSide': 'BUY',
        'orderType': 'LIMIT', 'bizType': 'SPOT', 'time': 1663073072298, 'price': '1.031929', 'quantity': '100.0000',
        'quoteQty': '103.192900', 'baseCurrency': 'people', 'quoteCurrency': 'usdt', 'fee': '0.2',
        'feeCurrency': 'people', 'takerMaker': 'MAKER'}
        ]}}

        """
        vars = locals()
        params = {self.underscore_to_camelcase(k): v for k, v in vars.items() if k != 'self' and v is not None}
        res = self.req_get('/v4/trade', params)
        return res['result']

    # -----------------------------------资产-----------------------------------
    def get_currencies(self):
        """
            获取币种信息
        :return:
        """
        res = self.req_get("/v4/public/currencies")
        return res['result']['currencies']

    def balance(self, currency):
        """

        :param currency: 币种列表,逗号分隔，eg: usdt,btc
        :return:
        """
        params = {'currency': currency}
        res = self.req_get('/v4/balance', params)
        return res['result']

    def balances(self, currencies=None):
        """

        :param currencies: 币种列表,逗号分隔，eg: usdt,btc
        :return:
        """
        params = {'currencies': ','.join(currencies)} if currencies else None
        res = self.req_get('/v4/balances', params)
        return res['result']

    def listen_key(self):
        """
        @return:
        """
        res = self.req_post('/v4/ws-token', auth=True)
        return res['result']

    def transfer(self, from_account, to_account, currency, amount):
        """
        BizType
        Status	Description
        SPOT	现货
        LEVER	杠杠
        FINANCE	理财
        FUTURES_U	合约u本位
        FUTURES_C	合约币本位

        @param from_account: BizType
        @param to_account: BizType
        @param currency:币种名称必须全部小写（usdt，btc）
        @param amount:
        @return:
        """

        params = {
            "bizId": int(time.time() * 1000),
            "from": from_account,
            "to": to_account,
            "currency": currency,
            "amount": amount
        }

        res = self.req_post("/v4/balance/transfer", params, auth=True)
        return res['result']


import json
import requests


class XtCodeError(Exception):
    pass


class XtHttpError(Exception):
    PARAMS_DIC = {
        'request': '请求',
        'response': '响应',
        'res': '结果',
    }

    def __init__(self, *args, **kwargs):
        """

        :param args:
        :param kwargs 自定义字段，一般用法如下:
        :info 描述
        :request 请求对象 字典 {url, method,params}
        :response 响应对象 requests.response
        :res 响应对象组装json
        """
        self.args = args
        self.exception = args[0]
        self.exception_type = type(self.exception)
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._err_data = kwargs
        self.init()

    def init(self):
        """
            提取一些常见异常，设置错误消息提示，便于程序员处理
        :return:
        """
        import traceback
        self.trace_info = traceback.format_exc()

    @property
    def desc(self):
        return f'XT服务异常:str{self.exception}'

    @property
    def err_str(self):
        res = []
        for k, v in self._err_data.items():
            try:
                s = self.PARAMS_DIC.get(k, k) + ':'
                if k == 'response' and type(v) is requests.Response:
                    v_ = {'status_code': v.status_code, 'content': str(v.content)}
                else:
                    v_ = v
                s += json.dumps(v_)
                res.append(s)
            except Exception as e:
                # logger.debug(e)
                pass
        return '\n'.join(res)

    def __str__(self):
        return f'XT接口异常:{self.info}\n详细数据:{self.err_str}\n异常信息:\n{self.desc}'


XT_MES_ERRORS = {
    '0': '客户端异常',
    'SUCCESS': '成功',
    'FAILURE': '失败',
    'not exist': '目标不存在',
    'AUTH_001': '缺少请求头 xt-validate-appkey',
    'AUTH_002': '缺少请求头 xt-validate-timestamp',
    'AUTH_003': '缺少请求头 xt-validate-recvwindow',
    'AUTH_004': '错误的请求头 xt-validate-recvwindow',
    'AUTH_005': '缺少请求头 xt-validate-algorithms',
    'AUTH_006': '错误的请求头 xt-validate-algorithms',
    'AUTH_007': '缺少请求头 xt-validate-signature',
    'AUTH_101': 'ApiKey不存在',
    'AUTH_102': 'ApiKey未激活',
    'AUTH_103': '签名错误',
    'AUTH_104': '非绑定IP请求',
    'AUTH_105': '报文过时',
    'AUTH_106': '超出apikey权限',
    'ORDER_001': '平台拒单',
    'ORDER_002': '资金不足',
    'ORDER_003': '交易对暂停交易',
    'ORDER_004': '禁止交易',
    'ORDER_005': '订单不存在',
    'ORDER_F0101': '触发价格过滤器-最小值',
    'ORDER_F0102': '触发价格过滤器-最大值',
    'ORDER_F0103': '触发价格过滤器-步进值',
    'ORDER_F0201': '触发数量过滤器-最小值',
    'ORDER_F0202': '触发数量过滤器-最大值',
    'ORDER_F0203': '触发数量过滤器-步进值',
    'ORDER_F0301': '触发金额过滤器-最小值',
    'ORDER_F0401': '触发开盘保护滤器',
    'ORDER_F0501': '触发限价保护滤器',
    'ORDER_F0601': '触发市价保护滤器',
    'ORDER_F0701': '过多的未完成订单',
    'ORDER_F0801': '过多未完成计划委托',
}


class XtBusinessError(Exception):
    def __init__(self, data, info: str = None):
        self.return_code = data.get('rc', '0')
        self.message_code = data.get('mc', '0')
        self.source = data
        self.info = info

    @property
    def desc(self):
        return XT_MES_ERRORS.get(self.message_code, f'未知异常码:{self.message_code}')

    def __str__(self):
        return f"XT ERROR. RC:{self.return_code} MC: {self.message_code} DESC:{self.desc} INFO: {self.info} SOURCE:{json.dumps(self.source)}"


if __name__ == "__main__":
    xt = Spot(host="http://sapi.xt.com", access_key='',
              secret_key='')
    print(xt.listen_key())
