import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from __init__ import app, db, bcrypt, mail
from models import User, Hobies, subs
from forms import RegistrationForm, LoginForm, UpdateAccountForm, SearchBar, HobbiesForm, RequestResetForm, ResetPasswordForm
from flask_mail import Message
from flask_login import login_user, current_user, logout_user, login_required
from preprocess import w_tok


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
    formq=SearchBar()
    return render_template('home.html', form=LoginForm(), forml=RegistrationForm(), formq=formq,title='Home')


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (300, 200)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html', form=LoginForm(), forml=RegistrationForm(),title= 'About')


@app.route("/contribution", methods=['GET', 'POST'])
def contribution():
    form_d = HobbiesForm()
    if form_d.validate_on_submit():
        picture_file=""
        if form_d.picture.data:
            print('Savage')
            picture_file = save_picture(form_d.picture.data)
        tag = form_d.tag.data
        title = form_d.title.data
        content = form_d.content.data
        new_hobby = Hobies(tag=tag,title=title,content=content,image_file=picture_file)
        db.session.add(new_hobby)
        db.session.commit()
        flash('Your entered hobby is added to database Successfully !!!', 'success')
        return redirect(url_for('home'))
    return render_template('contribution.html', form=LoginForm(), forml=RegistrationForm(), form_d=form_d)




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
    curr_user_id = current_user.get_id()
    curr_user = User.query.get_or_404(curr_user_id)
    selected_prod = curr_user.products

    return render_template('account.html', curr_user=curr_user,selected_prod=selected_prod, title='Account')

@app.route("/search_result", methods=['POST', 'GET'])
def search_result():
    formq=SearchBar()
    if formq.validate_on_submit():
        text = formq.search_query.data
        print(text,type(text),bool(text=='All'))
        if bool(text == 'All'):
            results = Hobies.query.all()
        else :
            search_query=w_tok(text)
            words = []
            for w in search_query:
                words.append('%'+w+'%')
            query_str = "SELECT * FROM hobies WHERE "
            query_str += "tag LIKE " + "'" + words[0] +"'" + " OR title LIKE " + "'" + words[0] +"'" + " OR content LIKE " + "'" + words[0] +"'"
            for w in words[1:]:
                query_str+="OR tag LIKE " + "'" + w +"'" + " OR title LIKE " + "'" + w +"'" +" OR content LIKE " + "'" + w +"'" 
            results = db.engine.execute(query_str)
            print("Search Executed")
            print(query_str)
        return render_template('search_result.html', form=LoginForm(), text=text, forml=RegistrationForm(), formq=formq, hob=results, title='Search_Result')
    return redirect(url_for('home'))


@app.route("/product/<int:prod_id>/<int:bol_>")
def product(prod_id,bol_):
    prod = Hobies.query.get_or_404(prod_id)
    if bol_ :
        if current_user.is_authenticated:
            prod = Hobies.query.get_or_404(prod_id)
            curr_user_id = current_user.get_id()
            print(curr_user_id)
            curr_user = User.query.get_or_404(curr_user_id)
            selected_prod = curr_user.products
            flag = True
            for pord in selected_prod:
                if prod_id == pord.prod_id:
                    flag = False 

            print(flag)
            if flag :
                curr_user.products.append(prod)
                db.session.commit()
                flash('Product Added to your account Successfully', 'success')
            else :
                flash('Product is already in your account !!!', 'info')

        else :
            flash('You need to login for accessing this feature', 'danger')

    return render_template('product.html', prod = prod, form=LoginForm(), forml=RegistrationForm(),title='Product')


def send_reset_email(user):
    token = user.get_reset_token()
    print(token)
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    formr = RequestResetForm()
    if formr.validate_on_submit():
        user = User.query.filter_by(email=formr.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', formr=formr, form=LoginForm(), forml=RegistrationForm())


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', formr=form, form=LoginForm(), forml=RegistrationForm())


if __name__ == '__main__':
    app.run(debug=True)
