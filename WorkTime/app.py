from flask import Flask, render_template, flash, redirect, url_for, session, logging, session, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

#Config MySQL
app.config['MYSQL_HOST'] = 'localhost:3306'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pokie123'
app.config['MYSQL_DB'] = 'work'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def main():
	return render_template('index.html')




# Registration form class
class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message="Passwords do not match")
	])
	confirm = PasswordField('Comfirm Password')


# Register User
@app.route('/register', methods = ['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO tbl_user(name, username, password) VALUES (%s,%s,%s)", (name, username, password))
		mysql.connection.commit()
		cur.close()

		flash(u"You are now registered and can login", "success")
		redirect(url_for('main'))
	return render_template('register.html', form=form)



# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method=='POST':
		# Get form fields
		username = request.form['username']
		password_pre = request.form['password']

		# Create cursor

		cur = mysql.connection.cursor()

		result = cur.execute("SELECT * FROM tbl_user WHERE username = %s", [username])

		if result > 0:
			data = cur.fetchone()
			password = data['password']
			name = data['name']


			# Compare passwords
			if sha256_crypt.verify(password_pre, password):
				session['logged_in'] = True
				session['username'] = username
				session['name'] = name

				flash('You are now logged in', 'success')
				return redirect(url_for('dashboard'))
			else:
				error = 'Invalid login'
				return render_template('login.html', error=error)

			cur.close()

		else:
			error = 'Username not found'
			return render_template('login.html', error=error)
	return render_template('login.html')

def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if('logged_in' in session):
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, please login', 'danger')
			return(redirect(url_for('login')))
	return wrap
# Logout
@app.route('/logout')
def logout():
	session.clear()
	flash('You have been successfully logged out', 'success')
	return redirect(url_for('login'))


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	return render_template('dashboard.html')



if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug=True)












