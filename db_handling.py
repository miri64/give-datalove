## @package db_handling
#  @author datalove.me
#  @brief Manages all database accesses of the web application. For database access it uses web.py's 
#  <a href="http://webpy.org/docs/0.3/api#web.db"><tt>db</tt> module</a>
#
#  No Copyright, no license, comes as it is

import web
from datetime import datetime
import hashlib

## The default value for the amount of datalove a user gets on account creation
DEFAULT_STARTING_LOVE = 5

## The default value for the amount of datalove a user gets on the first day of a month
DEFAULT_UPDATE_LOVE = 5

## The maximum length of a user's <tt>nickname</tt> as defined in datalovers_db.sql
MAX_NICK_LEN = 23

## The maximum length of a user's <tt>email</tt> address as defined in datalovers_db.sql
MAX_MAIL_LEN = 30

## The length of the password's hash. With SHA-256 as used in this module, it is 64 characters.
PW_HASH_LEN = 64

## This Exception is raised in any situation that causes errors with login data, like the user's <tt>nickname</tt> or
#  <tt>password</tt>, the <tt>session_id</tt>, or the mere existence of an user.
#  @extends Exception
class LoginException(Exception):
	## The constructor.
	#  @param value the value that represents the error, like an error message or error id.
	def __init__(self, value):
		self.value = value
	
	## The to-string definition.
	#  @returns value the value that represents the error, like an error message or error id.
	def __str__(self):
		return repr(self.value)

## This Exception is raised in any situation that causes errors with the <tt>session_id</tt>.
class IllegalSessionException(LoginException):
	## The constructor.
	#  @param value the value that represents the error, like an error message or error id.
	def __init__(self, value):
		self.value = value
	
	## The to-string definition.
	#  @returns value the value that represents the error, like an error message or error id.
	def __str__(self):
		return repr(self.value)

## This Exception is raised in any situation that involves the existence of users.
class UserException(LoginException):
	## The constructor.
	#  @param value the value that represents the error, like an error message or error id.
	def __init__(self, value):
		self.value = value
	
	## The to-string definition.
	#  @returns value the value that represents the error, like an error message or error id.
	def __str__(self):
		return repr(self.value)

## This Exception is raised in any situation that involves the existence of users.
class WrongPasswordException(LoginException):
	## The constructor.
	#  @param value the value that represents the error, like an error message or error id.
	def __init__(self, value):
		self.value = value
	
	## The to-string definition.
	#  @returns value the value that represents the error, like an error message or error id.
	def __str__(self):
		return repr(self.value)

## This Exception is raised when a user does not have enough available datalove to give.
#  @extends Exception
class NotEnoughDataloveException(Exception):
	## The constructor.
	#  @param value the value that represents the error, like an error message or error id.
	def __init__(self, value):
		self.value = value
	
	## The to-string definition.
	#  @returns value the value that represents the error, like an error message or error id.
	def __str__(self):
		return repr(self.value)

## This function hashes the password of the user, with it's nickname to calculate the salt of the hash.
# @param nickname Used to calculate the hash salt.
# @param password password to hash.
# @return SHA-256 hash of the password as an hexadecimal number string
def hash_password(nickname,password):
	if(not nickname or not password):
		raise AssertionError("Nickname or Password not set.")
	salt = sum([ord(char) for char in nickname]) % len(nickname)
	return hashlib.sha256(str(salt) + password).hexdigest()

## This class is the wrapper for all database operations of the web application.
class DBHandler:
	## The constructor
	# @param db A web.py <tt>web.db.DB</tt> object. You can construct such an object e. g. with web.py's 
	# <tt>web.database()</tt> function
	def __init__(self,db):
		self.db = db
	
	## Creates a new user in the database table users.
	# @param nickname The new user's nickname.
	# @param password The new user's password.
	# @param email (optional) The new user's email address. If it is set, it has to contain an 
	#        <tt>'@'</tt> character, 
	# otherwise an <a href="http://docs.python.org/release/2.5.2/lib/module-exceptions.html#l2h-101">
	# <tt>AssertionError</tt></a> is raised.
	# @param available_love (optional) The available love the user gets on account creation. By default it is set
	#        on the value of <tt>\ref DEFAULT_STARTING_LOVE</tt>.
	# @param pw_as_hash (optional) Flag to determine whether the password comes as a hash or in clear text. By default
	#        it is set to <tt><b>True</b></tt> i. e. the function asserts <i>password</i> value as a hash. If
	#        <i>password</i> has in this case not the length defined by <tt>\ref PW_HASH_LEN</tt> a 
	#        <tt>\ref WrongPasswordException</tt> is raised. If <i>pw_as_hash</i> is <tt><b>False</b></tt> the 
	#        function hashes the password with SHA-256 before the insertion to the database.
	# @exception AssertionError Is raised if eather the <i>nickname</i> or <i>password</i> are not set, if the
	#            <i>nickname</i>'s or the <i>email</i>'s length (if given) does not equal 
	#            <tt>\ref MAX_NICK_LEN</tt> or <tt>\ref MAX_MAIL_LEN</tt> respectively, or if <i>email</i> does 
	#            not contain an <tt>'@'</tt> character.
	# @exception UserException Is raised if a user identified by <i>nickname</i> already exists.
	# @exception WrongPasswordException Is raised if the <i>password</i> is not as long as <tt>\ref PW_HASH_LEN</tt>,
	#            though <i>pw_as_hash</i> is set <tt><b>True</b></tt>.
	def create_user(self, nickname, password, email = None, available_love = DEFAULT_STARTING_LOVE, \
					pw_as_hash = True):
		if(not nickname or not password):
			raise AssertionError("Nickname or Password not set.")
		if len(nickname) > MAX_NICK_LEN:
			raise AssertionError("Nickname to long. Must be at most "+str(MAX_NICK_LEN)+" characters long.")
		if self.__user_exists__(nickname):
			raise UserException("Username "+str(nickname)+" already exists.")
		if not pw_as_hash:
			password = hash_password(nickname,password)
		else:
			if not self.__check_pw_hash_length__(password): 
				raise WrongPasswordException("The password has not the length of a SHA-256 hash, "+\
											"though it should be hashed.")
		
		if email:
			if len(email) > MAX_MAIL_LEN:
				raise AssertionError("Email address to long. Must be at most "+str(MAX_MAIL_LEN)+" characters long.")
			if('@' not in email):
				raise AssertionError("Email address must contain an '@' symbol.")
				
			q = self.db.insert(
					'users', 
					nickname=nickname, 
					password=password, 
					email=email, 
					available_love=available_love
				)
		else:
			q = self.db.insert('users', nickname=nickname, password=password, available_love=available_love)
	
	## Drops a user from the database.
	# @param nickname The nickname of the user.
	# @param session_id The ID of the session the user currently uses in the web application.
	# @exception UserException Is raised if there is no user with the given <i>nickname</i>.
	# @exception IllegalSessionException Is raised if the <i>session_id</i> is not associated to the user 
	#            identified by <i>nickname</i>.
	def drop_user(self, nickname, session_id):
		if not self.__user_exists__(nickname):
			raise UserException('User '+str(nickname)+' does not exist.')
		if not self.__check_session_id__(nickname,session_id):
			raise IllegalSessionException("Session " + str(session_id) + " not associated to user "+str(nickname)+".")
		q = self.db.delete('users', where='nickname = $nickname', vars=locals())
	
	## Defines the login process for a user in the database layer.
	#  i. e. the <tt>session_id</tt> of the web application is associated to this specific user.
	# @param nickname The user's nickname.
	# @param password The user's password.
	# @param session_id The ID of the session currently in use of the web application.
	# @param pw_as_hash (optional) Flag to determine whether the password comes as a hash or in clear text. By default
	#        it is set to <tt><b>True</b></tt> i. e. the function asserts <i>password</i> value as a hash. If
	#        <i>password</i> has in this case not the length defined by <tt>\ref PW_HASH_LEN</tt> a 
	#        <tt>\ref WrongPasswordException</tt> is raised. If <i>pw_as_hash</i> is <tt><b>False</b></tt> the 
	#        function hashes the password with SHA-256 before the insertion to the database.
	# @exception UserException Is raised if there is no user with the given <i>nickname</i>.
	# @exception IllegalSessionException Is raised if the <i>session_id</i> was not generated by the web application.
	# @exception WrongPasswordException Is raised if the <i>password</i> is not as long as <tt>\ref PW_HASH_LEN</tt>,
	#            though <i>pw_as_hash</i> is set <tt><b>True</b></tt> or if the <i>password</i> is just wrong.
	def user_login(self, nickname, password, session_id, pw_as_hash = True):
		if not pw_as_hash:
			password = hash_password(nickname,password)
		else:
			if not self.__check_pw_hash_length__(password): 
				raise WrongPasswordException("The password has not the length of a SHA-256 hash, "+\
											"though it should be hashed.")
		
		if not len(self.db.select('sessions',what='session_id',where='session_id = $session_id',vars=locals())):
			raise IllegalSessionException("Session " + str(session_id) + " is not in database.")
		
		if not self.__check_password__(nickname,password):
			raise WrongPasswordException("The password for user "+nickname+" is wrong.")
		
		self.db.update('users',
				where="nickname = $nickname",
				vars = locals(),
				session_id=session_id
			)
	
	## Defines the logoff process for a user in the database layer.
	#  i. e. the association of the <tt>session_id</tt> to a specific user is removed.
	# @param nickname The user's nickname.
	# @param session_id The ID of the web application session the user is currently assossiated with.
	# @exception UserException Is raised if there is no user with the given <i>nickname</i>.
	# @exception IllegalSessionException Is raised if the <i>session_id</i> is not associated to the user 
	#             identified by <i>nickname</i>.
	def user_logoff(self, nickname, session_id):
		if not self.__user_exists__(nickname):
			raise UserException('User '+nickname+' does not exist.')
		if not self.__check_session_id__(nickname, session_id):
			raise IllegalSessionException("Session " + session_id + " not associated to user "+nickname+".")
		self.db.update('users',
				where="nickname = $nickname",
				vars = locals(),
				session_id=None
			)
	
	## Gets user information is the session is associated to an user.
	# @param session_id The ID of the web application session the user is currently assossiated with.
	# @exception IllegalSessionException Is raised if the <i>session_id</i> is not associated to the user 
	#            identified by <i>nickname</i>.
	# @returns A tuple consisting of the nickname, the email address, the available love count, and the
	#          received love count of the user who is associated to the session identified by the <i>session_id</i>
	def get_session(self, session_id):
		rows = self.db.select(
				['users','sessions'],
				what='nickname,email,available_love,received_love',
				where = "users.session_id = $session_id AND users.session_id = sessions.session_id",
				vars = locals()
			)
		
		if len(rows) == 0:
			raise IllegalSessionException("Session " + str(session_id) + " not associated to a user.")
		row = rows[0]
		return row.nickname, row.email, row.available_love, row.received_love
	
	## Changes the email address of an user.
	# @param nickname The user's nickname.
	# @param session_id The ID of the web application session the user is currently assossiated with.
	# @param email The new email address.
	# @exception UserException If there is no user with the given <i>nickname</i>.
	def change_email_address(self, nickname, session_id, email):
		if not self.__user_exists__(nickname):
			raise UserException('User '+str(nickname)+' does not exist.')
		if not self.__check_session_id__(nickname, session_id):
			raise IllegalSessionException("Session " + str(session_id) + " not associated to user "+str(nickname)+".")
		self.db.update('users',
				where="nickname = $nickname",
				vars = locals(),
				email=email
			)
	
	## Resets the password to a randomly generated 4 character string (using '<tt>pwgen -1</tt>')
	# @param nickname The user's nickname.
	# @exception UserException Is raised if there is no user with the given <i>nickname</i>.
	# @exception EnvironmentError Is raised if the function is not called on a POSIX system so we can use
	#            <tt>pwgen</tt>
	# @returns A tuple consisting of the new generated password and the user's email address where to send it to.
	def reset_password(self, nickname):
		user = self.__select_user__(
					'email', 
					nickname
				)
		if not user.email:
			raise UserException("The users email address is not know. Password reset is only possible with a valid email address.")
		
		import os
		from subprocess import Popen,PIPE
		
		if os.name == 'posix':
			new_password = Popen(['/usr/bin/pwgen','-1'], stdout=PIPE).communicate()[0].strip()
			new_password_hash = hash_password(nickname,new_password)
			self.db.update('users',
					where="nickname = $nickname",
					vars = locals(),
					password=new_password_hash
				)
			return new_password, user.email
		else:
			raise EnvironmentError("This function runs on POSIX systems only, because it makes use of the command \"pwgen\"")
	
	## Changes the password of a user's from <i>old_password</i> to <i>new_password</i>
	# @param nickname The user's nickname.
	# @param old_password The user's old password.
	# @param new_password The user's new password.
	# @param pw_as_hash (optional) Flag to determine whether the passwords come as a hash or in clear text. By default
	#        it is set to <tt><b>True</b></tt> i. e. the function asserts <i>password</i> value as a hash. If
	#        <i>old_password</i> and <i>new_password</i> has in this case not the length defined by 
	#        <tt>\ref PW_HASH_LEN</tt> a <tt>\ref WrongPasswordException</tt> is raised. If <i>pw_as_hash</i> is
	#        <tt><b>False</b></tt> the function hashes the passwords with SHA-256 before the insertion to the 
	#        database.
	# @exception WrongPasswordException Is raised if the <i>old_password</i> or <i>new_password</i> is not as 
	#            long as <tt>\ref PW_HASH_LEN</tt>, though <i>pw_as_hash</i> is set <tt><b>True</b></tt> or if 
	#            <i>old_password</i> is just wrong.
	def change_password(self, nickname, old_password, new_password, pw_as_hash = True):
		if not pw_as_hash:
			old_password = hash_password(nickname,old_password)
			new_password = hash_password(nickname,new_password)
		else:
			if not self.__check_pw_hash_length__(old_password): raise WrongPasswordException("Old Password not hashed, though it should be.")
			if not self.__check_pw_hash_length__(new_password): raise WrongPasswordException("New Password not hashed, though it should be.")
		
		if not self.__check_password__(nickname,old_password):
			raise WrongPasswordException("Wrong password!")
		
		self.db.update(
				'users',
				where="nickname = $nickname",
				vars = locals(),
				password=new_password
			)
	
	## Gives an amount of datalove points to a selection of users
	# @param 
	def spread_free_datalove(self, datalove_points, nicknames = None):
		users = list(self.db.select('users',what='nickname,available_love'))
		
		all_nicknames = [user.nickname for user in users]
		if nicknames == None: nicknames = all_nicknames
		points = dict()
		for i,nickname in enumerate(all_nicknames):
			if nickname in nicknames:
				user = users[i]
				self.db.update(
						'users',
						where="nickname = $nickname",
						vars = locals(),
						available_love = (user.available_love + datalove_points)
					)
	
	def send_datalove(self, from_nickname, to_nickname, session_id, datalove_points = 1):
		if from_nickname == to_nickname:
			raise AssertionError("Don't be so data-narcistic. Share the datalove with other users.")
				
		if(datalove_points < 0):
			raise ValueError("datalove_points must be positive. It is " + datalove_points + " currently.")
		
		if self.__check_session_id__(from_nickname,session_id):
			from_user_available_love = self.__update_love__(from_nickname)
			
			if from_user_available_love > 0:
				actually_spend_love = min(from_user_available_love,datalove_points)
				from_user_available_love -= actually_spend_love
				to_user = self.__select_user__("available_love, received_love",to_nickname)
				
				to_user.available_love += actually_spend_love
				to_user.received_love += actually_spend_love
				
				self.db.update('users',where='nickname = $from_nickname', vars=locals(), 
							available_love=from_user_available_love)
				self.db.update('users',where='nickname = $to_nickname', vars=locals(), 
							available_love=to_user.available_love,
							received_love=to_user.received_love)
			else:
				raise NotEnoughDataloveException(from_nickname+" has not enough datalovepoints to spend.")
		return actually_spend_love
	
	def get_available_love(self,nickname):
		user = self.__select_user__('available_love',nickname)
		return int(user.available_love)
	
	def get_received_love(self,nickname):
		user = self.__select_user__('received_love',nickname)
		return int(user.received_love)
	
	def __update_love__(self,nickname):
		user = self.__select_user__('available_love, last_changed', nickname)
		
		available_love = user.available_love
		current_time = datetime.today()
		
		years = current_time.year - user.last_changed.year
		months = 12*years + (current_time.month - user.last_changed.month)
		
		if (months > 0):
			user.available_love += months * DEFAULT_UPDATE_LOVE
			self.db.update(
					'users',
					where='nickname=$nickname',
					vars=locals(),
					available_love=user.available_love
				)
		
		return user.available_love
	
	def __user_exists__(self,nickname):
		try:
			return 0 != len(self.__select_user__('*',nickname))
		except UserException:
			return False
	
	def __check_session_id__(self,nickname,session_id):
		nickname_in_db,_,_,_ = self.get_session(session_id)
		return nickname_in_db == nickname
	
	def __check_pw_hash_length__(self,password):
		return len(password) == PW_HASH_LEN
	
	def __check_password__(self,nickname,password,pw_as_hash=True):
		if not pw_as_hash:
			password = hash_password(nickname,password)
		
		user = self.__select_user__(
				'password', 
				nickname
			)
		
		if password != user.password:
			return False
		
		return True
	
	def __select_user__(self,columns,nickname):
		rows = self.db.select('users',what=columns,where='nickname = $nickname',vars=locals())
		if len(rows) == 0:
			raise UserException("User '"+nickname+"' does not exist.")
		return rows[0]
	
