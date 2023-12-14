# -*- coding:utf-8 -*-
from pyxt.perp import Perp

xt = Perp(host="https://fapi.xt.com", access_key='', secret_key='')
print(xt.listen_key())
