from app import db, app
from app.models import Chart

def add_charts():
    with app.app_context():
        for i in range(2):
            chart = Chart()
            db.session.add(chart)
        db.session.commit()
        print("dodano wykresy")

add_charts()