from pyxt.perp import Perp

xt = Perp(host="https://fapi.xt.com", access_key='', secret_key='')
res = xt.send_order(symbol='btc_usdt', price=10000, amount=1, order_side='BUY', order_type='LIMIT', position_side='LONG')
print(res)
