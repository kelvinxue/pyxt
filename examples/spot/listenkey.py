# -*- coding:utf-8 -*-
from pyxt.spot import Spot

xt = Spot(host="https://sapi.xt.com", access_key='', secret_key='')
print(xt.listen_key())
