# Flask database viewer 
from flask import Flask

app = Flask(__name__)

app.config.from_object('FlaskViewer.settings')

import FlaskViewer.controllers