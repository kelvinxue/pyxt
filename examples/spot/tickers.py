from pyxt.spot import Spot

xt = Spot(host="https://sapi.xt.com", access_key='', secret_key='')
print(xt.get_tickers(symbol='btc_usdt'))
print(xt.get_tickers(symbols=['btc_usdt', 'xt_usdt']))
