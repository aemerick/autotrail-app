from flask import render_template
from flaskapp import app
# from flaskapp.a_model import ModelIt
import pandas as pd
from flask import request

@app.route('/')
def homepage():
    return render_template("model_page.html")
