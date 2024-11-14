# -*- coding:utf-8 -*-
import time
import threading
from pyxt.websocket.spot import SpotWebsocketStreamClient


if __name__ == '__main__':
    symbol = "btc_usdt"


    def message_handler(_, message):
        print(message)


    my_client = SpotWebsocketStreamClient(on_message=message_handler)

    # Subscribe to a single symbol stream
    my_client.kline(symbol=symbol, interval="1m", action=SpotWebsocketStreamClient.ACTION_SUBSCRIBE)
    # keep heartbeat
    threading.Thread(target=my_client.heartbeat, daemon=False).start()
    time.sleep(5)
    # # Unsubscribe
    my_client.kline(
        symbol=symbol, interval="1m", action=SpotWebsocketStreamClient.ACTION_UNSUBSCRIBE
    )
    time.sleep(5)
    print("closing ws connection")
    my_client.stop()
