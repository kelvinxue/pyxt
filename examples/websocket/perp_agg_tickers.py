# -*- coding:utf-8 -*-
import time
from pyxt.websocket import logger
from pyxt.websocket.perp import PerpWebsocketStreamClient

logger.initLogger()

if __name__ == '__main__':
    symbol = "btc_usdt"


    def message_handler(_, message):
        logger.info(message)


    my_client = PerpWebsocketStreamClient(on_message=message_handler,
                                          proxies={"http": "http://127.0.0.1:1088"})

    # Subscribe to a single symbol stream
    my_client.agg_tickers(action=PerpWebsocketStreamClient.ACTION_SUBSCRIBE)
    time.sleep(5)
    # # Unsubscribe
    my_client.agg_tickers(action=PerpWebsocketStreamClient.ACTION_UNSUBSCRIBE)
    time.sleep(5)
    logger.info("closing ws connection")
    my_client.stop()
