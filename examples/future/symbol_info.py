from pyxt.future import Future

xt = Future(host="https://fapi.xt.com", access_key='', secret_key='')
print(xt.get_market_config(symbol='btc_usdt'))
