from pyxt.spot import Spot

xt = Spot(host="https://sapi.xt.com", access_key='', secret_key='')
res = xt.cancel_order(order_id=12345678)
print(res)
