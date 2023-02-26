from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == "POST":
        # Purchase Item Logic
        purchased_item = request.form.get('purchased_item')
        purchased_item_obj = Item.query.filter_by(name=purchased_item).first()
        if purchased_item_obj:
            if current_user.can_purchase(purchased_item_obj):
                purchased_item_obj.buy(current_user)
                flash(f"You purchased {purchased_item_obj.name} for ${purchased_item_obj.price}", category="success")
            else:
                flash(f"Unfortunately, you don't have enough funds to purchase {purchased_item_obj.name}", category="danger")

        # Sell Item Logic
        sold_item = request.form.get('sold_item')
        sold_item_obj = Item.query.filter_by(name=sold_item).first()
        if sold_item_obj:
            if current_user.can_sell(sold_item_obj):
                sold_item_obj.sell(current_user)
                flash(f"Woohoo! {sold_item_obj.name} is now on the market", category="success")
            else:
                flash(f"Something went wrong selling {sold_item_obj.name}", category='danger')
        return redirect(url_for('market_page'))
    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html',
                               items=items,
                               purchase_form=purchase_form,
                               owned_items=owned_items,
                               selling_form=selling_form)
    return redirect(url_for('market_page'))

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email=form.email.data,
                              password=form.password1.data
                              )
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category="success")

        return redirect(url_for('market_page'))

    # If no errors from validations
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash(f'Incorrect username or password', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash(f'You have logged out', category='info')
    return redirect(url_for('home_page'))
