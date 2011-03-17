##
# No Copyright, no license, comes as it is

import web,os,config

import db_handling as dbh

web.config.debug = False
web.config.session_parameters['cookie_name'] = 'give_datalove_session_id'
web.config.session_parameters['timeout'] = 2 * 7 * 24 * 60 * 60	# 2 weeks in seconds
web.config.session_parameters['ignore_expiry'] = False 

test_cookie_text = 'Do you accept cookies?'

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

abspath = os.path.dirname(__file__)

db = web.database(
		dbn=config.db_engine, 
		db=config.db_name, 
		user=config.db_username, 
		pw=config.db_password
	)

db_handler = dbh.DBHandler(db)
app = web.application(urls, globals())	# get web.py application
store = web.session.DBStore(db, 'sessions')
session = web.session.Session(app, store)
application = app.wsgifunc()	# get web.py application as wsgi application

def get_session_id():
	#test = web.cookies().get('test_cookie')
	#if test == test_cookie_text:
	session_id = web.cookies().get(web.config.session_parameters['cookie_name'])
	#else:
	#	session_id = web.input().get('sid')
	return session_id

class index:
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		logged_in = True
		#web.setcookie(name='test_cookie',value=test_cookie_test, expires=60*60)
		try:
			session_id = web.cookies().get(web.config.session_parameters['cookie_name'])
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
				user, email, available, received = db_handler.get_session(session_id)
		except dbh.IllegalSessionException:
			user = None
			email = None
			available = None
			received = None
			logged_in = False
		templates = web.template.render(os.path.join(abspath,'templates'))
		return templates.index(logged_in, user, email, available, received)

class register_form:
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		templates = web.template.render(os.path.join(abspath,'templates'))
		return templates.register_form()

class register_action:
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
	def GET(self):
		raise web.seeother('/register_form')

class login_form:
	def GET(self,nickname=None):
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

class login_action:
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
			return 'Login failed: Nickname or password was wrong. <a href="reset_password_form">Reset password?</a>'
	def GET(self):
		raise web.seeother('/login_form')

class widget:
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		i = web.input()
		try:
			user = i.user
		except AttributeError:
			raise web.seeother('register_form')
		received_love = db_handler.get_received_love(user)
		templates = web.template.render(os.path.join(abspath,'templates'))
		return templates.widget(user,received_love)

class give_user_datalove:
	def GET(self,to_user):
		web.header('Content-Type','text/html;charset=utf-8')
		logged_in = True
		session_id = get_session_id()
		try:
			from_user, _, _, _ = db_handler.get_session(session_id)
		except dbh.IllegalSessionException, e:
			logged_in = False
		except AssertionError,e:
			return e
		except dbh.NotEnoughDataloveException, e:
			return "You have not enough datalove to spend :(\n Wait until next month, then you'll get some new or until someone gives you datalove."
		
		if logged_in:
			try:
				db_handler.send_datalove(from_user,to_user,session_id)
			except AssertionError,e:
				return e
			raise web.seeother('widget?user='+to_user)
		else:
			raise web.seeother('login_form')

class logoff:
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		session_id = get_session_id()
		nickname, _, _, _ = db_handler.get_session(session_id)
		db_handler.user_logoff(nickname,session_id)
		session.kill()
		raise web.seeother('/')

class unregister:
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		session_id = get_session_id()
		user, _, _, _ = db_handler.get_session(session_id)
		db_handler.drop_user(user,session_id)
		
		raise web.seeother('/')

class reset_password_form:
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		templates = web.template.render(os.path.join(abspath,'templates'))
		return templates.reset_password_form()

class reset_password_action:
	def POST(self):
		import smtplib
		from email.mime.text import MIMEText
		web.header('Content-Type','text/html;charset=utf-8')
		i = web.input()
		
		new_password, email_to = db_handler.reset_password(i.nickname)
		email_from = 'password-reset@give.datalove.me'
		
		msg_text = "Hello "+i.nickname+",\n"+ \
			"You're password was reset to '"+new_password+"'. Please change it immediately!\n\n" + \
			"Greets, Your datalove.me-Team\n"
		msg = MIMEText(msg_text)
		
		msg['Subject'] = 'Your new password for give.datalove.me'
		msg['From'] = email_from
		msg['To'] = email_to
		
		s = smtplib.SMTP('localhost')
		s.sendmail(email_from,[email_to],msg.as_string())
		s.quit()
		
		return 'Password reset successfully. you should get an e-mail to the address you are registered to.'
	def GET(self):
		raise web.seeother('/reset_password_form')

class change_mail_address_action:
	def POST(self):
		session_id = get_session_id()
		user, _, _, _ = db_handler.get_session(session_id)
		email = web.input().get('email')
		db_handler.change_email_address(user,session_id,email)
		raise web.seeother('/')
	def GET(self):
		raise web.seeother('/')

class change_password_action:
	def POST(self):
		session_id = get_session_id()
		nickname, _, _, _ = db_handler.get_session(session_id)
		old_password = dbh.hash_password(nickname,web.input().get('old_password'))
		new_password = dbh.hash_password(nickname,web.input().get('new_password'))
		db_handler.change_password(nickname,old_password,new_password)
		raise web.seeother('/')
	def GET(self):
		raise web.seeother('/')
