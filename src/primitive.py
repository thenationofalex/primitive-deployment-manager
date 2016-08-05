#!/usr/bin/env python3
'''Primitive Deployment Manager'''

import os

from dotenv import Dotenv
from termcolor import colored

dotenv_path = os.path.dirname(os.path.realpath(__file__)) + '/../.env'
dotenv = Dotenv(dotenv_path)
os.environ.update(dotenv)

print(colored('📡 🛰  Primitive Deployment Manager v0.0.1', 'magenta'))
