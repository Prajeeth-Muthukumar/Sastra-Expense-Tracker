from flask import Flask, render_template, request, url_for, redirect, flash
import numpy as np
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_BINDS'] = {
    'records' : 'sqlite:///records.sqlite3'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class users(db.Model):
    id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    username = db.Column(db.String(100), nullable = False, unique = True)
    password = db.Column(db.String(100), nullable = False)

    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = password

class records(db.Model):
    __bind_key__ = 'records'
    id = db.Column("id", db.Integer, primary_key = True, nullable = False)
    description = db.Column(db.String(50), nullable = False)
    amount = db.Column(db.Numeric(precision=10, scale=2), nullable = False)
    uid = db.Column(db.Integer, nullable = False)
    category = db.Column(db.String(50), nullable = False)

    def __init__(self, uid, description, amount, category):
        self.uid = uid
        self.description = description
        self.amount = amount
        self.category = category

@app.route('/')
def redirectPage():
    return redirect('/login')

@app.route('/login', methods = ["POST", "GET"])
def loginPage():
    if (request.method == "POST"):
        global name
        global uid
        uname = request.form["username"]
        password = request.form["password"]

        data = users.query.filter_by(username = uname, password = password).first()

        if data:
            name = data.name
            uid = data.id
            return redirect('/home')
        
        else:
            return render_template('login.html', stat = 1)
        
    return render_template('login.html', stat = 0)


@app.route('/signup', methods = ["POST", "GET"])
def signUp():
    if (request.method == "POST"):
        global name
        global uid
        name = request.form["name"]
        username = request.form['username']
        password = request.form['password']

        check = users.query.filter_by(username = username).first()
        
        if (not check):
            newUser = users(name, username, password)
            db.session.add(newUser)
            db.session.commit()

            data = users.query.filter_by(username = username).first()
            uid = data.id
            return redirect('/home')
        
        else:
            return render_template('signup.html', stat = 1)
        
    return render_template('signup.html', stat = 0)


@app.route('/home', methods = ["POST", "GET"])
def home_page():
    total = 0
    entries = records.query.filter_by(uid = uid)

    for j in entries:
        total += float(j.amount)
    
    if (request.method == "POST"):
        description = request.form["desc"]
        amount = request.form["amt"]
        category = request.form["cat"]
        total += float(amount)
        newEntry = records(uid, description, amount, category)
        db.session.add(newEntry)
        db.session.commit()

        entries = records.query.filter_by(uid = uid)
        return render_template('mainpage.html', name = name, entries = entries, sum = total)

    print(entries)
    if entries:
        return render_template('mainpage.html', name = name, entries = entries, sum = total)
    else:
        print("vanakkam")
        return render_template('mainpage.html',stat = 1, name = name, entries = entries, sum = total)
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(host = '0.0.0.0')
