from pyxt.perp import Perp

xt = Perp(host="https://fapi.xt.com", access_key='', secret_key='')
print(xt.get_k_line(symbol='btc_usdt', interval="1m"))
