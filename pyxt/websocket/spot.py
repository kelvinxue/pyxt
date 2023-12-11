# -*- coding:utf-8 -*-
from typing import Optional
from xt_websocket import XTWebsocketClient


class SpotWebsocketStreamClient(XTWebsocketClient):
    def __init__(
            self,
            stream_url="wss://stream.xt.com",
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
            stream_url = stream_url + "/public"
        else:
            stream_url = stream_url + "/private"
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
        """Kline/Candlestick Streams

        The Kline/Candlestick Stream push updates to the current klines/candlestick every second.

        Stream Name: kline@{symbol},{interval}

        interval: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M

        Update Speed: 1000ms
        """
        stream_name = "kline@{},{}".format(symbol.lower(), interval)

        self.send_message_to_server(stream_name, action=action, id=id)

    def limit_depth(self, symbol: str, level=5, id=None, action=None):
        """
        limit Book Depth Streams
        levels: 5, 10, 20, 50
        Stream Names: depth@{symbol},{levels}
        Update Speed: 1000ms
        """
        self.send_message_to_server("depth@{},{}".format(symbol.lower(), level), id=id, action=action)

    def incremental_depth(self, symbol: str, id=None, action=None):
        """
        incremental Book Depth Streams
        Stream Names: depth_update@{symbol}
        Update Speed: 100ms
        """
        self.send_message_to_server("depth_update@{}".format(symbol.lower()), id=id, action=action)

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
