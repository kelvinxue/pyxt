# -*- coding:utf-8 -*-
import time
from pyxt.websocket.spot import SpotWebsocketStreamClient


if __name__ == '__main__':
    symbol = "btc_usdt"


    def message_handler(_, message):
        print(message)


    my_client = SpotWebsocketStreamClient(on_message=message_handler)

    # Subscribe to a single symbol stream
    my_client.all_ticker(action=SpotWebsocketStreamClient.ACTION_SUBSCRIBE)
    time.sleep(5)
    # # Unsubscribe
    my_client.all_ticker(action=SpotWebsocketStreamClient.ACTION_UNSUBSCRIBE)
    time.sleep(5)
    print("closing ws connection")
    my_client.stop()
