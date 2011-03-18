## @package app
#  @author datalove.me
#  @brief Application script for web.py/wsgi
#  @see <a href="http://webpy.org/docs/0.3/">Web.py Documentation</a>
#
#  No Copyright, no license, comes as it is

import web,os,config

import db_handling as dbh

web.config.debug = False
web.config.session_parameters['cookie_name'] = 'give_datalove_session_id'
web.config.session_parameters['timeout'] = 2 * 7 * 24 * 60 * 60
		# 2 weeks in seconds
web.config.session_parameters['ignore_expiry'] = False 

## Text for a test cookie to implement cookie-less, URL-based Session Management
#  later on for users that do not want to use cookies.
test_cookie_text = 'Do you accept cookies?' 

## URL-Map that maps the urls to the respective classes 
# @see <a href="http://webpy.org/docs/0.3/">Web.py Documentation</a>
urls = (
	'/', 'index',
	'/register_action', 'register_action',
	'/register_form', 'register_form',
	'/login_action', 'login_action',
	'/login_form', 'login_form',
	'/widget', 'widget',
	'/give_(.+)_datalove', 'give_user_datalove',
	'/logoff', 'logoff',
	'/unregister', 'unregister',
	'/reset_password_form', 'reset_password_form',
	'/reset_password_action', 'reset_password_action',
	'/change_mail_address_action','change_mail_address_action',
	'/change_password_action', 'change_password_action'
)

## The absolute path of this script.
abspath = os.path.dirname(__file__)

## The web.py <tt>web.db.DB</tt> object to connect to the applications database.
db = web.database(
		dbn=config.db_engine, 
		db=config.db_name, 
		user=config.db_username, 
		pw=config.db_password
	)

## The db_handling.DBHandler to wrap the applications database operations.
db_handler = dbh.DBHandler(db)

## The web.py <a href="http://webpy.org/docs/0.3/api#web.application"><tt>
#  application</tt></a> object.
app = web.application(urls, globals())

## The Session store
store = web.session.DBStore(db, 'sessions')

## The applications session object.
session = web.session.Session(app, store)

## The mod_wsgi application function.
#  @see <a href="https://code.google.com/p/modwsgi/wiki/WhereToGetHelp?tm=6">
#       mod_wsga Documentation</a>
application = app.wsgifunc()	# get web.py application as wsgi application

## Get the session id from a cookie (or in later implementations the URL).
#  @returns The current session's session ID.
def get_session_id():
	#test = web.cookies().get('test_cookie')
	#if test == test_cookie_text:
	session_id = web.cookies().get(web.config.session_parameters['cookie_name'])
	#else:
	#	session_id = web.input().get('sid')
	return session_id

## Class for the <tt>/index</tt> URL.
class index:
	## Method for a HTTP GET request. 
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		logged_in = True
		#web.setcookie(name='test_cookie',value=test_cookie_test, expires=60*60)
		try:
			session_id = web.cookies().get(
					web.config.session_parameters['cookie_name']
				)
			if not session_id:
				i = web.input()
				session_id = i.get('sid')
			if not session_id:
				user = None
				email = None
				available = None
				received = None
				logged_in = False
			else:
				user, email, available, received = db_handler.get_session(
						session_id
					)
		except dbh.IllegalSessionException:
			user = None
			email = None
			available = None
			received = None
			logged_in = False
		templates = web.template.render(os.path.join(abspath,'templates'))
		return templates.index(logged_in, user, email, available, received)

## Class for the <tt>/register_form</tt> URL.
class register_form:
	## Method for a HTTP GET request. 
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		templates = web.template.render(os.path.join(abspath,'templates'))
		return templates.register_form()

## Class for the <tt>/register_action</tt> URL.
class register_action:
	## Method for a HTTP POST request. 
	def POST(self):
		web.header('Content-Type','text/html;charset=utf-8')
		import hashlib
		i = web.input()
		try:
			nickname = i.nickname
			password = dbh.hash_password(nickname,i.password)
			email = i.email
			db_handler.create_user(nickname,password,email)
			raise web.seeother('login_form')
		except AssertionError, e:
			return e
	## Method for a HTTP GET request. 
	def GET(self):
		raise web.seeother('/register_form')

## Class for the <tt>/login_form</tt> URL.
class login_form:
	## Method for a HTTP GET request. 
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		session_id = get_session_id()
		try:
			_, _, _, _ = db_handler.get_session(session_id)
			raise web.seeother('/')
		except dbh.LoginException:
			pass
		except AssertionError:
			pass
		templates = web.template.render(os.path.join(abspath,'templates'))
		return templates.login_form()

## Class for the <tt>/login_action</tt> URL.
class login_action:
	## Method for a HTTP POST request. 
	def POST(self):
		web.header('Content-Type','text/html;charset=utf-8')
		import hashlib
		i = web.input()
		try:
			session_id = get_session_id()
			nickname = i.nickname
			password = dbh.hash_password(nickname,i.password)
			db_handler.user_login(nickname,password,session_id)
			raise web.seeother('/')
		except AssertionError, e:
			return e
		except dbh.LoginException:
			return 'Login failed: Nickname or password was wrong. ' + \
					'<a href="reset_password_form">Reset password?</a>'
	## Method for a HTTP GET request. 
	def GET(self):
		raise web.seeother('/login_form')

## Class for the <tt>/widget</tt> URL.
class widget:
	## Method for a HTTP GET request. 
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		i = web.input()
		try:
			user = i.user
			received_love = db_handler.get_received_love(user)
		except AttributeError:
			raise web.seeother('register_form')
		except UserException,e:
			return e
		templates = web.template.render(os.path.join(abspath,'templates'))
		return templates.widget(user,received_love)

## Class for the <tt>/give_(.*)_datalove</tt> URL where the regular expression 
#  stands for the user's name.
class give_user_datalove:
	## Method for a HTTP GET request. 
	# @param to_user User the datalove should be given to.
	def GET(self,to_user):
		web.header('Content-Type','text/html;charset=utf-8')
		logged_in = True
		if not db_handler.user_exists(to_user):
			return "User does not exist."
		session_id = get_session_id()
		try:
			from_user, _, _, _ = db_handler.get_session(session_id)
		except dbh.IllegalSessionException, e:
			logged_in = False
		except AssertionError,e:
			return e
		except dbh.NotEnoughDataloveException, e:
			return "You have not enough datalove to spend :(\n Wait until " + \
					"next month, then you'll get some new or until someone " + \
					"gives you datalove."
		
		if logged_in:
			try:
				db_handler.send_datalove(from_user,to_user,session_id)
			except AssertionError,e:
				return e
			raise web.seeother('widget?user='+to_user)
		else:
			raise web.seeother('login_form')

## Class for the <tt>/logoff</tt> URL.
class logoff:
	## Method for a HTTP GET request. 
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		session_id = get_session_id()
		nickname, _, _, _ = db_handler.get_session(session_id)
		db_handler.user_logoff(nickname,session_id)
		session.kill()
		raise web.seeother('/')

## Class for the <tt>/unregister</tt> URL.
class unregister:
	## Method for a HTTP GET request. 
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		session_id = get_session_id()
		user, _, _, _ = db_handler.get_session(session_id)
		db_handler.drop_user(user,session_id)
		
		raise web.seeother('/')

## Class for the <tt>/reset_password_form</tt> URL.
class reset_password_form:
	## Method for a HTTP GET request. 
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		templates = web.template.render(os.path.join(abspath,'templates'))
		return templates.reset_password_form()

## Class for the <tt>/reset_password_action</tt> URL.
class reset_password_action:
	## Method for a HTTP POST request. 
	def POST(self):
		import smtplib
		from email.mime.text import MIMEText
		web.header('Content-Type','text/html;charset=utf-8')
		i = web.input()
		try:
			new_password, email_to = db_handler.reset_password(i.nickname)
		except UserException, e:
			return e
		email_from = 'password-reset@give.datalove.me'
		
		msg_text = "Hello "+i.nickname+",\n"+ \
			"You're password was reset to '" + new_password + \
			"'. Please change it immediately!\n\n" + \
			"Greets, Your datalove.me-Team\n"
		msg = MIMEText(msg_text)
		
		msg['Subject'] = 'Your new password for give.datalove.me'
		msg['From'] = email_from
		msg['To'] = email_to
		
		s = smtplib.SMTP('localhost')
		s.sendmail(email_from,[email_to],msg.as_string())
		s.quit()
		
		return 'Password reset successfully. you should get an e-mail to ' + \
				'the address you are registered to.'
	## Method for a HTTP GET request. 
	def GET(self):
		raise web.seeother('/reset_password_form')

## Class for the <tt>/change_mail_address_action</tt> URL.
class change_mail_address_action:
	## Method for a HTTP POST request. 
	def POST(self):
		session_id = get_session_id()
		user, _, _, _ = db_handler.get_session(session_id)
		email = web.input().get('email')
		db_handler.change_email_address(user,session_id,email)
		raise web.seeother('/')
	## Method for a HTTP GET request. 
	def GET(self):
		raise web.seeother('/')

## Class for the <tt>/change_password_action</tt> URL.
class change_password_action:
	## Method for a HTTP POST request. 
	def POST(self):
		session_id = get_session_id()
		nickname, _, _, _ = db_handler.get_session(session_id)
		old_password = dbh.hash_password(
				nickname,web.input().get('old_password')
			)
		new_password = dbh.hash_password(
				nickname,web.input().get('new_password')
			)
		db_handler.change_password(nickname,old_password,new_password)
		raise web.seeother('/')
	## Method for a HTTP GET request. 
	def GET(self):
		raise web.seeother('/')
