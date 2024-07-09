from app import db, app
from datetime import datetime, timezone
from models import Car

@app.before_first_request
def check_expired_cars():
    """Check for expired cars and send notifications."""
    for car in Car.query.filter(Car.is_expired()):
        print(datetime.now(timezone.utc), f"Car {car.make} {car.model} has been in the database for more than 30 days.")