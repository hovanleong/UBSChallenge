from flask import Flask

app = Flask(__name__)
import routes.square
import routes.dc
import routes.kazuma
