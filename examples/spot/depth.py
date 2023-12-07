from pyxt.spot import Spot

xt = Spot(host="https://sapi.xt.com", access_key='', secret_key='')
print(xt.get_depth(symbol='btc_usdt'))
print(xt.get_depth(symbol='btc_usdt', limit=10))
