from pyxt.spot import Spot

xt = Spot(host="https://sapi.xt.com", access_key='', secret_key='')
res = xt.order(symbol='btc_usdt', price=10000, quantity=0.001, side='BUY', type='LIMIT')
print(res)
