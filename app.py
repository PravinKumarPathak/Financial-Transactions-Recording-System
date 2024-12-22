from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

app=Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(precision=10, scale=2))
    desc = db.Column(db.String(500), nullable=False)
    
    def __repr__(self)->str:
        return f'{self.date}-{self.amount}'

class Contact(db.Model):
    srn = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            user = Contact.query.filter_by(email=email).first()
            if(user==None):
                flash("We don't recognize this email. Create a new account")
                return render_template('login.html')
            pas = user.password
            if(sha256_crypt.verify(password, pas)):
                session['email']=email
                return redirect(url_for('get_transactions'))
            else:
                flash("Invalid password for the given email")
                return render_template('login.html')

        except:
                flash('Try again')
                return render_template('login.html')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email=request.form['email']
        password = request.form['password']
        encpassword = sha256_crypt.encrypt(password)

        entry = Contact(email=email, password=encpassword)
        try:
            db.session.add(entry)
            db.session.commit()
            flash('Registration done')
            return render_template('login.html')
        except:
            flash('Try again')
            return render_template('register.html')   
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return render_template('login.html')

@app.route("/get_transactions")
def get_transactions():
    if 'email' not in session:
        flash('Please log in first!')
        return render_template('login.html')

    allOb = Todo.query.all()
    return render_template('transactions.html', tob=allOb)

@app.route("/add", methods=["GET", "POST"])
def add_transaction():
    if request.method == 'POST':
        date = request.form['date']
        amount = float(request.form['amount'])
        desc = request.form['desc']
        ob = Todo(date=date, amount=amount, desc=desc)
        db.session.add(ob)
        db.session.commit()
        return redirect(url_for("get_transactions"))

    return render_template("form.html")

@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
def edit_transaction(transaction_id):
    if request.method == 'POST':
        date = request.form['date']
        amount = float(request.form['amount'])
        desc = request.form['desc']
        ob = Todo.query.filter_by(id=transaction_id).first()
        ob.date = date
        ob.amount = amount
        ob.desc = desc
        db.session.commit()
        return redirect(url_for("get_transactions"))

    ob = Todo.query.filter_by(id=transaction_id).first()
    return render_template("edit.html", tob=ob)

@app.route("/delete/<int:transaction_id>")
def delete_transaction(transaction_id):
    ob = Todo.query.filter_by(id=transaction_id).first()
    db.session.delete(ob)
    db.session.commit()
    return redirect(url_for("get_transactions"))

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == 'POST':
        minval = float(request.form['min_amount'])
        maxval = float(request.form['max_amount'])
        filtered_transactions = []
        allSob = Todo.query.all()
        for ob in allSob:
            if ob.amount >= minval and ob.amount <= maxval:
                filtered_transactions.append(ob)
        return render_template('searched_transaction.html', tob=filtered_transactions)

    return render_template("search.html")

@app.template_filter('truncate')
def truncate(text, max_length):
    if len(text) > max_length:
        return text[:max_length] + '...'
    return text

if __name__ == "__main__":
    app.run(debug=True)
