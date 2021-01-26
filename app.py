from flask import Flask, render_template, redirect, request, flash, session, url_for, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///english.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# python -c 'import os; print(os.urandom(16))'
app.secret_key = b'\xa3 x>\xfa\xe2\xf8\xa3\xa98\xc7\x97\x91J\xd0x'

# Initializing database
db = SQLAlchemy(app)

# Create db model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    voice = db.Column(db.Integer, default=0);
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    days = db.Column(db.Integer, default=0)
    hours = db.Column(db.Integer, default=0)
    minutes = db.Column(db.Integer, default=1)
    seconds = db.Column(db.Integer, default=0)


    # Create function to return string when we add something
    def __repr__(self):
        return "<User(id='%d', username='%s', voice='%d')>" % (self.id, self.username, self.voice)

class Voc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    english = db.Column(db.String(100), nullable=False)
    vietnamese = db.Column(db.String(100), nullable=False)
    pronounciation = db.Column(db.String(100), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    note = db.Column(db.String(500))
    priority = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<Voc(id='%s', english='%s', vietnamese='%s', author_id='%d', note='%s', priority='%d')>" % (str(self.id), self.english, self.vietnamese, self.author_id, self.note, self.priority)

    def to_dict(self):
        return {
            'id': self.id,
            'english': self.english,
            'vietnamese': self.vietnamese,
            'pronounciation': self.pronounciation,
            'author_id': self.author_id,
            'created_date': self.created_date,
            'note': self.note
        }


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if (request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']

        database = User.query.all()
        for usr in database:
            if (usr.username == username and check_password_hash(usr.password, password)):
                session.clear()
                session['user_id'] = usr.id
                session['time'] = datetime.now()
                return redirect(url_for('index'))
        flash('Login unsucessfuly')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/register', methods=('GET', 'POST'))
def register():
    if (request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']

        if (username == '' or password == ''):
            flash('Username or Password not be empty!')
            return render_template('register.html')

        new_user = User(username=username, password=generate_password_hash(password))

        # Check where username is duplicate
        database = User.query.all()
        for usr in database:
            if (usr.username == username):
                flash('Username is already exists!')
                return render_template('register.html')

        # Push into database
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')
        except:
            return "There was an issue when registering!"

    return render_template('register.html')

@app.route('/vocabulary', methods=('GET', 'POST'))
def vocabulary():
    if (request.method == 'POST'):
        english = request.form['english']
        vietnamese = request.form['vietnamese']
        pronounciation = request.form['pronounciation']
        note = request.form['note']
        author_id = session.get('user_id')
        priority = 0

        new_word = Voc(
            english=english,
            vietnamese=vietnamese,
            pronounciation=pronounciation,
            note=note,
            priority=priority,
            author_id=author_id
        )

        try:
            session['time'] = datetime.now()
            
            data = Voc.query.filter_by(author_id=author_id).order_by(Voc.priority).all()
            cnt = 1
            for i in range(len(data)):
                data[i].priority = cnt
                cnt += 1

            db.session.add(new_word)
            db.session.commit()

            return redirect(url_for('index'))
        except:
            return "There was an issue when add new word!"

    return render_template('vocabulary.html')

@app.route('/update/<int:voc_id>', methods=('GET', 'POST'))
def update(voc_id):
    data = None
    try:
        data = Voc.query.filter_by(id=voc_id).one()
    except:
        flash('No Suck Vocabulary ID')
        return render_template('update.html', data=data)

    if (request.method == 'POST'):
        data.english = request.form['english']
        data.vietnamese = request.form['vietnamese']
        data.pronounciation = request.form['pronounciation']
        data.note = request.form['note']
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('update.html', data=data)

@app.route('/delete/<int:voc_id>')
def delete(voc_id):
    data = Voc.query.filter_by(id=voc_id).all()
    if (len(data) > 0):
        data = data[0]
    try:
        db.session.delete(data)
        db.session.commit()
    except:
        return 'There was an issue when delete vocabulary'
    return redirect(url_for('index'))

@app.route('/setting', methods=('GET', 'POST'))
def setting():
    if request.method == 'POST':
        selectedIndex = request.form['voiceSelect']
        data = User.query.filter_by(id=g.user.id).one()
        data.voice = int(selectedIndex)
        data.days = int(request.form['days'])
        data.hours = int(request.form['hours'])
        data.minutes = int(request.form['minutes'])
        data.seconds = int(request.form['seconds'])
        db.session.commit();
        return redirect(url_for('index'))
    return render_template('setting.html')

@app.route('/remove_user/<int:id>')
def remove_user(id):
    try:
        usr = User.query.filter_by(id=id).one()
        words = Voc.query.filter_by(author_id=id).all()
        db.session.delete(usr)
        for word in words:
            db.session.delete(word)
        db.session.commit()
    except:
        print("Can't remove user with id {}".format(id))
    return redirect(url_for('index'))

@app.route('/secret_route')
def secret_route():
    if (g.user.username != 'tuanio'):
        return redirect(url_for('index'))
    return render_template('secret_route.html')

@app.before_request
def load_user_before_request():

    user_id = session.get('user_id')

    g.user, g.vocs, g.all_user = None, [], []

    if (user_id is not None):
        g.user = User.query.filter_by(id=user_id).all()
        if (len(g.user) > 0):
            g.user = g.user[0]
        g.vocs = Voc.query.filter_by(author_id=user_id).order_by(Voc.priority).all()
        g.all_user = User.query.all()

    if (g.user == None):
        return

    if (g.vocs == []):
        session['time'] = datetime.now()

    if (g.user != None and g.user != []): 
        delta = datetime.now() - session.get('time')
        if (delta >= timedelta(days=g.user.days, hours=g.user.hours, minutes=g.user.minutes, seconds=g.user.seconds)):
            session['time'] = datetime.now()
            data = Voc.query.filter_by(author_id=user_id).order_by(Voc.priority).all()
            vocs_len = len(data)
            data[-1].priority = 1
            cnt = 2
            for i in range(vocs_len - 1):
                data[i].priority = cnt
                cnt += 1
            db.session.commit()
            g.vocs = Voc.query.filter_by(author_id=user_id).order_by(Voc.priority).all()

    column_name = Voc.__table__.columns.keys()[:-1]
    data = [{name: i.to_dict()[name] for name in column_name} for i in g.vocs]
    df = pd.DataFrame(data)
    df.to_excel('static/files/words.xlsx', encoding='utf-8-sig')
    

if __name__ == '__main__':
    app.run(debug=True)