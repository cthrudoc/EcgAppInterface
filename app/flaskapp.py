from flask import Flask
from flask import render_template, flash, redirect, url_for # [BUG] Ta linia powinna być w routes 
from config import Config
from forms import LoginForm # formularz importowany z forms.py przesyłany potem do login.html 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ROUTES 
# [BUG] Aplikacja powinna wywoływać osobny moduł "routes" ale nie wiem dalczego nie importuje.
@app.route('/index')
@app.route('/')
def index():
    user = {'username' : 'Yan'}
    return render_template("index.html", title="home", user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit(): # ta funkcja oczekuje POST, jeżeli przeglądarka wyśle GET, funkcja esencjalnie wykonuje pythonowy "break" w tej pętli "if". 
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data)) # [BUG] sprawdź co to .format, jak działa funkcja flash()
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

# Importowanie modułu niżej w celu uniknięcia zapętlenia wywoływania (flaskapp wywołuje routes, routes wywołuje flaskapp)
# [BUG] NIE DZIAŁA I NIE MOGĘ WYMYŚLIĆ DLACZEGO
# import routes

if __name__ == '__main__':
    app.run(debug=True)

