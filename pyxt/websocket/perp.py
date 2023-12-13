# -*- coding:utf-8 -*-
from typing import Optional
from pyxt.websocket.xt_websocket import XTWebsocketClient


class PerpWebsocketStreamClient(XTWebsocketClient):
    def __init__(
            self,
            stream_url="wss://fstream.xt.com",
            on_message=None,
            on_open=None,
            on_close=None,
            on_error=None,
            on_ping=None,
            on_pong=None,
            is_auth=False,
            timeout=None,
            proxies: Optional[dict] = None,
    ):
        if not is_auth:
            stream_url = stream_url + "/ws/market"
        else:
            stream_url = stream_url + "/ws/user"
        super().__init__(
            stream_url,
            on_message=on_message,
            on_open=on_open,
            on_close=on_close,
            on_error=on_error,
            on_ping=on_ping,
            on_pong=on_pong,
            timeout=timeout,
            proxies=proxies,
        )

    def trade(self, symbol: str, id=None, action=None, **kwargs):
        """
        Trade Streams
        Stream Name: trade@{symbol}
        Update Speed: Real-time
        """
        stream_name = "trade@{}".format(symbol.lower())
        self.send_message_to_server(stream_name, action=action, id=id)

    def kline(self, symbol: str, interval: str, id=None, action=None):
        """
        Kline/Candlestick Streams

        The Kline/Candlestick Stream push updates to the current klines/candlestick every second.

        Stream Name: kline@{symbol},{interval}

        interval: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M

        Update Speed: 1000ms
        """
        stream_name = "kline@{},{}".format(symbol.lower(), interval)
        self.send_message_to_server(stream_name, action=action, id=id)

    def depth(self, symbol: str, level=5, id=None, action=None):
        """
        limit Book Depth Streams
        levels: 50
        Stream Names: depth@{symbol},{levels}
        Update Speed: 1000ms
        """
        stream_name = "depth@{},{}".format(symbol.lower(), level)
        self.send_message_to_server(stream_name, id=id, action=action)

    def depth_update(self, symbol: str, id=None, action=None):
        """
        incremental Book Depth Streams
        Stream Names: depth_update@{symbol}
        Update Speed: 100ms
        """
        stream_name = "depth_update@{}".format(symbol.lower())
        self.send_message_to_server(stream_name, id=id, action=action)

    def ticker(self, symbol=None, id=None, action=None, **kwargs):
        """
        Stream Name: ticker@{symbol}

        Update Speed: 1000ms
        """
        stream_name = "ticker@{}".format(symbol.lower())
        self.send_message_to_server(stream_name, action=action, id=id)

    def all_ticker(self, id=None, action=None):
        """
        Stream Name: tickers

        Update Speed: 1000ms
        """

        stream_name = "tickers"
        self.send_message_to_server(stream_name, action=action, id=id)

    def agg_tickers(self, id=None, action=None):
        """
        Stream Name: agg_tickers

        Update Speed: 1000ms
        """
        stream_name = "agg_tickers"
        self.send_message_to_server(stream_name, action=action, id=id)

    def index_price(self, symbol, id=None, action=None):
        """
        Stream Name: index_price

        Update Speed: 1000ms
        """
        stream_name = "index_price@{}".format(symbol.lower())
        self.send_message_to_server(stream_name, action=action, id=id)

    def mark_price(self, symbol, id=None, action=None):
        """
        Stream Name: mark_price

        Update Speed: 1000ms
        """
        stream_name = "mark_price@{}".format(symbol.lower())
        self.send_message_to_server(stream_name, action=action, id=id)

    def fund_rate(self, symbol, id=None, action=None):
        """
        Stream Name: fund_rate

        Update Speed: 60s
        """
        stream_name = "fund_rate@{}".format(symbol.lower())
        self.send_message_to_server(stream_name, action=action, id=id)

    def user_balance(self, listen_key, id=None, action=None):
        """
        :return: balance
        """
        stream_name = "balance@{}".format(listen_key)
        self.send_message_to_server(stream_name, action=action, id=id)

    def user_position(self, listen_key, id=None, action=None):
        """
        :return: position
        """
        stream_name = "position@{}".format(listen_key)
        self.send_message_to_server(stream_name, action=action, id=id)

    def user_trade(self, listen_key, id=None, action=None):
        """
        :return: trade
        """
        stream_name = "trade@{}".format(listen_key)
        self.send_message_to_server(stream_name, action=action, id=id)

    def user_order(self, listen_key, id=None, action=None):
        """
        :return: order
        """
        stream_name = "order@{}".format(listen_key)
        self.send_message_to_server(stream_name, action=action, id=id)

    def user_notify(self, listen_key, id=None, action=None):
        """
        :return: notify
        """
        stream_name = "notify@{}".format(listen_key)
        self.send_message_to_server(stream_name, action=action, id=id)
