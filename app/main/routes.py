from datetime import datetime, timezone, timedelta
import io
from os import spawnl
from flask import render_template, flash, send_file,redirect, url_for, request, g, \
    current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
import sqlalchemy as sa
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm,AddInventoryForm,RatingForm, SellCarForm,MpesaForm, ReceiptForm, RemoveCarForm
from app.models import User, Car , Post, Customer, Rating, Payment
from app.main import bp
import pdfkit
# import plotly.graph_objs as go

# from app.profits import get_profit_data


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


#main inventory
#adding to the inventory
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory():
    form =AddInventoryForm()
    if form.validate_on_submit(): 
        vin=form.vin.data      
        make = form.make.data
        model= form.model.data
        year= form.year.data
        BP= form.BP.data
        bought_date= form.bought_date.data

# Add new inventory item to database
        car = Car(vin=vin, make=make, model=model, year=year, BP=BP, bought_date=bought_date)
        db.session.add(car)
        db.session.commit()
        
# Redirect to inventory page
        return redirect(url_for('main.inventory'))
    return render_template('addinventory.html' ,  form=form, title='Inventory')

@bp.route('/inventory/car sold', methods=['POST','GET'])
def sellcar():
    form=SellCarForm()
    if form.validate_on_submit():
        vin=form.vin.data
        car = Car.query.filter_by(vin=vin).first()
        if car and car.available:
            SP=form.SP.data
            sold_date=form.sold_date.data
            car.SP=SP
            car.sold_date=sold_date
            db.session.commit()
            flash('Car found')
            return redirect(url_for('main.sellcar'))
        else:
            flash('Car not found ')

    return render_template('sellcar.html', form=form)
                        
#removing from the inventory
@bp.route('/inventory/removecar', methods=['GET', 'POST'])
def removecar():
    form=RemoveCarForm()
    if form.validate_on_submit():
         vin = form.vin.data
         car = Car.query.filter_by(vin=vin).first()#filtering the vin number cause 2 cars cant have the same vin
         if car and car.available:
             #car.available = False#boolean
             db.session.delete(car)
             db.session.commit
             flash('car removed')
             return redirect (url_for('main.removecar'))
         else:
             flash('Car not found or not available in inventory')
            
         return redirect(url_for('main.removecar'))
    return render_template('removecar.html',form=form)

#viewing the inventory
@bp.route('/inventory/viewinventory' ,methods=['GET', 'POST'])
def inventorystatus():
    available_cars = Car.query.filter_by(available=True).all()
    sold_cars = Car.query.filter_by(available=False).all()
    available_cars_count = Car.query.filter_by(available=True).count()
    sold_cars_count = Car.query.filter_by(available=False).count()
    return render_template('inventorystatus.html', available_cars=available_cars, sold_cars=sold_cars, 
                           available_cars_count=available_cars_count, sold_cars_count=sold_cars_count)

#showing the car view
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/inventory/car view', methods=['GET', 'POST'])
def carview():
    cars = Car.query.all()
    return render_template('carview.html' , cars=cars)


@bp.route('/customercenter', methods=['GET', 'POST'])
@login_required
def customercenter():
    form= PostForm()
    if form.validate_on_submit():
        customer = Customer(form.customername.data)
        db.session.commit()
        post=Post(body=form.post.data, author=customer )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.customercenter'))
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'],
                        error_out=False)
    next_url = url_for('main.customercenter', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.customercenter', page=posts.prev_num) \
        if posts.has_prev else None
    
    
    return render_template('index.html',
                        posts=posts.items, next_url=next_url,
                        prev_url=prev_url, form=form  )

@bp.route('/customercenter/ Payment', methods=['GET', 'POST'])
@login_required
def payment():
    form=MpesaForm()
    if form.validate_on_submit():
        vin = form.vin.data
        car = Car.query.filter_by(vin=vin).first()
        if car and car.available:
            car.available = False#boolean
            db.session.commit()
            flash('Car Payed')
        else:
            flash('Car not available')
        mpesacode= form.mpesacode.data
        payers_name=form.payers_name.data
        payers_email=form.payers_email.data
        payers_phonenumber=form.payers_phonenumber.data
        date=form.date.data
        mpesacode=Payment(mpesacode=mpesacode, vin=vin, payers_name=payers_name,
                          payers_email=payers_email,payers_phonenumber=payers_phonenumber, date=date)
        db.session.add(mpesacode)
        db.session.commit()
        return redirect (url_for('main.payment'))
    return render_template('payment.html', form=form)

@bp.route('/customercenter/ Receipts', methods=['GET', 'POST'])
@login_required
def receipt():
    form=ReceiptForm()
    if form.validate_on_submit():
        mpesacode = form.mpesacode.data
        payment = Payment.query.filter_by(mpesacode=mpesacode).first()
        db.session.add(payment)
        return (url_for('main.receipt'))

    return render_template('receipt.html', form=form)
        # Generate the receipt as a PDF
    #     pdf = generate_receipt_pdf(payment)

    #     return send_file(
    #     io.BytesIO(pdf),
    #     attachment_filename=f'Receipt_{payment.mpesacode}.pdf',
    #     mimetype='application/pdf',
    #     as_attachment=True
    # )
    # else:
    # # If the form is not valid, show an error message
    #     flash('Invalid M-PESA code. Please check the code and try again.')
    return render_template('receipt_form.html', form=form)


# def generate_receipt_pdf(payment):
#     # Generate the HTML for the receipt
#     html = render_template('receipt.html', payment=payment)

#     # Convert the HTML to a PDF
#     config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe') # Add path to wkhtmltopdf.exe
#     pdf = pdfkit.from_string(html, False, configuration=config)

#     return pdf
            
    

            
@bp.route('/customercenter/Socials and Ratings', methods=['GET','POST'])
@login_required
def socialsandrating():
    form=RatingForm()  
    if form.validate_on_submit(): 
        service = form.service.data
        product = form.product.data
        efficiency = form.efficiency.data
        payment = form.payment.data
        overall = form.overall.data

        rating= Rating(service=service,product=product,efficiency=efficiency,payment=payment,overall=overall)
        
        
        db.session.add(rating)
        db.session.commit()
    
        flash('Thank you for your feedback!')
        return redirect(url_for('main.socialsandrating'))

    return render_template('socialsandrating.html', form=form)



@bp.route('/Service and maintenance/notification', methods=['GET', 'POST'])
@login_required
def notifications():
    car_old = Car.query.filter(Car.bought_date < datetime.now(timezone.utc) - timedelta(days=30)).all()
    if car_old:
        messages = []
        for car in car_old:
            message = f"{car.model} {car.make} {car.vin} is due for maintenance"
            messages.append(message)
    else:
        messages = None
    return render_template('notifications.html', messages=messages)

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/analytics', methods=['GET', 'POST'])
@login_required
def analytics():
    available_cars = Car.query.filter_by(available=True).all()
    sold_cars = Car.query.filter_by(available=False).all()
    available_cars_count = Car.query.filter_by(available=True).count()
    sold_cars_count = Car.query.filter_by(available=False).count()

    # Calculate profits for cars sold
    sales = db.session.query(
        Car.id,
        Car.SP,  # column for the selling price
        Car.BP   # column for the purchase price
    ).filter(
        Car.available==False
    ).all()

    profits = 0
    num_sold_cars = 0
    for sale in sales:
        profits += sale.SP - sale.BP
        num_sold_cars += 1

    avg_profit = 0
    if num_sold_cars > 0:
        avg_profit = profits / num_sold_cars

    return render_template('analytics.html',
        available_cars_count=available_cars_count,available_cars=available_cars,sold_cars=sold_cars,
        sold_cars_count=sold_cars_count,
        profits=profits,
        avg_profit=avg_profit
    )





    
@bp.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    form = EmptyForm()
    return render_template('user.html', user=user, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)




