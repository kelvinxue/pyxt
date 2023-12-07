from pyxt.spot import Spot

xt = Spot(host="https://sapi.xt.com", access_key='', secret_key='')
print(xt.get_tickers_book(symbol='btc_usdt'))
print(xt.get_tickers_book(symbols=['btc_usdt', 'xt_usdt']))
