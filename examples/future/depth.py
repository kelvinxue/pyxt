from pyxt.future import Future

xt = Future(host="https://fapi.xt.com", access_key='', secret_key='')
print(xt.get_depth(symbol='btc_usdt', depth=10))
