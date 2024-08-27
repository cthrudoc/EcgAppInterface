from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel

app = FastAPI()
baza = "baza.db"

class makepies(BaseModel):
    imie: str
    wiek: int

@app.get("/psy/")
def readpies():
    connect = sqlite3.connect(baza)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM psy") 
    odczytane_psy = cursor.fetchall()
    connect.close
    return odczytane_psy

@app.post("/psy/")
def addpies(nowypies: makepies):
    connect = sqlite3.connect(baza)
    cursor = connect.cursor()
    cursor.execute("INSERT INTO psy (imie , wiek) VALUES (?,?)",(nowypies.imie, nowypies.wiek)) 
    connect.commit()
    connect.close()
    return nowypies
