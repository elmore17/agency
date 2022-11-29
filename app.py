import os

import MySQLdb.cursors
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import time
import re
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
from datetime import date

UPLOAD_FOLDER = 'static\\img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Danil2002'
app.config['MYSQL_DB'] = 'agency'

mysql = MySQL(app)


@app.route('/')
def main():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM agency.real_estate''')
    rv = cur.fetchmany(3)
    if 'logged_in' in session:
        return render_template('index.html', username=session['username'], real_estate=rv)

    return redirect(url_for('auth'))


@app.route('/profil')
def profil():
    if 'logged_in' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM client WHERE id_client = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.execute('''SELECT * FROM agency.order_client''')
        rv = cursor.fetchall()
        a = 0
        for i in rv:
            if account['id_client'] == i['id_client']:
                a = a + 1
        return render_template('profil.html', account=account, a=a)
    return redirect(url_for('auth'))


@app.route('/realest')
def realest():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM agency.real_estate''')
    rv = cur.fetchall()
    if 'logged_in' in session:
        return render_template('real_estate.html', real_estate=rv)

    return redirect(url_for('auth'))


@app.route('/addrealest')
def realestadd():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM agency.agency''')
    rv = cur.fetchall()
    if 'logged_in' in session:
        return render_template('addrealest.html', agency=rv)

    return redirect(url_for('auth'))


@app.route('/reg')
def form():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM agency.agency''')
    rv = cur.fetchall()
    return render_template('formreg.html', agency=rv)


@app.route('/aut')
def auth():
    return render_template('form.html')


@app.route('/order/<id>')
def order(id):
    if 'logged_in' in session:
        return render_template('order.html', id=id)

    return redirect(url_for('auth'))


@app.route('/orderlist')
def orderlist():
    if 'logged_in' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM client WHERE id_client = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.execute('''SELECT * FROM agency.order_client''')
        rv = cursor.fetchall()
        orders = []
        for i in rv:
            if account['id_client'] == i['id_client']:
                orders.append(i)

        return render_template('orderlist.html', orderlist=orders, account=account)

    return redirect(url_for('auth'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return "Login via the login Form"

    if request.method == 'POST':
        today = date.today()
        a1 = today.year
        a1 = int(a1)-18
        id = time.time()
        name = request.form['name']
        id_agency = request.form['agency']
        c = mysql.connection.cursor()
        c.execute('''SELECT * FROM agency.agency''')
        r = c.fetchall()
        for i in r:
            if i[1] == id_agency:
                id_agency = i[0]
        dates = request.form['date']
        a = dates.split("-")[0]
        a = int(a)
        if a>a1:
            return f"Для регистрации, вам должно быть 18+"
        number = request.form['number']
        address = request.form['address']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute('''SELECT * FROM agency.client''')
        rv = cur.fetchall()
        for i in rv:
            if i[7] == email:
                return f"Такая почта существует"
        password = request.form['pass']
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photoLink = str((os.path.join(app.config['UPLOAD_FOLDER'], filename)))
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO client VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                       (id, id_agency, name, password, dates, number, address, email, photoLink))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('auth'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/addestate', methods=['POST', 'GET'])
def addestate():
    if request.method == 'GET':
        return "Addest via the Form"

    if request.method == 'POST':
        id = time.time()
        real_est = request.form['real_est']
        count_room = request.form['count_room']
        location = request.form['location']
        est = request.form['est']
        des = request.form['descry']
        agency = request.form['agency']
        c = mysql.connection.cursor()
        c.execute('''SELECT * FROM agency.agency''')
        r = c.fetchall()
        for i in r:
            if i[1] == agency:
                agency = i[0]
        sale = request.form['sale']
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photoLink = str((os.path.join(app.config['UPLOAD_FOLDER'], filename)))
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO real_estate VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                       (id, real_est, count_room, location, est, agency, sale, photoLink,des))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('realest'))


@app.route('/authorization', methods=['GET', 'POST'])
def authorization():
    if request.method == 'POST' and 'email' in request.form and 'pass' in request.form:
        username = request.form['email']
        password = request.form['pass']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM client WHERE passpot = %s AND email = %s', (password, username))
        account = cursor.fetchone()
        if account:
            session['logged_in'] = True
            session['id'] = account['id_client']
            session['username'] = account['email']
            return redirect(url_for('main'))
        else:
            msg = 'Incorrect username/password!'
    return redirect(url_for('form'))


@app.route('/orderclient', methods=['POST', 'GET'])
def orderclient():
    if request.method == 'GET':
        return "Order via the Form"

    if request.method == 'POST':
        today = date.today()
        a1 = today.year
        a1 = int(a1)
        b1 = today.month
        b1 = int(b1)
        c1 = today.day
        c1 = int(c1)
        id = time.time()
        textcl = request.form['text']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM client WHERE id_client = %s', (session['id'],))
        account = cursor.fetchone()
        id_client = account['id_client']
        id_employee = 1
        number = request.form['number']
        FC = account['FCs']
        dates = request.form['data']
        a = dates.split("-")[0]
        a = int(a)
        b = dates.split("-")[1]
        b = int(b)
        c = dates.split("-")[2]
        c = int(c)
        if a < a1 or b<b1 or c<c1:
            return f"Дата не может быть меньше текущей"
        id_agency = 1
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO order_client VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',
                       (id, id_client, id_employee, number, FC, dates, textcl, id_agency))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('realest'))


@app.route('/authorization/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('auth'))


app.run(host='localhost', port=5000)
