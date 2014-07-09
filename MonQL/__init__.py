# Flask database viewer 
from flask import Flask
__version__ = '0.0.1'

app = Flask(__name__)

app.config.from_object('MonQL.settings')

import MonQL.controllers