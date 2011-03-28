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
	'/manage_account', 'manage_account',
	'/register_action', 'register_action',
	'/register_form', 'register_form',
	'/widget', 'widget',
	r'/give_([^?$/\\#%\s]+)_datalove', 'give_user_datalove',
	'/logoff', 'logoff',
	'/unregister', 'unregister',
	'/reset_password_form', 'reset_password_form',
	'/reset_password_action', 'reset_password_action',
	r'/api/([^?$/\\#%\s]+)','get_users_love',
	r'/api/([^?$/\\#%\s]+)/','get_users_love',
	r'/api/([^?$/\\#%\s]+)/available_datalove', 'get_users_available_love',
	r'/api/([^?$/\\#%\s]+)/received_datalove', 'get_users_received_love',
	r'/api/([^?$/\\#%\s]+)/give_datalove', 'give_user_datalove_api',
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

## Joins two fragments of an URL path with an '/' (if needed).
# @param a The first fragment. This must contain the at least the scheme and 
#        host part of the URL.
# @param b The remainder of the URL path.
# @returns A nicely joined URL path.
def url_path_join(a, b):
	path = a
	if a.endswith('/'):
		if b.startswith('/'):
			path += b[1:]
		else:
			path += b
	else:
		if b.startswith('/'):
			path += b
		else:
			path += '/' + b
	return path

## Class for the <tt>/index</tt> URL.
class index:
	## Shows the page
	# @param login_error Possible errors (as string) that happened during login.
	# @return String in HTML code of what the side looks like
	def show(self, login_error = None):
		web.header('Content-Type','text/html;charset=utf-8')
		try:
			#web.setcookie(name='test_cookie',value=test_cookie_test, expires=60*60)
			session_id = web.cookies().get(
					web.config.session_parameters['cookie_name']
				)
			templates = web.template.render(os.path.join(abspath,'templates'))
			if not session_id or \
					not db_handler.session_associated_to_any_user(session_id):
				content = templates.welcome()
				return templates.index(content,login_error = login_error)
			else:
				nickname, _, available, received = db_handler.get_session(
						session_id
					)
				content = templates.userpage(nickname,received,available)
				return templates.index(content,nickname != None,login_error)
		except BaseException, e:
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)
	
	## Handles what happens on login
	def login_action(self):
		import hashlib
		i = web.input()
		session_id = get_session_id()
		nickname = i.nickname
		password = dbh.hash_password(nickname,i.password)
		db_handler.user_login(nickname,password,session_id)
	
	## Method for a HTTP GET request. 
	def GET(self):
		return self.show()
	
	## Method for a HTTP POST request. 
	def POST(self):
		try:
			self.login_action()
		except AssertionError, e:
			return self.show(e)
		except dbh.LoginException:
			return self.show(
					'Password not associated to nickname.'
				)
		except BaseException, e:
			web.header('Content-Type','text/html;charset=utf-8')
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)
		raise web.seeother(config.host_url)

## Class for the <tt>/manage_account</tt> URL, i. e. forms for changing email
#  address and password.
class manage_account:
	## Shows the page
	# @param email_change_error Possible errors (as string) that happened 
	#        during the change of the email address.
	# @param pw_change_error Possible errors (as string) that happened 
	#        during the change of the password.
	# @return String in HTML code of what the side looks like
	def show(self, email_change_error = None, pw_change_error = None):
		web.header('Content-Type','text/html;charset=utf-8')
		try:
			session_id = web.cookies().get(
					web.config.session_parameters['cookie_name']
				)
			templates = web.template.render(os.path.join(abspath,'templates'))
			if session_id and \
					db_handler.session_associated_to_any_user(session_id):
				nickname, email, _, _ = db_handler.get_session(
						session_id
					)
				content = templates.manage_account(
						nickname,
						email,
						email_change_error,
						pw_change_error
					)
				return templates.index(content,nickname != None)
		except BaseException, e:
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)
		raise web.seeother(config.host_url)
		
	## Method for a HTTP GET request. 
	def GET(self):
		return self.show()
	
	## Method for a HTTP POST request. 
	def POST(self):
		try:
			session_id = get_session_id()
			nickname, _, _, _ = db_handler.get_session(session_id)
			
			i = web.input() 
			
			
			session_id = get_session_id()
			user, _, _, _ = db_handler.get_session(session_id)
			i = web.input()
			email = i.get('email')
			old_password = i.get('old_password')
			new_password = i.get('new_password')
			new_password_conf = i.get('new_password_conf')
			
			if email:
				try:
					db_handler.change_email_address(user,session_id,email)
				except dbh.LoginException, e:
					return self.show(email_change_error = e)
				except AssertionError, e:
					return self.show(email_change_error = e)
			elif old_password and new_password and new_password_conf:
				if new_password != new_password_conf:
					return self.show(
							pw_change_error = "New password and confirmation " +
									"of new password were not equal."
						)
			
				old_password = dbh.hash_password(
					nickname,old_password
				)
				new_password = dbh.hash_password(
					nickname,new_password
				)
				try:
					db_handler.change_password(
							nickname,
							old_password,
							new_password
						)
				except dbh.LoginException, e:
					return self.show(pw_change_error = e)
		except BaseException, e:
			web.header('Content-Type','text/html;charset=utf-8')
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)
		raise web.seeother(url_path_join(config.host_url,'manage_account'))
		
## Class for the <tt>/register_form</tt> URL.
class register_form:
	## Method for a HTTP GET request. 
	def GET(self):
		try:
			web.header('Content-Type','text/html;charset=utf-8')
			templates = web.template.render(os.path.join(abspath,'templates'))
			return templates.register_form()
		except BaseException, e:
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)

## Class for the <tt>/register_action</tt> URL.
class register_action:
	## Method for a HTTP POST request. 
	def POST(self):
		web.header('Content-Type','text/html;charset=utf-8')
		try:
			import hashlib
			i = web.input()
			if i.password != i.conf_password:
				return "Password and confirmation of password "+ \
						"were not equal."
			nickname = i.nickname
			password = dbh.hash_password(nickname,i.password)
			email = i.email
			db_handler.create_user(nickname,password,email)
		except AssertionError, e:
			return str(e)
		except dbh.UserException, e:
			return str(e)
		except BaseException, e:
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)
		raise web.seeother(config.host_url)
	## Method for a HTTP GET request. 
	def GET(self):
		raise web.seeother(url_path_join(config.host_url,'register_form'))

## Class for the <tt>/widget</tt> URL.
class widget:
	## Method for a HTTP GET request. 
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		try:
			i = web.input()
			user = i.user
			received_love = db_handler.get_received_love(user)
			templates = web.template.render(os.path.join(abspath,'templates'))
			return templates.widget(user,received_love)
		except dbh.UserException,e:
			return str(e)
		except AttributeError:
			raise web.seeother(url_path_join(config.host_url,'register_form'))
		except BaseException, e:
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)

## Class for the <tt>/give_([^?$/\\#%\s]+)_datalove</tt> URL where the regular 
#  expression stands for the user's name.
class give_user_datalove:
	## Method for a HTTP GET request. 
	# @param to_user User the datalove should be given to.
	def GET(self,to_user):
		web.header('Content-Type','text/html;charset=utf-8')
		try:
			logged_in = True
			if not db_handler.user_exists(to_user):
				return "User does not exist."
			session_id = get_session_id()
			from_user, _, _, _ = db_handler.get_session(session_id)
		except dbh.IllegalSessionException, e:
			logged_in = False
		except AssertionError,e:
			return str(e)
		except BaseException, e:
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)
		if logged_in:
			try:
				db_handler.send_datalove(from_user,to_user,session_id)
			except AssertionError,e:
				return str(e)
			except dbh.NotEnoughDataloveException, e:
				return str(e)
			except BaseException, e:
				web.ctx.status = '500 Internal Server Error'
				return '<b>Internal Server Error:</b> ' + str(e)
			raise web.seeother(
					url_path_join(config.host_url,'widget?user='+to_user)
				)
		else:
			raise web.seeother(config.host_url)

## Class for the <tt>/logoff</tt> URL.
class logoff:
	## Method for a HTTP GET request. 
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		try:
			session_id = get_session_id()
			nickname, _, _, _ = db_handler.get_session(session_id)
			db_handler.user_logoff(nickname,session_id)
			session.kill()
		except BaseException, e:
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)
		raise web.seeother(config.host_url)

## Class for the <tt>/unregister</tt> URL.
class unregister:
	## Method for a HTTP GET request. 
	def GET(self):
		try:
			web.header('Content-Type','text/html;charset=utf-8')
			
			session_id = get_session_id()
			user, _, _, _ = db_handler.get_session(session_id)
			db_handler.drop_user(user,session_id)
		except BaseException, e:
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)
		raise web.seeother(config.host_url)

## Class for the <tt>/reset_password_form</tt> URL.
class reset_password_form:
	## Method for a HTTP GET request. 
	def GET(self):
		web.header('Content-Type','text/html;charset=utf-8')
		try:
			templates = web.template.render(os.path.join(abspath,'templates'))
			return templates.reset_password_form()
		except BaseException, e:
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)

## Class for the <tt>/reset_password_action</tt> URL.
class reset_password_action:
	## Method for a HTTP POST request. 
	def POST(self):
		web.header('Content-Type','text/html;charset=utf-8')
		try:
			import smtplib
			from email.mime.text import MIMEText
			i = web.input()
			try:
				new_password, email_to = db_handler.reset_password(i.nickname)
			except UserException, e:
				return str(e)
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
		except BaseException, e:
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)
	## Method for a HTTP GET request. 
	def GET(self):
		raise web.seeother(url_path_join(config.host_url,'/reset_password_form'))

## Class for the <tt>/api/([^?$/\\#%\s]+)/</tt> URL where the regular 
#  expression stands for the user's name.
class get_users_love:
	## Method for a HTTP GET request. 
	# @param nickname The user's nickname
	def GET(self,nickname):
		web.header('Content-Type','text/html;charset=utf-8')
		try:
			if not db_handler.user_exists(nickname):
				web.ctx.status = '404 Not Found'
				return "<b>Not Found:</b> User " + nickname + " does not exist."
			available_love = db_handler.get_available_love(nickname)
			received_love = db_handler.get_received_love(nickname)
			return str(available_love) + ',' + str(received_love)
		except BaseException, e:
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)

## Class for the <tt>/api/([^?$/\\#%\s]+)/available_datalove</tt> URL where the 
#  regular expression stands for the user's name.
class get_users_available_love:
	## Method for a HTTP GET request. 
	# @param nickname The user's nickname
	def GET(self,nickname):
		web.header('Content-Type','text/html;charset=utf-8')
		try:
			if not db_handler.user_exists(nickname):
				web.ctx.status = '404 Not Found'
				return "<b>Not Found:</b> User " + nickname + " does not exist."
			available_love = db_handler.get_available_love(nickname)
			return str(available_love)
		except BaseException, e:
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)


## Class for the <tt>/api/([^?$/\\#%\s]+)/received_datalove</tt> URL where the 
#  regular expression stands for the user's name.
class get_users_received_love:
	## Method for a HTTP GET request. 
	# @param nickname The user's nickname
	def GET(self,nickname):
		web.header('Content-Type','text/html;charset=utf-8')
		try:
			if not db_handler.user_exists(nickname):
				web.ctx.status = '404 Not Found'
				return "<b>Not Found:</b> User " + nickname + " does not exist."
			received_love = db_handler.get_received_love(nickname)
			return str(received_love)
		except BaseException, e:
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)

## Class for the <tt>/api/([^?$/\\#%\s]+)/give_datalove</tt> URL where the 
#  regular expression stands for the user's name.
class give_user_datalove_api:
	## Method for a HTTP GET request. 
	# @param to_user User the datalove should be given to.
	def GET(self,nickname):
		web.header('Content-Type','text/html;charset=utf-8')
		try:
			logged_in = True
			if not db_handler.user_exists(nickname):
				web.ctx.status = '404 Not Found'
				return "<b>Not Found:</b> User " + nickname + " does not exist."
			session_id = get_session_id()
			from_user, _, _, _ = db_handler.get_session(session_id)
		except BaseException, e:
			web.ctx.status = '500 Internal Server Error'
			return '<b>Internal Server Error:</b> ' + str(e)
		if logged_in:
			try:
				db_handler.send_datalove(from_user,nickname,session_id)
			except AssertionError,e:
				return str(e)
			except dbh.NotEnoughDataloveException, e:
				return str(e)
			except BaseException, e:
				web.ctx.status = '500 Internal Server Error'
				return '<b>Internal Server Error:</b> ' + str(e)
			return ''
		else:
			raise web.seeother(config.host_url)
