from flask import Flask

app = Flask(__name__)
import routes.square
import routes.dc2
import routes.kazuma
import klotski
