from flask import render_template, url_for, flash, redirect, request, abort
from __init__ import app, db, bcrypt
from models import User
from forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    forml = LoginForm()
    if forml.validate_on_submit():
        user = User.query.filter_by(email=forml.email.data).first()
        if user and bcrypt.check_password_hash(user.password, forml.password.data):
            login_user(user, remember=forml.remember.data)
            next_page = request.args.get('next')
            flash('You are Successfully Logged In', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    else :
        return redirect(url_for('home'))
    return redirect(url_for('home'))



@app.route("/", methods=['GET', 'POST'])
@app.route("/home",methods=['GET', 'POST'])
def home():
    form=LoginForm()
    if form.validate_on_submit():
        email=form.email.data
        print ("siuccess")
        return render_template('home.html', form=form,email=email)
    return render_template('home.html', form=form, forml=RegistrationForm())


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('home'))
    else :
        flash('Something went Wrong can,t submit form', 'danger')
    return redirect(url_for('home'))


@app.route("/logout")
def logout():
    logout_user()
    flash('You are Successfully Logged OUT', 'success')
    return redirect(url_for('home'))



@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email
    return render_template('account.html', first_name = first_name, last_name = last_name, email = email)


if __name__ == '__main__':
    app.run(debug=True)
