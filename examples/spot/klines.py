from pyxt.spot import Spot

xt = Spot(host="https://sapi.xt.com", access_key='', secret_key='')
print(xt.get_kline(symbol='btc_usdt', interval="1m"))
print(xt.get_kline(symbol='btc_usdt', interval="1h", limit=10))