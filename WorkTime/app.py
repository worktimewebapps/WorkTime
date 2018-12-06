from flask import Flask, render_template, flash, redirect, url_for, session, logging, session, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

#Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'work'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'   
# app.config['CLEARDB_DATABASE_URL'] = ''      




mysql = MySQL(app)


@app.route('/')
def main():
	make_admin()
	return render_template('index.html')



#-------------------------------FORMS--------------------------------------#

# Registration form class
class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message="Passwords do not match")
	])
	confirm = PasswordField('Confirm Password')

# Scheduler form
class SchedulerForm(Form):
	username = StringField('Username', [validators.Length(min=1, max=50)])
	dayofweek = StringField('Day of Week', [validators.Length(min=4, max=25)])
	starttime = StringField('Start Time', [validators.Length(min=1, max=10)])
	endtime = StringField('End Time', [validators.Length(min=1, max=10)])

# Scheduler form
class ShiftEditForm(Form):
	dayofweek = StringField('Day of Week', [validators.Length(min=4, max=25)])
	starttime = StringField('Start Time', [validators.Length(min=1, max=10)])
	endtime = StringField('End Time', [validators.Length(min=1, max=10)])

#--------------------------------------------------------------------------#





# Makes Admin on login or dropscreen
def make_admin():
	curr = mysql.connection.cursor()
	results = curr.execute("SELECT * FROM tbl_user WHERE admin = true")
	curr.close()

	if results < 1:
		aname = 'Administrator'
		ausername = 'admin'
		adminpass = 'admin'
		passadmin = sha256_crypt.encrypt(str(adminpass))
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO tbl_user(name, username, password, admin) VALUES (%s,%s, %s, true)", (aname, ausername, passadmin))
		mysql.connection.commit()
		cur.close()



# Check to see if admin
def is_admin(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		chk = session['is_admin']
		if (chk==1):
			# app.logger.info(session['is_admin'])   ---- left comment in to show how to print to the console
			return f(*args, **kwargs)
		else:
			flash('You must be an administrator', 'danger')
			return(redirect(url_for('dashboard')))
	return wrap



# Check to see if logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if('logged_in' in session):
			return f(*args, **kwargs)
		else:
			flash('Please login', 'danger')
			return(redirect(url_for('login')))
	return wrap




# Register User
@app.route('/register', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO tbl_user(name, username, password, admin) VALUES (%s,%s,%s,false)", (name, username, password))
		mysql.connection.commit()
		cur.close()

		flash(u"User has been registered", "success")
		redirect(url_for('main'))
	return render_template('register.html', form=form)



# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
	make_admin()
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
			admin = data['admin']

			# Compare passwords
			if sha256_crypt.verify(password_pre, password):
				session['is_admin'] = admin
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
	username = session['username']
	cur = mysql.connection.cursor()
	cur.execute('SELECT username, dayofweek, starttime, endtime FROM tbl_times WHERE username = %s', [username])
	data = cur.fetchall()
	cur.close()
	# app.logger.info(results)
	return render_template('dashboard.html', articles=data)



# Delete User
@app.route('/deleteuser/<string:username>')
@is_logged_in
@is_admin
def deleteuser(username):
	cur = mysql.connection.cursor()
	cur.execute('DELETE from tbl_user WHERE username = %s', [username])
	cur.execute('DELETE from tbl_times WHERE username = %s', [username])
	mysql.connection.commit()
	return redirect(url_for('allemployeetimes'))


# Scheduler
@app.route('/scheduler', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def scheduler():
	form = SchedulerForm(request.form)
	cur = mysql.connection.cursor()
	if request.method == 'POST' and form.validate():
		username = form.username.data
		dayofweek = form.dayofweek.data
		starttime = form.starttime.data
		endtime = form.endtime.data

		result = cur.execute("SELECT * FROM tbl_user WHERE username = %s", [username])

		if result < 1:
			error = "User does not exist"
			return render_template('scheduler.html', error=error, form=form)
		
		cur.execute("INSERT INTO tbl_times(username, dayofweek, starttime, endtime) VALUES (%s,%s,%s,%s)", (username, dayofweek, starttime, endtime))
		mysql.connection.commit()
		

		flash(u"Successfully Added", "success")

	cur.execute('SELECT name, username FROM tbl_user')
	nameuser = cur.fetchall()
	cur.close()
	return render_template('scheduler.html', form=form, nameuser=nameuser)
	

# Clear all
@app.route('/clearall')
@is_logged_in
def clearall():
	cur = mysql.connection.cursor()
	cur.execute('DELETE from tbl_times WHERE username <> "admin"')
	mysql.connection.commit()
	cur.close()
	return redirect(url_for('allemployeetimes'))



# Employees
@app.route('/allemployeetimes')
@is_logged_in
@is_admin
def allemployeetimes():

	cur= mysql.connection.cursor()
	cur.execute('SELECT name, username FROM tbl_user')
	names = cur.fetchall()

	cur.execute('SELECT * FROM tbl_times')
	data = cur.fetchall()

	for x in data:
		name = x['username']
		cur.execute('SELECT name FROM tbl_user WHERE username = %s', [name])
		res = cur.fetchone()

		x['name'] = res['name']

	# app.logger.info(data)

	cur.close()
	return render_template('allemployeetimes.html', data=data, names=names)



# Delete Shift
@app.route('/deleteshift/<string:id>')
@is_logged_in
@is_admin
def deleteshift(id):
	
	cur = mysql.connection.cursor()
	cur.execute("DELETE from tbl_times WHERE id = %s", [id])
	mysql.connection.commit()

	flash("Deleted shift", "success")
	return redirect(url_for('allemployeetimes'))



# Edit Shift
@app.route('/editshift/<string:id>/', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def editshift(id):
	form = ShiftEditForm(request.form)
	cur = mysql.connection.cursor()

	cur.execute('SELECT * FROM tbl_times WHERE id = %s', [id])
	shift = cur.fetchone()

	if request.method == 'POST' and form.validate():
		dayofweek = form.dayofweek.data
		starttime = form.starttime.data
		endtime = form.endtime.data

		cur.execute("UPDATE tbl_times SET dayofweek=%s, starttime=%s, endtime=%s WHERE id = %s ", (dayofweek,starttime,endtime,id))

		mysql.connection.commit()

		flash("Edit Success", "success")
	
	return render_template('editshift.html', form=form, shift=shift)



# Main
if __name__ == '__main__':
	app.secret_key='secret123'
	app.run()




