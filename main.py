from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__, template_folder='templates')
app.secret_key = 'dein-super-sicherer-schlüssel'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User- und Message-Models

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(200), nullable=True)
    content = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        user = User.query.filter_by(username=username).first()

        if user:
            if user.password == password:
                session['username'] = user.username
                return redirect(url_for("start_page", name=user.username))
            else:
                flash("Falsches Passwort", "danger")
        else:
            # Neuer Benutzer wird registriert
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.username
            flash("Neuer Benutzer registriert", "success")
            return redirect(url_for("start_page", name=new_user.username))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('username', None)
    flash("Logout erfolgreich", "info")
    return redirect(url_for("login"))

@app.route("/<name>", methods=['GET', 'POST'])
def start_page(name):
    print("FORM-DATEN:", request.form)
    if 'username' not in session or session['username'] != name:
        flash("Bitte zuerst einloggen!", "warning")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        print("POST REQUEST ERKANNT:", request.form)
        action = request.form.get('action')
        content = request.form.get('content')

        if action == 'send':
            if content and content.strip():
                new_message = Message(user=name, content=content.strip())
                db.session.add(new_message)
                db.session.commit()

        elif action == 'clear':
            Message.query.delete()
            db.session.commit()

        return redirect(url_for('start_page', name=name))

    messages = Message.query.order_by(Message.created_at).all()
    return render_template("index.html", messages=messages, current_user=name)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)