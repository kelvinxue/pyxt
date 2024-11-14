# -*- coding:utf-8 -*-
import time
import threading
from pyxt.websocket.perp import PerpWebsocketStreamClient

if __name__ == '__main__':
    symbol = "btc_usdt"
    listen_key = ""


    def message_handler(_, message):
        print(message)


    my_client = PerpWebsocketStreamClient(on_message=message_handler,
                                          is_auth=True)

    # Subscribe to a single symbol stream
    my_client.user_order(listen_key=listen_key, action=PerpWebsocketStreamClient.ACTION_SUBSCRIBE)
    # keep heartbeat
    threading.Thread(target=my_client.heartbeat, daemon=False).start()
    time.sleep(5)
    # # Unsubscribe
    my_client.user_order(listen_key=listen_key, action=PerpWebsocketStreamClient.ACTION_UNSUBSCRIBE)
    time.sleep(5)
    print("closing ws connection")
    my_client.stop()
