from __future__ import with_statement
from sqlite3 import dbapi2 as sqlite3
from contextlib import closing
from flask import Flask, request, session, g,redirect,\
	url_for, abort, render_template,flash,json

DATABASE='flaskr.db'
DEBUG=True
SECRET_KEY='secret'
USERNAME='admin'
PASSWORD='admin'

app=Flask(__name__)

app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
	'''try:
		db=open(DATABASE).read()
		print db
	except IOError:
		db='{"entries":[]}'
	g.db=json.loads(db)
	'''
	g.db=connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()
	
	'''
	if hasattr(g,'db'):
		open(DATABASE,'w').wrtie(json.dumps(g.db))
	'''

@app.route('/')
def show_entries():
	cur=g.db.execute('select title, text from entries order by id desc')
	entries=[dict(title=row[0],text=row[1]) for row in cur.fetchall()]
	return render_template('show_entries.html', entries=entries)
	#return render_template('show_entries.html',entries=g.db['entries'])

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		print 'abort'
		abort(401)
	#g.db['entries'].insert(0,{'title':request.form['title'],'text':request.form['text']})

	g.db.execute('insert into entries (title, text) values (?, ?)',
			[request.form['title'], request.form['text']])
	print session.get('logged_in')
	g.db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET','POST'])
def login():
	error=None
	print request.method
	print app.config['USERNAME']

	if request.method=='POST':
		if request.form['username'] != 'admin':
			error ='Invalid username'
		elif request.form['password'] != 'admin':
			error ='Invalid password'
		else:
			session['logged_in']=True
			flash('You were logged in')
			return redirect(url_for('show_entries'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in',None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))

if __name__=='__main__':
	init_db()
	app.run()

