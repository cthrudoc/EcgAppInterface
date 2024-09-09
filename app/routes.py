from flask import render_template
from flaskapp import app
from app.forms import LoginForm # formularz importowany z forms.py przesyłany potem do login.html 


@app.route('/index')
@app.route('/')
def index():
    user = {'username' : 'Yan'}
    return render_template("index.html", title="home", user=user)

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)