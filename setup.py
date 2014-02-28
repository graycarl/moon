# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="moon",
    version="0.3",
    packages=["moon", "moon.sqlalchemy", "moon.lazy"],

    install_requires=['sqlalchemy'],

    description="Useful Snips All in One",
    author="Hongbo He",
    author_email="hhbcarl@gmail.com",
    url="http://blog.graycarl.me",
)
