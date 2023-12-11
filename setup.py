from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='pyxt',
    version='0.4.5',
    description='Python3 XT.COM HTTP API Connector',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kelvinxue/pyxt",
    download_url='https://github.com/kelvinxue/pyxt/archive/refs/tags/v0.4.5.tar.gz',
    license="MIT License",
    author="xt",
    author_email="xt@xt.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="xt api connector",
    packages=["pyxt", "pyxt.websocket"],
    python_requires=">=3.9",
    install_requires=[
        "requests"
    ]
)
