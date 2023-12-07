from pyxt.future import Future

xt = Future(host="https://fapi.xt.com", access_key='', secret_key='')
res = xt.cancel_order(order_id=12345678)
print(res)
