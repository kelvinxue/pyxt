import requests
import json
import urllib
from urllib import parse
import hashlib
import hmac
import time
import traceback
from http.client import IncompleteRead
from requests.exceptions import ChunkedEncodingError

TIMEOUT = 5


def http_get_request(url, params, add_to_headers=None):
    headers = {
        "Content-type": 'application/x-www-form-urlencoded'
    }
    if add_to_headers:
        headers.update(add_to_headers)
    postdata = urllib.parse.urlencode(params)
    try:
        response = requests.get(url, postdata, headers=headers, timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            print('++++++++++++==response==+++++++++++++')
            print(f"response.headers:{response.headers}")
            print(f"response.request{response.request}")
            print(f"response.json{response.json}")
            print('++++++++++++==reuqest==+++++++++++++')
            print(f"request.headers:{headers}")
            print(f"request.params:{params}")
            print(f"request.url:{response.url}")
            print(f"code != 200 {response.text}")
            return None
    except IncompleteRead:
        print("httpGet failed, detail is:%s" % traceback.format_exc())
    except ChunkedEncodingError:
        print("httpGet failed, detail is:%s" % traceback.format_exc())
    except Exception as e:
        print("httpGet failed, detail is:%s" % traceback.format_exc())
        raise e


def http_post_request(url, params, add_to_headers=None):
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
    }
    if add_to_headers:
        headers.update(add_to_headers)
    try:
        response = requests.post(url, params=params, headers=headers, timeout=TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            print('++++++++++++==response==+++++++++++++')
            print(f"response.headers:{response.headers}")
            print(f"response.request{response.request}")
            print(f"response.json{response.json}")
            print(f"response.text{response.text}")
            print('++++++++++++==reuqest==+++++++++++++')
            print(f"request.headers:{headers}")
            print(f"request.params:{params}")
            print(f"request.url:{response.url}")
            print(f"code != 200 {response.text}")
            return None
    except IncompleteRead:
        print("httpGet failed, detail is:%s" % traceback.format_exc())
    except ChunkedEncodingError:
        print("httpGet failed, detail is:%s" % traceback.format_exc())
    except Exception as e:
        print("httpPost failed, detail is:%s" % traceback.format_exc())
        raise e


def create_sign(access_key, secret_key, path: str, method: str, bodymod: str = None, params: dict = {},
                algorithms='HmacSHA256'):
    apikey = access_key
    secret = secret_key
    timestamp = str(int(time.time() * 1000))
    # timestamp = "1647849140713"
    if bodymod == 'x-www-form-urlencoded' or bodymod is {} or params is not {}:
        params = dict(sorted(params.items(), key=lambda e: e[0]))
        message = "&".join([f"{arg}={params[arg]}" for arg in params])
    elif bodymod == 'json':
        params = params
        message = "&".join([f"{arg}={params[arg]}" for arg in params])
    else:
        print(f'不支持的bodymod参数类型')

    if method == 'get' and len(params.keys()) > 0:
        signkey = f'xt-validate-appkey={apikey}&xt-validate-timestamp={timestamp}#{path}#{message}'
    elif method == 'get' and len(params.keys()) == 0:
        signkey = f'xt-validate-appkey={apikey}&xt-validate-timestamp={timestamp}#{path}'
    elif method == 'post' and len(params.keys()) > 0:
        signkey = f'xt-validate-appkey={apikey}&xt-validate-timestamp={timestamp}#{path}#{message}'
    elif method == 'post' and len(params.keys()) == 0:
        signkey = f'xt-validate-appkey={apikey}&xt-validate-timestamp={timestamp}#{path}'
    else:
        print(f'不支持的请求方式--->{method}')

    if algorithms == 'HmacSHA256':
        digestmodule = hashlib.sha256
    elif algorithms == 'HmacMD5':
        digestmodule = hashlib.md5
    elif algorithms == 'HmacSHA1':
        digestmodule = hashlib.sha1
    elif algorithms == 'HmacSHA224':
        digestmodule = hashlib.sha224
    elif algorithms == 'HmacSHA384':
        digestmodule = hashlib.sha384
    elif algorithms == 'HmacSHA512':
        digestmodule = hashlib.sha512
    else:
        print(f'不支持加密算法--->{algorithms}，默认加密算法类--->HmacSHA256')

    sign = hmac.new(secret.encode("utf-8"), signkey.encode("utf-8"), digestmod=digestmodule).hexdigest()
    header = {
        'xt-validate-appkey': apikey,
        'xt-validate-timestamp': timestamp,
        'xt-validate-signature': sign,
        'xt-validate-algorithms': algorithms,
        'xt-validate-recvwindow': "10000000000"
    }
    return header


def api_key_get(path, url, access_key, secret_key, bodymod, params):
    header = create_sign(access_key=access_key, secret_key=secret_key, path=path, method="get", bodymod=bodymod,
                         params=params)
    res = http_get_request(url=url, params=params, add_to_headers=header)
    return res


def api_key_post(path, url, access_key, secret_key, bodymod, params):
    header = create_sign(access_key=access_key, secret_key=secret_key, path=path, method="post",
                         bodymod=bodymod,
                         params=params)
    res = http_post_request(url=url, params=params, add_to_headers=header)
    return res


class Future:
    def __init__(self, host, access_key, secret_key):
        self.__url = host
        self.__access_key = access_key
        self.__secret_key = secret_key

    def get_market_config(self, symbol):
        """
        symbol:
        :return:获取单个交易对的配置信息
        """
        params = {"symbol": symbol}
        url = self.__url + "/future/market" + '/v1/public/symbol/detail'
        return http_get_request(url, params=params)

    def get_all_pair_info(self):
        """
        :return:获取交易对币种
        """
        url = self.__url + "/future/market" + '/v1/public/symbol/list'
        return http_get_request(url, params="")

    def get_funding_rate(self, symbol):
        """
        :return:获取资金费率
        """
        params = {"symbol": symbol}
        url = self.__url + "/future/market" + '/v1/public/q/funding-rate'
        return http_get_request(url, params=params)

    def get_agg_tiker(self, symbol):
        """
        :return:返回聚合行情
        """
        params = {"symbol": symbol}
        url = self.__url + "/future/market" + '/v1/public/q/agg-ticker'
        return http_get_request(url, params=params)

    def get_book_ticker(self, symbol):
        """
        :return:返回ticker book
        """
        params = {"symbol": symbol}
        url = self.__url + "/future/market" + '/v1/public/q/ticker/book'
        return http_get_request(url, params=params)

    def get_last_price(self, symbol, length):
        """
        :return:获取最近成交记录
        """
        params = {"symbol": symbol, "num": length}
        url = self.__url + "/future/market" + '/v1/public/q/deal'
        return http_get_request(url, params=params)

    def get_depth(self, symbol, depth):
        """
        :return:获取深度数据
        """
        params = {"symbol": symbol, "level": depth}
        url = self.__url + "/future/market" + '/v1/public/q/depth'
        return http_get_request(url, params=params)

    def get_account_capital(self):
        """
        :return:获取账户资金
        """
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/user" + '/v1/balance/list'
        url = self.__url + path
        return api_key_get(path=path, url=url, access_key=self.__access_key, secret_key=self.__secret_key,
                           bodymod=bodymod, params={})

    def send_order(self, symbol, price, amount, order_side, order_type, position_side, client_id=None):
        """
        :return:获取账户资金
        """
        params = {"orderSide": order_side,
                  "orderType": order_type,
                  "origQty": amount,
                  "positionSide": position_side,
                  "symbol": symbol,
                  "price": price}
        if client_id:
            params["clientOrderId"] = client_id

        bodymod = "application/x-www-form-urlencoded"
        path = "/future/trade" + '/v1/order/create'
        url = self.__url + path
        return api_key_post(path=path, url=url, access_key=self.__access_key, secret_key=self.__secret_key,
                            bodymod=bodymod, params=params)

    def send_batch_order(self, order_list: list):
        """
        :return:获取账户资金
        """
        params = {"list": str(order_list)}

        bodymod = "x-www-form-urlencoded"
        path = "/future/trade" + '/v1/order/create-batch'
        url = self.__url + path
        return api_key_post(path=path, url=url, access_key=self.__access_key, secret_key=self.__secret_key,
                            bodymod=bodymod, params=params)

    def get_history_order(self):
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/trade" + '/v1/order/list-history'
        url = self.__url + path
        return api_key_get(path=path, url=url, access_key=self.__access_key, secret_key=self.__secret_key,
                           bodymod=bodymod, params={})

    def get_account_order(self, symbol, state, page, size):
        """
        state:
        订单状态 NEW：新建订单（未成交）；
        PARTIALLY_FILLED：部分成交；
        FILLED：全部成交；CANCELED：用户撤销；
        REJECTED：下单失败；EXPIRED：已过期；
        UNFINISHED：未完成；HISTORY：（历史）
        """
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/trade" + '/v1/order-entrust/list'
        url = self.__url + path
        params = {
            "symbol": symbol,
            "state": state,
            "page": page,
            "size": size
        }
        return api_key_get(path=path, url=url, access_key=self.__access_key, secret_key=self.__secret_key,
                           bodymod=bodymod, params=params)

    def get_position(self, symbol):
        """
        获取持仓信息
        :return:
        """
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/user" + '/v1/position/list'
        url = self.__url + path
        params = {
            "symbol": symbol,
        }
        return api_key_get(path=path, url=url, access_key=self.__access_key, secret_key=self.__secret_key,
                           bodymod=bodymod, params=params)

    def cancel_order(self, order_id):
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/trade" + '/v1/order/cancel'
        url = self.__url + path
        params = {
            "orderId": order_id
        }
        return api_key_post(path=path, url=url, access_key=self.__access_key, secret_key=self.__secret_key,
                            bodymod=bodymod, params=params)

    def cancel_batch_order(self, order_id_list):
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/trade" + '/v1/order/cancel-batch'
        url = self.__url + path
        params = {
            "orderIds": str(order_id_list)
        }
        return api_key_post(path=path, url=url, access_key=self.__access_key, secret_key=self.__secret_key,
                            bodymod=bodymod, params=params)

    def cancel_all_order(self):
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/trade" + '/v1/order/cancel-all'
        url = self.__url + path
        params = {}
        return api_key_post(path=path, url=url, access_key=self.__access_key, secret_key=self.__secret_key,
                            bodymod=bodymod, params=params)

    def get_mark_price(self, symbol, size):
        """
        :return:
        """
        params = {"symbol": symbol, "size": size}
        url = self.__url + "/future/market" + '/v1/public/q/symbol-mark-price'
        return http_get_request(url, params=params)

    def get_index_price(self, symbol, size):
        """
        :param symbol:
        :param size:
        :return:
        """
        params = {"symbol": symbol, "size": size}
        url = self.__url + "/future/market" + '/v1/public/q/symbol-index-price'
        return http_get_request(url, params=params)

    def get_order_id(self, order_id, ci):
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/api" + '/v1/order/detail'
        url = self.__url + path
        params = {
            "orderId": order_id
        }
        return api_key_get(path=path, url=url, access_key=self.__access_key, secret_key=self.__secret_key,
                           bodymod=bodymod, params=params)

    def get_batch_order_id(self, order_id_list: list):
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/trade" + '/v1/order/list-by-ids'
        url = self.__url + path
        order_id_query = ",".join(order_id_list)
        params = {
            "ids": order_id_query
        }
        return api_key_post(path=path, url=url, access_key=self.__access_key, secret_key=self.__secret_key,
                            bodymod=bodymod, params=params)

    def set_account_leverage(self, leverage, position_side, symbol):
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/user" + '/v1/position/adjust-leverage'
        url = self.__url + path
        params = {
            "leverage": leverage,
            "positionSide": position_side,
            "symbol": symbol
        }
        return api_key_post(path=path, url=url, access_key=self.__access_key, secret_key=self.__secret_key,
                            bodymod=bodymod, params=params)

    def set_merge_position(self, symbol, merge_amount=None):
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/user" + '/v1/position/merge'
        url = self.__url + path
        params = {
            "symbol": symbol
        }
        if merge_amount:
            params["mergeAmount"] = merge_amount
        return api_key_post(path=path, url=url, access_key=self.__access_key, secret_key=self.__secret_key,
                            bodymod=bodymod, params=params)

    def get_k_line(self, symbol, interval, start_time=None, end_time=None, limit=None):
        """
        :param symbol:
        :param interval: interval string true  时间间隔 1m;5m;15m;30m;1h;4h;1d;1w
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

        url = self.__url + "/future/market" + '/v1/public/q/kline'
        return http_get_request(url, params=params)


if __name__ == '__main__':
    url = "https://fapi.xt.com"
    access_key = ""
    secret_key = ""

    xt = Future(url, access_key, secret_key)
    a = xt.get_account_capital()
    print(a)