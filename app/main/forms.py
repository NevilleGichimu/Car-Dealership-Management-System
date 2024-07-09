from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, TextAreaField, DateField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
import sqlalchemy as sa
from flask_babel import _, lazy_gettext as _l
from app import db
from app.models import User, Customer
from datetime import datetime


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == self.username.data))
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    customername=StringField(('Name'), validators=[DataRequired(), Length(min=1, max=30)])
    post = TextAreaField(_l('Say something'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))

class AddInventoryForm(FlaskForm):
    vin = IntegerField('Vin-Number', validators=[DataRequired()])
    make=StringField('Make',validators=[DataRequired(), Length(min=1,max=50)])
    model = StringField('Model', validators=[DataRequired(), Length(min=1,max=140)])
    year = IntegerField('Year',validators=[DataRequired()])
    BP = IntegerField('Buying Price', validators=[DataRequired()])
    bought_date= DateField('Date Bought ', validators=[DataRequired()], format=['%Y-%m-%d'])
    submit = SubmitField('Add Inventory')

class SellCarForm(FlaskForm):
    vin = IntegerField('Vin-Number', validators=[DataRequired()])
    SP = IntegerField('Selling Price', validators=[DataRequired()])
    sold_date=DateField('Date Added',validators=[DataRequired()], format=['%Y-%m-%d'])
    submit= SubmitField('Add Price')

class RemoveCarForm(FlaskForm):
    vin= IntegerField('Vin-Number', validators=[DataRequired()])
    submit= SubmitField('Remove Inventory')

class RatingForm(FlaskForm):
    service = SelectField('Service', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], coerce=int)
    product = SelectField('Product', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], coerce=int)
    efficiency = SelectField('Efficiency', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], coerce=int)
    payment = SelectField('Payment', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], coerce=int)
    overall = SelectField('Overall', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], coerce=int)
    submit = SubmitField('Submit')

class MpesaForm(FlaskForm):
    mpesacode= StringField('Mpesa Code', validators=[DataRequired(), Length(min=1, max=20)])
    vin= IntegerField('Vin-Number', validators=[DataRequired()])
    payers_name=StringField('Name', validators=[DataRequired(), Length(min=1, max=70)])
    payers_email=StringField('Email', validators=[DataRequired(), Length(min=1, max=70)])
    payers_phonenumber=StringField('Phone Number', validators=[DataRequired(), Length(min=1, max=70)])
    date=DateField('Date',validators=[DataRequired()], format=['%Y-%m-%d'])
    submit=SubmitField('Confirm')

class ReceiptForm(FlaskForm):
    mpesacode=StringField('Mpesa Code', validators=[DataRequired(), Length(min=1, max=20)])
    SubmitField=SubmitField('Print')
