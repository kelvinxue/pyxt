# -*- coding:utf-8 -*-
import time
import json
import hashlib
import hmac
import requests


class Perp:
    def __init__(self, host, access_key, secret_key, *args, **kwargs):
        self.host = host
        self.__access_key = access_key
        self.__secret_key = secret_key
        self.timeout = kwargs["timeout"] if kwargs.get("timeout", None) else 10

    @staticmethod
    def _create_sign(access_key, secret_key, path: str, bodymod: str = None, params: dict = None):
        header = dict()
        apikey = access_key
        secret = secret_key
        timestamp = str(int(time.time() * 1000))
        if bodymod == 'application/x-www-form-urlencoded':
            if params:
                params = dict(sorted(params.items(), key=lambda e: e[0]))
                message = "&".join([f"{arg}={params[arg]}" for arg in params])
                signkey = f"xt-validate-appkey={apikey}&xt-validate-timestamp={timestamp}#{path}#{message}"
            else:
                signkey = f"xt-validate-appkey={apikey}&xt-validate-timestamp={timestamp}#{path}"
        elif bodymod == 'application/json':
            if params:
                message = json.dumps(params)
                signkey = f"xt-validate-appkey={apikey}&xt-validate-timestamp={timestamp}#{path}#{message}"
            else:
                signkey = f"xt-validate-appkey={apikey}&xt-validate-timestamp={timestamp}#{path}"
        else:
            assert False, f"not support this bodymod:{bodymod}"

        digestmodule = hashlib.sha256
        sign = hmac.new(secret.encode("utf-8"), signkey.encode("utf-8"), digestmod=digestmodule).hexdigest()
        header.update({
            'validate-signversion': "2",
            'xt-validate-appkey': apikey,
            'xt-validate-timestamp': timestamp,
            'xt-validate-signature': sign,
            'xt-validate-algorithms': "HmacSHA256"
        })
        return header

    @staticmethod
    def _fetch(method, url, params=None, body=None, data=None, headers=None, timeout=30, **kwargs):
        """
        Create a HTTP request.
           Args:
               method: HTTP request method. `GET` / `POST` / `PUT` / `DELETE`
               url: Request url.
               params: HTTP query params.
               body: HTTP request body, string or bytes format.
               data: HTTP request body, dict format.
               headers: HTTP request header.
               timeout: HTTP request timeout(seconds), default is 30s
               kwargs:
                   proxy: HTTP proxy.

           Return:
               code: HTTP response code.
               success: HTTP response data. If something wrong, this field is None.
               error: If something wrong, this field will holding a Error information, otherwise it's None.

           Raises:
               HTTP request exceptions or response data parse exceptions. All the exceptions will be captured and return
               Error information.
        """
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers, timeout=timeout, **kwargs)
            elif method == "POST":
                response = requests.post(url, params=params, data=body, json=data, headers=headers,
                                         timeout=timeout, **kwargs)
            elif method == "PUT":
                response = requests.put(url, params=params, data=body, json=data, headers=headers,
                                        timeout=timeout, **kwargs)
            elif method == "DELETE":
                response = requests.delete(url, params=params, data=body, json=data, headers=headers,
                                           timeout=timeout, **kwargs)
            else:
                error = "http method error!"
                return None, None, error
        except Exception as e:
            print("method:", method, "url:", url, "headers:", headers, "params:", params, "body:", body,
                  "data:", data, "Error:", e)
            return None, None, e
        code = response.status_code
        if code not in (200, 201, 202, 203, 204, 205, 206):
            text = response.text
            request_url = response.request.url
            print("method:", method, "url:", request_url, "headers:", headers, "params:", params, "body:", body,
                  "data:", data, "code:", code, "result:", text)
            return code, None, text
        try:
            result = response.json()
        except:
            result = response.text
            print("response data is not json format!")
            print("method:", method, "url:", url, "headers:", headers, "params:", params, "body:", body,
                  "data:", data, "code:", code, "result:", json.dumps(result))
        print("method:", method, "url:", url, "headers:", headers, "params:", params, "body:", body,
              "data:", data, "code:", code)
        return code, result, None

    def get_market_config(self, symbol):
        """
        @param symbol:
        @return: market config info
        """
        params = {"symbol": symbol}
        url = self.host + "/future/market" + '/v1/public/symbol/detail'
        code, success, error = self._fetch(method="GET", url=url, params=params, timeout=self.timeout)
        return code, success, error

    def get_all_pair_info(self):
        """
        :return: all pairs info
        """
        params = {}
        url = self.host + "/future/market" + '/v1/public/symbol/coins'
        code, success, error = self._fetch(method="GET", url=url, params=params, timeout=self.timeout)
        return code, success, error

    def get_funding_rate(self, symbol):
        """
        :return:funding rate
        """
        params = {"symbol": symbol}
        url = self.host + "/future/market" + '/v1/public/q/funding-rate'
        code, success, error = self._fetch(method="GET", url=url, params=params, timeout=self.timeout)
        return code, success, error

    def get_agg_tiker(self, symbol):
        """
        :return:agg ticker
        """
        params = {"symbol": symbol}
        url = self.host + "/future/market" + '/v1/public/q/agg-ticker'
        code, success, error = self._fetch(method="GET", url=url, params=params, timeout=self.timeout)
        return code, success, error

    def get_book_ticker(self, symbol):
        """
        :return:book ticker
        """
        params = {"symbol": symbol}
        url = self.host + "/future/market" + '/v1/public/q/ticker/book'
        code, success, error = self._fetch(method="GET", url=url, params=params, timeout=self.timeout)
        return code, success, error

    def get_last_price(self, symbol, length):
        """
        :return: last trade record
        """
        params = {"symbol": symbol, "num": length}
        url = self.host + "/future/market" + '/v1/public/q/deal'
        code, success, error = self._fetch(method="GET", url=url, params=params, timeout=self.timeout)
        return code, success, error

    def get_depth(self, symbol, depth):
        """
        :return:market depth
        """
        params = {"symbol": symbol, "level": depth}
        url = self.host + "/future/market" + '/v1/public/q/depth'
        code, success, error = self._fetch(method="GET", url=url, params=params, timeout=self.timeout)
        return code, success, error

    def get_mark_price(self, symbol):
        """
        :return:mark price
        """
        params = {"symbol": symbol}
        url = self.host + "/future/market" + '/v1/public/q/symbol-mark-price'
        code, success, error = self._fetch(method="GET", url=url, params=params, timeout=self.timeout)
        return code, success, error

    def get_k_line(self, symbol, interval, start_time=None, end_time=None, limit=None):
        """
        :param symbol:
        :param interval: interval string true 1m;5m;15m;30m;1h;4h;1d;1w
        :param start_time:
        :param end_time:
        :param limit:
        :return:
        """
        params = {
            "symbol": symbol,
            "interval": interval,
        }
        if start_time:
            params.update({"startTime": start_time})
        if end_time:
            params.update({"endTime": end_time})
        if limit:
            params.update({"limit": limit})

        url = self.host + "/future/market" + '/v1/public/q/kline'
        code, success, error = self._fetch(method="GET", url=url, params=params, timeout=self.timeout)
        return code, success, error

    def get_account_capital(self):
        """
        :return: account capital
        """
        bodymod = "application/json"
        path = "/future/user" + '/v1/balance/list'
        url = self.host + path
        params = {}
        header = self._create_sign(self.__access_key, self.__secret_key, path=path, bodymod=bodymod,
                                   params=params)
        code, success, error = self._fetch(method="GET", url=url, headers=header, data=params, timeout=self.timeout)
        return code, success, error

    def get_listen_key(self):
        """
        :return: listen_key
        """
        bodymod = "application/json"
        path = "/future/user" + '/v1/user/listen-key'
        url = self.host + path
        params = {}
        header = self._create_sign(self.__access_key, self.__secret_key, path=path, bodymod=bodymod,
                                   params=params)
        code, success, error = self._fetch(method="GET", url=url, headers=header, data=params, timeout=self.timeout)
        return code, success, error

    def send_order(self, symbol, amount, order_side, order_type, position_side, price=None):
        """
        :return: send order
        """
        params = {
            "orderSide": order_side,
            "orderType": order_type,
            "origQty": amount,
            "positionSide": position_side,
            "symbol": symbol
        }
        if price:
            params["price"] = price

        bodymod = "application/json"
        path = "/future/trade" + '/v1/order/create'
        url = self.host + path
        params = dict(sorted(params.items(), key=lambda e: e[0]))
        header = self._create_sign(self.__access_key, self.__secret_key, path=path, bodymod=bodymod,
                                   params=params)
        code, success, error = self._fetch(method="POST", url=url, headers=header, data=params, timeout=self.timeout)
        return code, success, error

    def send_batch_order(self, order_list):
        """
        :return: send batch order
        """
        params = order_list

        bodymod = "application/json"
        path = "/future/trade" + "/v2/order/create-batch"
        url = self.host + path
        header = self._create_sign(self.__access_key, self.__secret_key, path=path, bodymod=bodymod,
                                   params=params)
        header.pop("validate-signversion")
        code, success, error = self._fetch(method="POST", url=url, headers=header, data=params, timeout=self.timeout)
        return code, success, error

    def get_history_order(self, symbol=None, direction=None, oid=None, limit=None, start_time=None, end_time=None):
        """
        :return: get_history_order
        Error
        """
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/trade" + '/v1/order/list-history'
        url = self.host + path
        params = {}
        if symbol:
            params["symbol"] = symbol
        if direction:
            params["direction"] = direction
        if oid:
            params["id"] = oid
        if limit:
            params["limit"] = limit
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        header = self._create_sign(self.__access_key, self.__secret_key, path=path, bodymod=bodymod,
                                   params=params)
        code, success, error = self._fetch(method="GET", url=url, headers=header, params=params, timeout=self.timeout)
        return code, success, error

    def get_position(self, symbol):
        """
        get_position
        :return:
        """
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/user" + '/v1/position/list'
        url = self.host + path
        params = {
            "symbol": symbol,
        }
        header = self._create_sign(self.__access_key, self.__secret_key, path=path, bodymod=bodymod,
                                   params=params)
        header["Content-Type"] = "application/x-www-form-urlencoded"
        code, success, error = self._fetch(method="GET", url=url, headers=header, params=params, timeout=self.timeout)
        return code, success, error

    def cancel_order(self, order_id):
        """
        cancel_order
        :return:
        """
        bodymod = "application/json"
        path = "/future/trade" + '/v1/order/cancel'
        url = self.host + path
        params = {
            "orderId": order_id
        }
        header = self._create_sign(self.__access_key, self.__secret_key, path=path, bodymod=bodymod,
                                   params=params)
        code, success, error = self._fetch(method="POST", url=url, headers=header, data=params, timeout=self.timeout)
        return code, success, error

    def cancel_batch_order(self, order_id_list: list):
        """
        cancel_batch_order
        :return:
        {'returnCode': 0, 'msgInfo': 'success', 'error': None, 'result': True}
        """
        bodymod = "application/json"
        path = "/future/trade" + '/v1/order/cancel-batch'
        url = self.host + path
        params = {
            "orderIds": str(order_id_list)
        }
        header = self._create_sign(self.__access_key, self.__secret_key, path=path, bodymod=bodymod,
                                   params=params)
        code, success, error = self._fetch(method="POST", url=url, headers=header, data=params, timeout=self.timeout)
        return code, success, error

    def cancel_all_order(self, symbol):
        """
        :return: cancel_all_order
        """
        bodymod = "application/json"
        path = "/future/trade" + '/v1/order/cancel-all'
        url = self.host + path
        params = {
            "symbol": symbol
        }
        header = self._create_sign(self.__access_key, self.__secret_key, path=path, bodymod=bodymod,
                                   params=params)
        code, success, error = self._fetch(method="POST", url=url, headers=header, data=params, timeout=self.timeout)
        return code, success, error

    def get_order_id(self, order_id):
        """
        :return: get_order_id
        {'returnCode': 0, 'msgInfo': 'success', 'error': None, 'result': {'orderId': '137699581654889152', 'clientOrderId': None, 'symbol': 'btc_usdt', 'orderType': 'LIMIT', 'orderSide': 'BUY', 'positionSide': 'LONG', 'timeInForce': 'GTC', 'closePosition': False, 'price': '18500', 'origQty': '10', 'avgPrice': '0', 'executedQty': '0', 'marginFrozen': '18.5', 'triggerProfitPrice': None, 'triggerStopPrice': None, 'sourceId': None, 'forceClose': False, 'closeProfit': None, 'state': 'CANCELED', 'createdTime': 1662532138730}}
        """
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/trade" + '/v1/order/detail'
        url = self.host + path
        params = {
            "orderId": order_id
        }
        header = self._create_sign(self.__access_key, self.__secret_key, path=path, bodymod=bodymod,
                                   params=params)
        code, success, error = self._fetch(method="GET", url=url, headers=header, params=params, timeout=self.timeout)
        return code, success, error

    def set_account_leverage(self, leverage, position_side, symbol):
        """
        :return: set_account_leverage
        """
        bodymod = "application/json"
        path = "/future/user" + '/v1/position/adjust-leverage'
        url = self.host + path
        params = {
            "leverage": leverage,
            "positionSide": position_side,
            "symbol": symbol
        }
        params = dict(sorted(params.items(), key=lambda e: e[0]))
        header = self._create_sign(self.__access_key, self.__secret_key, path=path, bodymod=bodymod,
                                   params=params)
        code, success, error = self._fetch(method="POST", url=url, headers=header, data=params, timeout=self.timeout)
        return code, success, error

    def get_account_order(self, state):
        """
        :return: get_account_order
        """
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/trade" + '/v1/order/list'
        url = self.host + path
        params = {
            "state": state,
        }
        header = self._create_sign(self.__access_key, self.__secret_key, path=path, bodymod=bodymod,
                                   params=params)
        code, success, error = self._fetch(method="GET", url=url, headers=header, params=params, timeout=self.timeout)
        return code, success, error


if __name__ == '__main__':
    symbol_xt = 'eth_usdt'
    quantity = 1
    host = "http://fapi.xt-qa.com"
    access_key = ""
    secret_key = ""
    xt_perp = Perp(host, access_key, secret_key)
    # 1.账户资金
    # res = xt_perp.get_account_capital()
    # print(res)
    # 2.listen-key
    # res = xt_perp.get_listen_key()
    # print(res)
    # 3.下单
    # res = xt_perp.send_order(symbol=symbol_xt, amount=quantity, order_side='BUY', price=2000, order_type='LIMIT',
    #                          position_side='LONG')
    # print(res)
    # 4.撤单
    # res = xt_perp.cancel_order(order_id="319725440900455488")
    # print(res)
    # 5.批量下单
    # res = xt_perp.send_batch_order(
    #     order_list=[
    #         {"symbol": "eth_usdt", "origQty": "1", "orderSide": "BUY", "price": "2000", "positionSide": "LONG",
    #          "orderType": "LIMIT"}])
    # print(res)
    # 6.批量撤单
    # res = xt_perp.cancel_batch_order(["319626610863430720"])
    # print(res)
    # 7.查询账户订单
    # res = xt_perp.get_account_order("NEW")
    # print(res)
    # 8.查询订单状态 318212657052603520
    # res = xt_perp.get_order_id("318212657052603520")
    # print(res)
    # 10.设置杠杆
    # res = xt_perp.set_account_leverage(leverage=1,symbol="eth_usdt",position_side="LONG")
    # print(res)
    # 11.查询历史订单
    res = xt_perp.get_history_order()
    print(res)
    # 12.全部撤单
    # res = xt_perp.cancel_all_order(symbol="eth_usdt")
    # print(res)
    # 13.获取仓位
    # res = xt_perp.get_position(symbol="eth_usdt")
    # print(res)
