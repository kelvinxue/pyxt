from pyxt.perp import Perp

xt = Perp(host="https://fapi.xt.com", access_key='', secret_key='')
print(xt.get_book_ticker(symbol='btc_usdt'))
