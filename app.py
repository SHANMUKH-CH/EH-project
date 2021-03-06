import re
import db
from flask import Flask, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL, MySQLdb
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

csrf = CSRFProtect(app)

app.secret_key = 'kingkongdingdong'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'shanmukh'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        db.add_comment(request.form['comment'])
    comments = db.get_comments()
    return render_template('home.html', comments=comments)


@app.route('/login', methods=["GET", "POST"])
def login():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM registration WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('home.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=message)


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confrim']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM registration WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Bruhhh Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Bruhhh Invalid email address !'
        elif password != confirm:
            msg = 'Bruhhh Password mismatch !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Bruhhh Please fill out the form !'
        else:
            cursor.execute(
                'INSERT INTO registration VALUES (NULL, % s, % s, % s)', (username, email, password))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Bruhh Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route('/profile', methods=['GET', 'POST'])
@csrf.exempt
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM registration WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        if request.method == 'POST' and 'username' in request.form:
            username = request.form['username']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "UPDATE registration SET username= %s WHERE id=%s", (username, session['id']))
            mysql.connection.commit()
            msg = 'updated!'
            return render_template('profile.html', msg=msg, account=account)
        return render_template('profile.html', account=account)
    else:
        return render_template('login.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    # sql injection = admin1'; drop table test;
    if request.method == 'POST' and 'username' in request.form:
        username = request.form['username']
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT * FROM registration WHERE username = '%s'" % username)
        # user input is concatenated directly into the query
        # SELECT * FROM registration WHERE username = %s"(username,))
        account = cursor.fetchall()
        if account:
            return render_template('users.html', account=account)
        else:
            return ''' <h1> no such username</h1>
        <a href="{{ url_for('register') }}" class="btn">register</a>
        '''


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
