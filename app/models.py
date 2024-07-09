from datetime import datetime, timezone, timedelta
from hashlib import md5
from time import time
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import json
from app import db, login



class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


    

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception:
            return
        return db.session.get(User, id)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Customer(db.Model):
    id:so.Mapped[int]= so.mapped_column(primary_key=True)
    customername:so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author')
    
    def __init__(self, customername):
        self.customername = customername


class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    customer_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Customer.id),
                                               index=True)
    language: so.Mapped[Optional[str]] = so.mapped_column(sa.String(5))

    author: so.Mapped[Customer] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    
    
class Car(db.Model):
    id : so.Mapped[int]=so.mapped_column(nullable=True)
    vin: so.Mapped[int]=so.mapped_column(primary_key=True, nullable=True)
    make :so.Mapped[str]=so.mapped_column (sa.String(20),nullable=True)
    model : so.Mapped[str]=so.mapped_column (sa.String(20),nullable=True )
    year : so.Mapped[int]=so.mapped_column(sa.Integer(), nullable=True)
    BP : so.Mapped[float]=so.mapped_column(sa.Float(), nullable=True)
    SP: so.Mapped[float]=so.mapped_column(sa.Float(), nullable=True , default=0)
    bought_date: so.Mapped[datetime]=so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    sold_date: so.Mapped[datetime]=so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    available: so.Mapped[bool]=so.mapped_column(sa.Boolean, default=True)

    def __repr__(self):
        return f'<Car  {self.model} {self.vin} {self.year} {self.BP} {self.SP} {self.bought_date} {self.sold_date} {self.make} {self.available}>'
   
    def is_expired(self):
        """Returns True if the car has been in the database for more than 30 days."""
        return datetime.now(timezone.utc) - self.bought_date > timedelta(days=30)

class Rating(db.Model):
    id :so.Mapped[int]=so.mapped_column(primary_key=True)
    service : so.Mapped[int]=so.mapped_column(sa.Integer(), nullable=False)
    product :so.Mapped[int]=so.mapped_column(sa.Integer(), nullable=False)
    efficiency :so.Mapped[int]=so.mapped_column(sa.Integer(), nullable=False)
    payment : so.Mapped[int]=so.mapped_column(sa.Integer(), nullable=False)
    overall : so.Mapped[int]=so.mapped_column(sa.Integer(), nullable=False)

    def __repr__(self):
        return f'<Rating {self.id} {self.service}{self.product}{self.efficiency}{self.payment}{self.overall}>'
    
class Payment(db.Model):
    mpesacode: so.Mapped[str]= so.mapped_column (primary_key=True)
    vin :so.Mapped[int]=so.mapped_column(sa.Integer(), nullable=False)
    payers_name:so.Mapped[str]=so.mapped_column(sa.String(), nullable=False)
    payers_email: so.Mapped[str] = so.mapped_column(sa.String(120), nullable=False)
    payers_phonenumber:so.Mapped[int]= so.mapped_column(sa.Integer, nullable=False)
    date: so.Mapped[datetime]=so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))

    def _repr__(self):
        return f'<Payment {self.mpesacode} {self.vin} {self.payers_name} {self.payers_email} {self.payers_phonenumber}>'