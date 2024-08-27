from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)
api_url = "http://127.0.0.1:8000"

@app.route('/')
def index():
    response = requests.get(f"{api_url}/psy/")
    psy = response.json()
    return render_template("index.html", piesy=psy)

@app.route("/dodaj", methods = ['POST'])
def dodaj():
    imie = request.form.get("imie")
    wiek = request.form.get("wiek")
    requests.post(f"{api_url}/psy/" , json = {"imie" : imie , "wiek" : wiek})
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)