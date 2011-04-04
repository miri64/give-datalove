## @package db_handling
#  @author datalove.me
#  @brief Manages all database accesses of the web application. For database 
#         access it uses web.py's 
#         <a href="http://webpy.org/docs/0.3/api#web.db"><tt>db</tt> module</a>
#
#  No Copyright, no license, comes as it is

import web
from datetime import datetime
from log import log
from log import get_ctx
import hashlib

## The default value for the amount of datalove a user gets on account creation
DEFAULT_STARTING_LOVE = 5

## The default value for the amount of datalove a user gets on the first day of 
#  a month
DEFAULT_UPDATE_LOVE = 5

## The maximum length of a user's <tt>nickname</tt> as defined in 
#  datalovers_db.sql
MAX_NICK_LEN = 23

## The maximum length of a user's <tt>email</tt> address as defined in 
#  datalovers_db.sql
MAX_MAIL_LEN = 50

## The maximum length of a user's <tt>website</tt> address as defined in 
#  datalovers_db.sql
MAX_WEBSITE_LEN = 50

## The length of the password's hash. With SHA-256 as used in this module, 
#  it is 64 characters.
PW_HASH_LEN = 64

## This Exception is raised in any situation that causes errors with login data,
#  like the user's <tt>nickname</tt> or <tt>password</tt>, the 
#  <tt>session_id</tt>, or the mere existence of an user.
#  @extends Exception
class LoginException(Exception):
    ## The constructor.
    #  @param value the value that represents the error, like an error message 
    #         or error id.
    def __init__(self, value):
        self.value = value
    
    ## The to-string definition.
    #  @returns value the value that represents the error, like an error message
    #           or error id.
    def __str__(self):
        return unicode(self.value)

## This Exception is raised in any situation that causes errors with the 
#  <tt>session_id</tt>.
class IllegalSessionException(LoginException):
    ## The constructor.
    #  @param value the value that represents the error, like an error message 
    #         or error id.
    def __init__(self, value):
        self.value = value
    
    ## The to-string definition.
    #  @returns value the value that represents the error, like an error message
    #           or error id.
    def __str__(self):
        return unicode(self.value)

## This Exception is raised in any situation that involves the existence of 
#  users.
class UserException(LoginException):
    ## The constructor.
    #  @param value the value that represents the error, like an error message 
    #         or error id.
    def __init__(self, value):
        self.value = value
    
    ## The to-string definition.
    #  @returns value the value that represents the error, like an error message
    #           or error id.
    def __str__(self):
        return unicode(self.value)

## This Exception is raised in any situation that involves the existence of 
#  users.
class WrongPasswordException(LoginException):
    ## The constructor.
    #  @param value the value that represents the error, like an error message 
    #         or error id.
    def __init__(self, value):
        self.value = value
    
    ## The to-string definition.
    #  @returns value the value that represents the error, like an error message
    #           or error id.
    def __str__(self):
        return unicode(self.value)

## This Exception is raised when a user does not have enough available datalove 
#  to give.
#  @extends Exception
class NotEnoughDataloveException(Exception):
    ## The constructor.
    #  @param value the value that represents the error, like an error message 
    #         or error id.
    def __init__(self, value):
        self.value = value
    
    ## The to-string definition.
    #  @returns value the value that represents the error, like an error message
    #           or error id.
    def __str__(self):
        return unicode(self.value)

## This function hashes the password of the user, with it's nickname to 
#  calculate the salt of the hash.
# @param nickname Used to calculate the hash salt.
# @param password password to hash.
# @return SHA-256 hash of the password as an hexadecimal number string
def hash_password(nickname,password):
    nickname = nickname.lower()
    if(not nickname or not password):
        raise AssertionError("Nickname or Password not set.")
    salt = sum([ord(char) for char in nickname]) % len(nickname)
    return hashlib.sha256(str(salt) + password).hexdigest()

## This class is the wrapper for all database operations of the web application.
class DBHandler:
    ## The constructor
    # @param db A web.py <tt>web.db.DB</tt> object. You can construct such an 
    #        object e. g. with web.py's 
    # <tt>web.database()</tt> function
    def __init__(self,db):
        log.info('%s Initializing DB handler', get_ctx())
        self.db = db
    
    ## Checks if a string contains any characters in a set of given characters,
    # even their URL escapes.
    # @param str String to be checked.
    # @param set Set on which the string is checked upon.
    # @return True, if str contains any characters in set, False, if not.
    def __containsAny__(self, str, set):
        import urllib
        urlescapes = [urllib.quote_plus(c) for c in set]
        return True in [c in str for c in set] or \
                -1 not in [str.find(esc) for esc in urlescapes]
    
    ## Creates a new user in the database table users.
    # @param nickname The new user's nickname.
    # @param password The new user's password.
    # @param email (optional) The new user's email address. If it is set, it has
    #        to contain an <tt>'@'</tt> character, otherwise an 
    #        <a href="http://docs.python.org/release/2.5.2/lib/module-exceptions.html#l2h-101">
    #        <tt>AssertionError</tt></a> is raised.
    # @param available_love (optional) The available love the user gets on 
    #        account creation. By default it is set on the value of 
    #        <tt>\ref DEFAULT_STARTING_LOVE</tt>.
    # @param pw_as_hash (optional) Flag to determine whether the password comes 
    #        as a hash or in clear text. By default it is set to 
    #        <tt><b>True</b></tt> i. e. the function asserts <i>password</i> 
    #        value as a hash. If <i>password</i> has in this case not the length
    #        defined by <tt>\ref PW_HASH_LEN</tt> a 
    #        <tt>\ref WrongPasswordException</tt> is raised. If 
    #        <i>pw_as_hash</i> is <tt><b>False</b></tt> the function hashes the
    #        password with SHA-256 before the insertion to the database.
    # @exception AssertionError Is raised if eather the <i>nickname</i> or 
    #            <i>password</i> are not set, if the <i>nickname</i>'s or the 
    #            <i>email</i>'s length (if given) does not equal 
    #            <tt>\ref MAX_NICK_LEN</tt> or <tt>\ref MAX_MAIL_LEN</tt> 
    #            respectively, or if <i>email</i> does not contain an 
    #            <tt>'@'</tt> character.
    # @exception UserException Is raised if a user identified by <i>nickname</i>
    #            already exists.
    # @exception WrongPasswordException Is raised if the <i>password</i> is not 
    #            as long as <tt>\ref PW_HASH_LEN</tt>, though <i>pw_as_hash</i> 
    #            is set <tt><b>True</b></tt>.
    def create_user(self, nickname, password, email = None, 
                    available_love = DEFAULT_STARTING_LOVE, 
                    pw_as_hash = True):
        nickname = nickname.lower()
        log.debug(
                '%s Try to create user %s with available_love = %d ' + \
                        'where DEFAULT_STARTING_LOVE = %d',
                get_ctx(),
                repr(nickname),
                available_love,
                DEFAULT_STARTING_LOVE
            )
        if(not nickname or not password):
            raise AssertionError("Nickname or Password not set.")
        if len(nickname) > MAX_NICK_LEN:
            raise AssertionError(
                    "Nickname to long. Must be at most " + 
                    str(MAX_NICK_LEN) + 
                    " characters long.")
        
        if self.__containsAny__(nickname, '?$/\\#% \t\n\r\f\v'):
            raise AssertionError(
                    "Nickname must not contain whitespaces or any of the " +
                    "following characters: ?, $, /, \\, #, %"
                )
        if self.user_exists(nickname):
            raise UserException(
                    "Username " + 
                    str(nickname) + 
                    " already exists."
                )
        if not pw_as_hash:
            password = hash_password(nickname,password)
        else:
            if not self.__check_pw_hash_length__(password): 
                raise WrongPasswordException(
                        "The password has not the length of a SHA-256 hash, " +
                        "though it should be hashed."
                    )
        
        if email:
            if len(email) > MAX_MAIL_LEN:
                raise AssertionError(
                        "Email address to long. Must be at most " + 
                        str(MAX_MAIL_LEN) + 
                        " characters long."
                    )
            if('@' not in email):
                raise AssertionError("Email address must contain an '@' symbol.")
                
        self.db.insert(
                'users', 
                nickname=nickname, 
                password=password, 
                email=email, 
                available_love=available_love
            )
        import re
        log.debug(
                '%s Successfully inserted into db: %s',
                get_ctx(),
                str(dict(
                    self.__select_user__('nickname, available_love',nickname)
                ))
            )
    
    ## Drops a user from the database.
    # @param nickname The nickname of the user.
    # @param session_id The ID of the session the user currently uses in the 
    #        web application.
    # @exception UserException Is raised if there is no user with the given 
    #            <i>nickname</i>.
    # @exception IllegalSessionException Is raised if the <i>session_id</i> is 
    #            not associated to the user identified by <i>nickname</i>.
    def drop_user(self, nickname, session_id):
        nickname = nickname.lower()
        if not self.user_exists(nickname):
            raise UserException('User '+str(nickname)+' does not exist.')
        if not self.__check_session_id__(nickname,session_id):
            raise IllegalSessionException( 
                    "Session " + 
                    str(session_id) + 
                    " not associated to user "+str(nickname)+"."
                )
        self.user_logoff(nickname,session_id)
        q = self.db.delete('users', where='nickname = $nickname', vars=locals())
    
    ## Defines the login process for a user in the database layer.
    #  i. e. the <tt>session_id</tt> of the web application is associated to 
    #  this specific user.
    # @param nickname The user's nickname.
    # @param password The user's password.
    # @param session_id The ID of the session currently in use of the web 
    #        application.
    # @param pw_as_hash (optional) Flag to determine whether the password comes 
    #        as a hash or in clear text. By default it is set to 
    #        <tt><b>True</b></tt> i. e. the function asserts <i>password</i> 
    #        value as a hash. If <i>password</i> has in this case not the length
    #        defined by <tt>\ref PW_HASH_LEN</tt> a 
    #        <tt>\ref WrongPasswordException</tt> is raised. If 
    #        <i>pw_as_hash</i> is <tt><b>False</b></tt> the function hashes the 
    #        password with SHA-256 before the insertion to the database.
    # @exception AssertionError Is raised if the <i>session_id</i> is allready
    #            associated to another user.
    # @exception UserException Is raised if there is no user with the given 
    #            <i>nickname</i>.
    # @exception IllegalSessionException Is raised if the <i>session_id</i> was 
    #            not generated by the web application.
    # @exception WrongPasswordException Is raised if the <i>password</i> is not 
    #            as long as <tt>\ref PW_HASH_LEN</tt>, though <i>pw_as_hash</i> 
    #            is set <tt><b>True</b></tt> or if the <i>password</i> is just 
    #            wrong.
    def user_login(self, nickname, password, session_id, pw_as_hash = True):
        log.debug(
                "%s Try user login for session %s.",
                get_ctx(),
                repr(session_id)
            )
        nickname = nickname.lower()
        if self.session_associated_to_any_user(session_id):
            raise AssertionError(
                    "There is already a user logged in with this session. " +
                    "Only one user per session is allowed."
                )
        if not pw_as_hash:
            password = hash_password(nickname,password)
        else:
            if not self.__check_pw_hash_length__(password): 
                raise WrongPasswordException(
                        "The password has not the length of a SHA-256 hash, " + 
                        "though it should be hashed."
                    )
        
        if not len(self.db.select(
                    'sessions',
                    what='session_id',
                    where='session_id = $session_id',
                    vars=locals()
                )):
            raise IllegalSessionException(
                    "Session " + 
                    str(session_id) + 
                    " is not in database."
                )
        
        if not self.__check_password__(nickname,password):
                # raises UserException if user does not exist.
            raise WrongPasswordException(
                    "The password for user " + 
                    nickname + 
                    " is wrong."
                )
        self.db.insert('user_sessions',
                nickname=nickname,
                session_id=session_id
            )
        log.debug(
                "%s User login successful for session %s.",
                get_ctx(),
                repr(session_id)
            )
    
    ## Defines the logoff process for a user in the database layer.
    #  i. e. the association of the <tt>session_id</tt> to a specific user is 
    #  removed.
    # @param nickname The user's nickname.
    # @param session_id The ID of the web application session the user is 
    #        currently assossiated with.
    # @exception UserException Is raised if there is no user with the given 
    #            <i>nickname</i>.
    # @exception IllegalSessionException Is raised if the <i>session_id</i> 
    #             is not associated to the user identified by <i>nickname</i>.
    def user_logoff(self, nickname, session_id):
        nickname = nickname.lower()
        if not self.user_exists(nickname):
            raise UserException('User ' + nickname + ' does not exist.')
        if not self.__check_session_id__(nickname, session_id):
            raise IllegalSessionException(
                    "Session " + 
                    session_id + 
                    " not associated to user " + 
                    nickname + 
                    "."
                )
        self.db.delete(
                'user_sessions',
                where="nickname = $nickname AND session_id = $session_id",
                vars=locals()
            )
    
    ## Gets user information is the session is associated to an user.
    # @param session_id The ID of the web application session the user is 
    #        currently assossiated with.
    # @exception IllegalSessionException Is raised if the <i>session_id</i> is 
    #            not associated to the user identified by <i>nickname</i>.
    # @returns A dictionary containing the nickname, the email address, the 
    #          available love count, the received love count and the websites
    #          of the user who is associated to the session identified by the 
    #          <i>session_id</i>
    def get_session_user(self, session_id):
        log.debug("%s Try to get user of session_id '%s'", 
                    get_ctx(), session_id)
        user_rows = self.db.query(
                """SELECT nickname, email, available_love, received_love
                   FROM users NATURAL JOIN user_sessions
                   WHERE session_id = $session_id""",
                vars=locals()
            )
        
        website_rows = self.db.query(
                """SELECT website
                   FROM users   NATURAL JOIN user_sessions 
                                NATURAL JOIN user_websites 
                   WHERE session_id = $session_id""",
                vars=locals()
            )
        
        if len(user_rows) == 0:
            raise IllegalSessionException(
                    "Session " + 
                    str(session_id) + 
                    " not associated to a user."
                )
        user = user_rows[0]
        user['available_love'] = self.__update_love__(user.nickname)
        user['websites'] = [row.website for row in website_rows]
        return user
    
    ## Changes the email address of an user.
    # @param nickname The user's nickname.
    # @param session_id The ID of the web application session the user is 
    #        currently assossiated with.
    # @param email The new email address.
    # @exception UserException If there is no user with the given 
    #            <i>nickname</i>.
    # @exception IllegalSessionException If <tt>session_id</tt> is not 
    #            associated to <tt>nickname</tt>.
    # @exception AssertionError If <tt>email</tt> does not contain an '@' 
    #            character.
    def change_email_address(self, nickname, session_id, email):
        nickname = nickname.lower()
        if not self.user_exists(nickname):
            raise UserException('User '+str(nickname)+' does not exist.')
        if not self.__check_session_id__(nickname, session_id):
            raise IllegalSessionException(
                    "Session " + 
                    str(session_id) + 
                    " not associated to user " + 
                    str(nickname) + 
                    "."
                )
        if len(email) == 0:
            self.db.update(
                    'users',
                    where="nickname = $nickname",
                    vars = locals(),
                    email=None
                )
        else:
            if len(email) > MAX_MAIL_LEN:
                raise AssertionError(
                        "Email address to long. Must be at most " + 
                        str(MAX_MAIL_LEN) + 
                        " characters long."
                    )
            if('@' not in email):
                    raise AssertionError(
                            "Email address must contain an '@' character."
                        )
            self.db.update(
                    'users',
                    where="nickname = $nickname",
                    vars = locals(),
                    email=email
                )

    ## Changes the website of an user.
    # @param nickname The user's nickname.
    # @param session_id The ID of the web application session the user is 
    #        currently assossiated with.
    # @param websites An iteralable object of websites.
    # @exception UserException If there is no user with the given 
    #            <i>nickname</i>.
    # @exception IllegalSessionException If <tt>session_id</tt> is not 
    #            associated to <tt>nickname</tt>.
    # @exception AssertionError If <tt>email</tt> does not contain an '@' 
    #            character.
    def change_websites(self, nickname, session_id, websites):
        nickname = nickname.lower()
        if not self.user_exists(nickname):
            raise UserException('User '+str(nickname)+' does not exist.')
        if not self.__check_session_id__(nickname, session_id):
            raise IllegalSessionException(
                    "Session " + 
                    str(session_id) + 
                    " not associated to user " + 
                    str(nickname) + 
                    "."
                )
        
        values = []
        
        for website in set(websites):
            if len(website) > MAX_WEBSITE_LEN:
                raise AssertionError(
                        "Website address is to long. Must be at most " + 
                        str(MAX_WEBSITE_LEN) + 
                        " characters long."
                    )
            if len(website) == 0:
                continue
            if(not website.startswith('http://')):
                    website = 'http://' + website
            values.append(website)
        
        # Eliminate duplicates
        values = [{"nickname": nickname, "website": website} 
                        for website in set(values)]
        
        ta = self.db.transaction()
        try:
            self.db.delete(
                    'user_websites',
                    where="nickname = $nickname",
                    vars = locals()
                )
            self.db.multiple_insert(
                    'user_websites',
                    values
                )
        except:
            ta.rollback()
            raise
        else:
            ta.commit()

    ## Resets the password to a randomly generated 8 character string (using 
    #  the shell command <tt>pwgen -1</tt>)
    # @param nickname The user's nickname.
    # @exception UserException Is raised if there is no user with the given 
    #            <i>nickname</i> or if the user's email address is not known.
    # @exception EnvironmentError Is raised if the function is not called on a 
    #            POSIX system so we can use <tt>pwgen</tt>
    # @returns A tuple consisting of the new generated password and the user's 
    #          email address where to send it to.
    def reset_password(self, nickname):
        nickname = nickname.lower()
        user = self.__select_user__(
                'email', 
                nickname
            )
            # Raises UserException if user does not exist.
        if not user.email:
            raise UserException(
                    "The user's email address is not known. " +
                    "Password reset is only possible with a valid " + 
                    "email address."
                )
        
        import os
        from subprocess import Popen,PIPE
        
        if os.name == 'posix':
            new_password = Popen(
                    ['/usr/bin/pwgen','-1'], 
                    stdout=PIPE
                ).communicate()[0].strip()
            new_password_hash = hash_password(nickname,new_password)
            self.db.update(
                    'users',
                    where="nickname = $nickname",
                    vars = locals(),
                    password=new_password_hash
                )
            return new_password, user.email
        else:
            raise EnvironmentError(
                    "This function runs on POSIX systems " + 
                    "only, because it makes use of the command \"pwgen\""
                )
    
    ## Changes the password of a user's from <i>old_password</i> to 
    #  <i>new_password</i>
    # @param nickname The user's nickname.
    # @param old_password The user's old password.
    # @param new_password The user's new password.
    # @param pw_as_hash (optional) Flag to determine whether the passwords 
    #        come as a hash or in clear text. By default it is set to 
    #        <tt><b>True</b></tt> i. e. the function asserts <i>password</i> 
    #        value as a hash. If <i>old_password</i> and <i>new_password</i> has
    #        in this case not the length defined by <tt>\ref PW_HASH_LEN</tt> a 
    #        <tt>\ref WrongPasswordException</tt> is raised. If 
    #        <i>pw_as_hash</i> is <tt><b>False</b></tt> the function hashes the 
    #        passwords with SHA-256 before the insertion to the database.
    # @exception WrongPasswordException Is raised if the <i>old_password</i> or 
    #            <i>new_password</i> is not as long as 
    #            <tt>\ref PW_HASH_LEN</tt>, though <i>pw_as_hash</i> is set 
    #            <tt><b>True</b></tt> or if <i>old_password</i> is just wrong.
    # @exception UserException Is raised if there is no user with the given 
    #            <i>nickname</i>.
    def change_password(self, nickname, old_password, new_password, 
            pw_as_hash = True):
        nickname = nickname.lower()
        log.debug("%s Try to change password for %s", get_ctx(), nickname)
        if not pw_as_hash:
            old_password = hash_password(nickname,old_password)
            new_password = hash_password(nickname,new_password)
        else:
            if not self.__check_pw_hash_length__(old_password): 
                raise WrongPasswordException(
                        "The old password has not the length of a SHA-256 " + 
                        "hash, though it should be hashed."
                    )
            if not self.__check_pw_hash_length__(new_password): 
                raise WrongPasswordException(
                        "The new password has not the length of a SHA-256 " + 
                        "hash, though it should be hashed."
                    )
        
        if not self.__check_password__(nickname,old_password):
                # Raises UserException if user does not exist.
            raise WrongPasswordException("The old password is wrong!")
        
        self.db.update(
                'users',
                where="nickname = $nickname",
                vars = locals(),
                password=new_password
            )
        log.debug("%s Changed password for %s", get_ctx(), nickname)
    
    ## Gives an amount of datalove points to a selection of users.
    # @param datalove_points The amount of datalove to spread.
    # @param nicknames (optional) An iterable object of nicknames to which users
    #        the amount of datalove should be spend. If it is not set or 
    #        <tt><b>None</b></tt> all users in the database reseve the amount. 
    #        If a user in the list is not in the database he is ignored.
    def spread_free_datalove(self, datalove_points, nicknames = None):
        users = list(self.db.select('users',what='nickname,available_love'))
        
        all_nicknames = [user.nickname for user in users]
        if nicknames == None: nicknames = all_nicknames
        points = dict()
        for i,nickname in enumerate(all_nicknames):
            nickname = nickname.lower()
            if nickname in nicknames:
                user = users[i]
                self.db.update(
                        'users',
                        where="nickname = $nickname",
                        vars = locals(),
                        available_love = (user.available_love + datalove_points)
                    )
    
    ## Sends datalove from a user to another user.
    # @param from_nickname The sending user's nickname.
    # @param to_nickname The receiving user's nickname.
    # @param session_id The ID of the web application session the sending user 
    #        is currently assossiated with.
    # @param datalove_points (optional) The amount of datalove points to send. 
    #        By default it is 1. If the user has not enough pounts to spend, 
    #        all his or hers points are spended the actual number he or her 
    #        spended is returns. If the user has no points at all a 
    #        <tt>\ref NotEnoughDataloveException</tt> is raised.
    # @exception AssertionError Is raised if <i>from_nickname</i> and 
    #        <i>to_nickname</i> are the same.
    # @exception ValueError Is raised if <i>datalove_points</i> is negative.
    # @exception IllegalSessionException Is raised if the <i>session_id</i> 
    #             is not associated to the user identified by 
    #             <i>from_nickname</i>.
    # @exception UserException Is raised if any of the given users not exists.
    # @exception NotEnoughDataloveException Is raised if the user has 0 
    #            available datalove points.
    # @returns The actual amount of datalove points spend.
    def send_datalove(self, from_nickname, to_nickname, session_id, 
            datalove_points = 1):
        log.debug("%s Try to send %d datalovez %s -> %s for session %s", 
                get_ctx(), 
                datalove_points,
                from_nickname,
                to_nickname,
                repr(session_id)
            )
        from_nickname = from_nickname.lower()
        to_nickname = to_nickname.lower()
        if from_nickname == to_nickname:
            raise AssertionError(
                    "Share datalove with other users, not yourself."
                )
        self.__update_love__(to_nickname)
        if(datalove_points < 0):
            raise ValueError(
                    "datalove_points must be positive. It is " + 
                    datalove_points + 
                    " currently."
                )
        
        if not self.user_exists(from_nickname):
            raise UserException("User '"+nickname+"' does not exist.")
        
        if not self.__check_session_id__(from_nickname,session_id):
            raise IllegalSessionException(
                    "Session " + 
                    session_id + 
                    " not associated to user " + 
                    from_nickname + 
                    "."
                )
        
        from_user_available_love = self.__update_love__(from_nickname)
                # Raises UserException if user with from_nickname does not 
                # exist.
        
        if not from_user_available_love:
            raise NotEnoughDataloveException(
                    from_nickname + 
                    " doesn't have enough datalovepoints to spend."
                )
        actually_spend_love = min(
                from_user_available_love, 
                datalove_points
            )
        log.debug("%s Set actually_spend_love = %d (datalove_points = %d)", 
                get_ctx(), 
                actually_spend_love,
                datalove_points
            )
        from_user_available_love -= actually_spend_love
        to_user = self.__select_user__(
                "available_love, received_love",
                to_nickname
            ) 
            # Raises UserException if user with to_nickname does not 
            # exist.
        
        to_user.available_love += actually_spend_love
        to_user.received_love += actually_spend_love
        
        ta = self.db.transaction()
        try:
            q = self.db.update(
                    'users',
                    where='nickname = $from_nickname',
                    vars=locals(), 
                    available_love=from_user_available_love
                )
            log.debug(
                    '%s Successfully token available love of %s: %s', 
                    get_ctx(),
                    from_nickname,
                    str(dict(self.__select_user__(
                            'nickname, available_love',
                            from_nickname
                        )))
                )
            q = self.db.update(
                    'users',
                    where='nickname = $to_nickname',
                    vars=locals(), 
                    available_love=to_user.available_love,
                    received_love=to_user.received_love
                )
            log.debug(
                    '%s Successfully given love to %s: %s', 
                    get_ctx(),
                    to_nickname,
                    str(dict(self.__select_user__(
                            'nickname, available_love, received_love',
                            to_nickname
                        )))
                )
            q = self.db.insert(
                    'history',
                    sender=from_nickname,
                    recipient=to_nickname,
                    amount=actually_spend_love
                )
            log.debug(
                    '%s Successfully updated history: %s', 
                    get_ctx(),
                    to_nickname,
                    str(dict(self.db.query("""
                            SELECT sender, recipient, amount
                            FROM history
                            WHERE timestamp IN
                                    (SELECT MAX(timestamp)
                                    FROM history
                                    WHERE   sender = $from_nickname AND
                                            recipient = $to_nickname AND
                                            amount = $actually_spend_love)
                            """, vars=locals()
                        )[0]))
                )
        except:
            ta.rollback()
            log.debug("%s Sending %d datalovez %s -> %s for session %s failed.", 
                    get_ctx(), 
                    actually_spend_love,
                    from_nickname,
                    to_nickname,
                    repr(session_id)
                )
            raise
        else:
            ta.commit()
            log.debug(
                    "%s Sending %d datalovez %s -> %s " +
                            "for session %s successful.", 
                    get_ctx(), 
                    actually_spend_love,
                    from_nickname,
                    to_nickname,
                    repr(session_id)
                )
        return actually_spend_love
    
    ## Returns the user's amount of available datalove points.
    # @param nickname Some user's nickname.
    # @exception UserException Is raised if there is no user with the given 
    #            <i>nickname</i>.
    # @returns The amount of available datalove of the user.
    def get_available_love(self,nickname):
        nickname = nickname.lower()
        user = self.__select_user__('available_love',nickname)
                # Raises UserException if user does not exist.
        return int(user.available_love)
    
    ## Returns the user's amount of received datalove points.
    # @param nickname Some user's nickname.
    # @exception UserException Is raised if there is no user with the given 
    #            <i>nickname</i>.
    # @returns The amount of received datalove of the user.
    def get_received_love(self,nickname):
        nickname = nickname.lower()
        user = self.__select_user__('received_love',nickname)
                # Raises UserException if user does not exist.
        return int(user.received_love)
    
    ## Returns a random-ordered list of registered nicknames.
    # @returns A random-ordered list of registered nicknames.
    def get_users(self):
        users = self.db.select('users',order='RAND()',what='nickname,received_love')
        return users
    
    ## Checks the existance of a user.
    # @param nickname Some user's nickname.
    # @returns <tt><b>True</b></tt> if the user exists, <tt><b>False</b></tt> if 
    #          he or she does not.
    def user_exists(self,nickname):
        nickname = nickname.lower()
        rows = self.db.select(
                'users',
                where='nickname = $nickname',
                vars=locals()
            )
        return len(rows) != 0
    
    ## Returns a random username.
    # @returns String containing a randomly picked username.
    def random_nickname(self):
        user = self.db.select('users',what="nickname",order="RAND()",limit=1)
        return user[0].nickname
    
    ## Checks the existance of a session.
    # @param session_id Some session's ID.
    # @returns <tt><b>True</b></tt> if the session exists, <tt><b>False</b></tt>
    #          if it does not.
    def session_exists(self,session_id):
        rows = self.db.select(
                'sessions',
                where='session_id = $session_id',
                vars=locals()
            )
        return len(rows) != 0
    
    ## Checks if a session is associated to any user.
    # @param session_id Some session's ID.
    # @returns <tt><b>True</b></tt> if the session is associated to a user, 
    #          <tt><b>False</b></tt> if it does not.
    def session_associated_to_any_user(self,session_id):
        rows = self.db.query(
                """SELECT * 
                   FROM user_sessions NATURAL JOIN sessions
                   WHERE session_id = $session_id""",
                vars=locals()
            )
        return len(rows) != 0
    
    ## Increases the available datalove of an user by every first of month by 
    #  the amont defined by <tt>\ref DEFAULT_UPDATE_LOVE</tt>.
    # @param nickname The user's nickname.
    # @exception UserException Is raised if there is no user with the given 
    #            <i>nickname</i>.
    # @returns The user's new amount of available datalove points.
    def __update_love__(self,nickname):
        nickname = nickname.lower()
        log.debug(
               '%s Try to update love for user %s, where '+
                        'DEFAULT_UPDATE_LOVE = %d',
                get_ctx(),
                repr(nickname),
                DEFAULT_UPDATE_LOVE
            )
        user = self.__select_user__(
                'available_love, last_changed', 
                nickname
            )
            # Raises UserException if user does not exist.
        
        available_love = user.available_love
        current_time = datetime.today()
        
        years = current_time.year - user.last_changed.year
        months = 12*years + (current_time.month - user.last_changed.month)
        
        if (months > 0):
            user.available_love += months * DEFAULT_UPDATE_LOVE
            q = self.db.update(
                    'users',
                    where='nickname=$nickname',
                    vars=locals(),
                    available_love=user.available_love,
                    _test=True
                )
            log.debug(
                    '%s Successfully updated love (last change was %s: %s)',
                    get_ctx(), 
                    str(user.last_changed),
                    str(q))
        else:
            log.debug('%s No need to update.', get_ctx())
        
        return user.available_love
    
    ## Checks if a session is associated to an user
    # @param nickname The user's nickname.
    # @param session_id The ID of the web application session which association 
    #        to the user should be checked.
    # @exception IllegalSessionException Is raised if the <i>session_id</i> is 
    #            not associated to the user identified by <i>nickname</i>.
    # @return <tt><b>True</b></tt> if <i>nickname</i> equals the user's nickname
    #         the session identified by <i>session_id</i> is associated to, 
    #         <tt><b>False</b></tt> if not.
    def __check_session_id__(self, nickname, session_id):
        user = self.get_session_user(session_id)
        return user.nickname == nickname
    
    ## Checks if password has a length equal to <tt>\ref PW_HASH_LEN</tt>
    # @param password The password to be checked.
    # @return <tt><b>True</b></tt> if <i>password</i>'s length equals 
    #         <tt>\ref PW_HASH_LEN</tt>, <tt><b>False</b></tt> if not.
    def __check_pw_hash_length__(self,password):
        return len(password) == PW_HASH_LEN
    
    ## Checks if password of a user is correct.
    # @param nickname The user's nickname.
    # @param password The password to be checked.
    # @param pw_as_hash (optional) Flag to determine whether the password comes 
    #        as a hash or in clear text. By default it is set to 
    #        <tt><b>True</b></tt> i. e. the function asserts <i>password</i> 
    #        value as a hash. If <i>password</i> has in this case not the length
    #        defined by <tt>\ref PW_HASH_LEN</tt> a 
    #        <tt>\ref WrongPasswordException</tt> is raised. If 
    #        <i>pw_as_hash</i> is <tt><b>False</b></tt> the function hashes the 
    #        password with SHA-256 before the insertion to the database.
    # @exception UserException Is raised if there is no user with the given 
    #            <i>nickname</i>.
    # @exception WrongPasswordException Is raised if the <i>password</i> is not 
    #            as long as <tt>\ref PW_HASH_LEN</tt>, though <i>pw_as_hash</i> 
    #            is set <tt><b>True</b></tt>.
    # @return <tt><b>True</b></tt> if the password is correct, 
    #         <tt><b>False</b></tt> if not.
    def __check_password__(self,nickname,password,pw_as_hash=True):
        if not pw_as_hash:
            password = hash_password(nickname,password)
        else:
            if not self.__check_pw_hash_length__(password): 
                raise WrongPasswordException(
                        "The password has not the length of a SHA-256 hash, " + 
                        "though it should be hashed."
                    )
        
        user = self.__select_user__(
                'password', 
                nickname
            )
            # Raises UserException if user does not exist.
        
        if password != user.password:
            return False
        
        return True
    
    ## Selects a cupple of columns from the databases users table for a specific
    #  user
    # @param columns The columns as a comma seperated string that should be
    #        selected.
    # @param nickname The user's nickname.
    # @exception UserException Is raised if there is no user with the given 
    #            <i>nickname</i>.
    # @returns The selected data as web.py's <tt>
    #    <a href="http://webpy.org/docs/0.3/api#web.utils">ThreadedDict</a></tt> 
    #    object.
    def __select_user__(self,columns,nickname):
        nickname = nickname.lower()
        rows = self.db.select(
                'users',
                what=columns,
                where='nickname = $nickname',
                vars=locals()
            )
        if len(rows) == 0:
            raise UserException("User '"+nickname+"' does not exist.")
        return rows[0]
    
    ## Gets the last 30 recieved and sent love of the current user
    # @param nickname The nickname the user is currently assossiated with.
    # @returns A tuple consisting of tuples with each the sent and received
    #    love.
    def get_history(self, nickname):
        sent = self.db.select(
                'history',
                what='recipient, amount, timestamp',
                where='sender = $nickname',
                order='timestamp DESC',
                limit=30,
                vars=locals()
            )
        received = self.db.select(
                'history',
                what='sender, amount, timestamp',
                where='recipient = $nickname',
                order='timestamp DESC',
                limit=30,
                vars=locals()
            )
        return received, sent
    
    ## Returns the overall number of users currently registered.
    # @returns The overall number of users currently registered.
    def get_total_loverz(self):
        log.debug("%s Try to get total loverz from DB.",get_ctx())
        amount = self.db.select('users', what='COUNT(nickname) AS amount')[0] \
                        .amount
        log.debug("%s Got %d loverz from DB.",get_ctx(),amount)
        return amount
    
    ## Gets profile information of a user.
    # @param nickname The user's nickname.
    # @exception UserException Is raised if there is no user with the given 
    #            <i>nickname</i>.
    # @returns A dictionary containing the user's available and received love 
    #          and his or hers websites.
    def get_profile(self, nickname):
        users = self.db.select(
                'users',
                what='available_love, received_love',
                where='nickname = $nickname',
                vars=locals()
            )
        
        if len(users) == 0:
            raise UserException("User '"+nickname+"' does not exist.")
            
        websites = [row.website for row in self.db.select(
                'user_websites',
                what='website',
                where='nickname = $nickname',
                vars=locals()
            )]
        
        user = users[0]
        
        user['websites'] = websites
        
        return user
