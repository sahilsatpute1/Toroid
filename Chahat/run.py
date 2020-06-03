from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
def account():
    return render_template('account.html')

if __name__ == '__main__':
    app.run(debug=True)