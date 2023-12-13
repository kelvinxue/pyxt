# -*- coding:utf-8 -*-

import time
import json
import threading

import logging
from typing import Optional
from urllib.parse import urlparse
from websocket import (
    ABNF,
    create_connection,
    WebSocketException,
    WebSocketConnectionClosedException,
    WebSocketTimeoutException,
)

logger = logging.getLogger(__name__)


def get_timestamp():
    return int(time.time() * 1000)


def parse_proxies(proxies: dict):
    """Parse proxy url from dict, only support http and https proxy, not support socks5 proxy"""
    proxy_url = proxies.get("http") or proxies.get("https")
    if not proxy_url:
        return {}

    parsed = urlparse(proxy_url)
    return {
        "http_proxy_host": parsed.hostname,
        "http_proxy_port": parsed.port,
        "http_proxy_auth": (parsed.username, parsed.password)
        if parsed.username and parsed.password
        else None,
    }


class XTSocketManager(threading.Thread):
    def __init__(
            self,
            stream_url,
            on_message=None,
            on_open=None,
            on_close=None,
            on_error=None,
            on_ping=None,
            on_pong=None,
            timeout=None,
            proxies: Optional[dict] = None,
    ):
        threading.Thread.__init__(self)
        self.stream_url = stream_url
        self.on_message = on_message
        self.on_open = on_open
        self.on_close = on_close
        self.on_ping = on_ping
        self.on_pong = on_pong
        self.on_error = on_error
        self.timeout = timeout

        self._proxy_params = parse_proxies(proxies) if proxies else {}

        self.create_ws_connection()

    def create_ws_connection(self):
        logger.debug(
            f"Creating connection with WebSocket Server: {self.stream_url}, proxies: {self._proxy_params}",
        )

        self.ws = create_connection(
            self.stream_url, timeout=self.timeout, **self._proxy_params
        )
        logger.debug(
            f"WebSocket connection has been established: {self.stream_url}, proxies: {self._proxy_params}",
        )
        self._callback(self.on_open)

    def run(self):
        self.read_data()

    def send_message(self, message):
        logger.debug(f"Sending message to XT WebSocket Server: {message}")
        self.ws.send(message)

    def ping(self):
        self.ws.ping()

    def read_data(self):
        data = ""
        while True:
            try:
                op_code, frame = self.ws.recv_data_frame(True)
            except WebSocketException as e:
                if isinstance(e, WebSocketConnectionClosedException):
                    logger.error("Lost websocket connection")
                elif isinstance(e, WebSocketTimeoutException):
                    logger.error("Websocket connection timeout")
                else:
                    logger.error("Websocket exception: {}".format(e))
                raise e
            except Exception as e:
                logger.error("Exception in read_data: {}".format(e))
                raise e

            self._handle_data(op_code, frame, data)
            self._handle_heartbeat(op_code, frame)

            if op_code == ABNF.OPCODE_CLOSE:
                logger.warn(
                    "CLOSE frame received, closing websocket connection"
                )
                self._callback(self.on_close)
                break

    def _handle_heartbeat(self, op_code, frame):
        if op_code == ABNF.OPCODE_PING:
            self._callback(self.on_ping, frame.data)
            self.ws.pong("")
            logger.debug("Received Ping; PONG frame sent back")
        elif op_code == ABNF.OPCODE_PONG:
            logger.debug("Received PONG frame")
            self._callback(self.on_pong)

    def _handle_data(self, op_code, frame, data):
        if op_code == ABNF.OPCODE_TEXT:
            data = frame.data.decode("utf-8")
            self._callback(self.on_message, data)

    def close(self):
        if not self.ws.connected:
            logger.warn("Websocket already closed")
        else:
            self.ws.send_close()
        return

    def _callback(self, callback, *args):
        if callback:
            try:
                callback(self, *args)
            except Exception as e:
                logger.error("Error from callback {}: {}".format(callback, e))
                if self.on_error:
                    self.on_error(self, e)


class XTWebsocketClient:
    ACTION_SUBSCRIBE = "subscribe"
    ACTION_UNSUBSCRIBE = "unsubscribe"

    def __init__(
            self,
            stream_url,
            on_message=None,
            on_open=None,
            on_close=None,
            on_error=None,
            on_ping=None,
            on_pong=None,
            timeout=None,
            proxies: Optional[dict] = None,
    ):
        self.socket_manager = self._initialize_socket(
            stream_url,
            on_message,
            on_open,
            on_close,
            on_error,
            on_ping,
            on_pong,
            timeout,
            proxies,
        )

        # start the thread
        self.socket_manager.start()
        logger.debug("XT WebSocket Client started.")

    def _initialize_socket(
            self,
            stream_url,
            on_message,
            on_open,
            on_close,
            on_error,
            on_ping,
            on_pong,
            timeout,
            proxies,
    ):
        return XTSocketManager(
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

    def _single_stream(self, stream):
        if isinstance(stream, str):
            return True
        elif isinstance(stream, list):
            return False
        else:
            raise ValueError("Invalid stream name, expect string or array")

    def send(self, message: dict):
        self.socket_manager.send_message(json.dumps(message))

    def send_message_to_server(self, message, action=None, id=None, listen_key=None):
        if not id:
            id = get_timestamp()

        if action != self.ACTION_UNSUBSCRIBE:
            return self.subscribe(message, id=id, listen_key=listen_key)
        return self.unsubscribe(message, id=id, listen_key=listen_key)

    def subscribe(self, stream, id=None, listen_key=None):
        if not id:
            id = get_timestamp()
        if self._single_stream(stream):
            stream = [stream]
        mes = {
            "method": "subscribe",
            "params": stream,
            "id": str(id)
        }
        if listen_key:
            mes.update({"listenKey": listen_key})
        json_msg = json.dumps(mes)
        self.socket_manager.send_message(json_msg)

    def unsubscribe(self, stream, id=None, listen_key=None):
        if not id:
            id = get_timestamp()
        if self._single_stream(stream):
            stream = [stream]

        mes = {
            "method": "unsubscribe",
            "params": stream,
            "id": str(id)
        }
        if listen_key:
            mes.update({"listenKey": listen_key})
        json_msg = json.dumps(mes)
        self.socket_manager.send_message(json_msg)

    def ping(self):
        logger.debug("Sending ping to XT WebSocket Server")
        self.socket_manager.ping()

    def stop(self, id=None):
        self.socket_manager.close()
        self.socket_manager.join()
