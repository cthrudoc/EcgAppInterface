import sqlite3

def makedb():
    connect = sqlite3.connect("baza.db")
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE psy (
                   imie TEXT,
                   wiek INTEGER
    )
""")
    connect.commit()
    connect.close()

if __name__ == "__main__":
    makedb()