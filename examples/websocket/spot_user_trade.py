# -*- coding:utf-8 -*-
import time
import threading
from pyxt.websocket.spot import SpotWebsocketStreamClient

if __name__ == '__main__':
    symbol = "btc_usdt"
    listen_key = ""


    def message_handler(_, message):
        print(message)


    my_client = SpotWebsocketStreamClient(on_message=message_handler,
                                          is_auth=True)

    # Subscribe to a single symbol stream
    my_client.trade(listen_key=listen_key, action=SpotWebsocketStreamClient.ACTION_SUBSCRIBE)
    # keep heartbeat
    threading.Thread(target=my_client.heartbeat, daemon=False).start()
    time.sleep(5)
    # # Unsubscribe
    my_client.trade(listen_key=listen_key, action=SpotWebsocketStreamClient.ACTION_UNSUBSCRIBE)
    time.sleep(5)
    print("closing ws connection")
    my_client.stop()
