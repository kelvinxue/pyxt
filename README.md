# pyxt
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Official Python3 API connector for XT.COM's HTTP APIs.

## Table of Contents

- [About](#about)
- [Installation](#installation)
- [Usage](#usage)
- [Contact](#contact)

## About
Put simply, `pyxt` (Python + XT.COM) is the official lightweight one-stop-shop module for the XT.COM HTTP APIs. 

## Installation
`pyxt` requires Python 3.9.1 or higher. The module can be installed manually or via [PyPI](https://pypi.org/project/pyxt/) with `pip`:
```
pip install pyxt
```

## Usage
You can retrieve a specific market like so:
```python
from pyxt.spot import Spot
```

Create an HTTP session and connect via WebSocket for Inverse on mainnet:
```python
xt = Spot(host="http://sapi.xt.com", access_key='', secret_key='')
```

Information can be sent to, or retrieved from, the XT.COM APIs:
```python
print(xt.balance("usdt"))
```

## Contact
You can reach out for support on the [XTAPI Telegram](https://t.me/XT_api) group chat.
