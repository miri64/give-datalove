## @mainpage
#  This documents the web application for give.datalove.me. It is written in
#  Python using the web.py framework via wsgi_mod. The git repository for the
#  source code can be found at 
#  <a href="https://github.com/authmillenon/give-datalove">
#  https://github.com/authmillenon/give-datalove
#  </a>. Its wiki gives further information for web designers. This 
#  documentation is for developers specifically.

## @package app
#  @author datalove.me
#  @brief Application script for web.py/wsgi
#  @see <a href="http://webpy.org/docs/0.3/">Web.py Documentation</a>
#
#  No Copyright, no license, comes as it is

import web,os,config,traceback

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
    '/register', 'register',
    '/users','users',
    '/widget', 'widget',
    r'/give_([^?$/\\#%\s]+)_datalove', 'give_user_datalove',
    '/logoff', 'logoff',
    '/unregister', 'unregister',
    '/reset_password', 'reset_password',
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
session = web.session.Session(app, store, initializer={'spend_love': dict()})
# spend_love counts the amount of love spend to a user when not logged in
# if the user is logged in, this love is automatically spend.

## The mod_wsgi application function.
#  @see <a href="https://code.google.com/p/modwsgi/wiki/WhereToGetHelp?tm=6">
#       mod_wsga Documentation</a>
application = app.wsgifunc()    # get web.py application as wsgi application

## Get the session id from a cookie (or in later implementations the URL).
#  @returns The current session's session ID.
def get_session_id():
    #test = web.cookies().get('test_cookie')
    #if test == test_cookie_text:
    session_id = web.cookies().get(web.config.session_parameters['cookie_name'])
    #else:
    #    session_id = web.input().get('sid')
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

## Sends the client a HTTP 500 Internal Server Error with a message and an
#  error stack.
# @param msg (optional) The error message to this error.
# @param error_stack (optional) The error stack of 
# @return The content of the HTTP 500 Internal Server Error message.
def raise_internal_server_error(msg = None, error_stack = None):
    web.header('Content-Type','text/html;charset=utf-8')
    web.ctx.status = '500 Internal Server Error'
    templates = web.template.render(os.path.join(abspath,'templates'))
    return templates.internal_server_error(str(msg),str(error_stack))

## Sends the client a HTTP 404 Not Found with a message.
# @param msg (optional) A message that explains how the searched item was not
#        found.
# @return The content of the HTTP 404 Not Found message.
def raise_not_found(msg):
    web.header('Content-Type','text/html;charset=utf-8')
    web.ctx.status = '404 Not Found'
    templates = web.template.render(os.path.join(abspath,'templates'))
    return templates.not_found(str(msg))

## Class for the <tt>/index</tt> URL.
class index:
    ## Shows the page
    # @param login_error Possible errors (as string) that happened during login.
    # @return String in HTML code of what the side looks like
    def show(self, login_error = None):
        try:
            web.header('Content-Type','text/html;charset=utf-8')
            #web.setcookie(name='test_cookie',value=test_cookie_test, expires=60*60)
            session_id = get_session_id()
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
                return templates.index(
                        content,
                        logged_in = True,
                        login_block = False
                    )
        except BaseException, e:
            return raise_internal_server_error(e,traceback.format_exc())
    
    ## Handles what happens on login
    def login_action(self):
        import hashlib
        i = web.input()
        session_id = get_session_id()
        nickname = i.nickname
        password = dbh.hash_password(nickname,i.password)
        db_handler.user_login(nickname,password,session_id)
        # spend love that was spend, while not logged in
        for to_user,datalovez in session.spend_love.items():
            if not db_handler.get_available_love(nickname):
                break
            if to_user != nickname:
                db_handler.send_datalove(nickname,to_user,session_id,datalovez)
            session.spend_love[to_user] = 0
        
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
            return raise_internal_server_error(e,traceback.format_exc())
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
        try:
            web.header('Content-Type','text/html;charset=utf-8')
            session_id = get_session_id()
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
                return templates.index(
                        content,
                        logged_in = True,
                        login_block = False
                    )
        except BaseException, e:
            return raise_internal_server_error(e,traceback.format_exc())
        raise web.seeother(config.host_url)
    
    ## Handles what happens on password change
    def change_password_action(
                self,
                nickname,
                old_password,
                new_password,
                new_password_conf
            ):
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
                self.change_password_action(
                        nickname,
                        old_password, 
                        new_password,
                        new_password_conf
                    )
        except BaseException, e:
            return raise_internal_server_error(e,traceback.format_exc())
        raise web.seeother(url_path_join(config.host_url,'manage_account'))
        
## Class for the <tt>/register</tt> URL.
class register:
    ## Shows the page.
    # @param nickname The nickname to register.
    # @param email The email address associated to the new account.
    # @param registration_error (optional) Possible errors (as string) that 
    #        happened during registration.
    # @return String in HTML code of what the side looks like
    def show(self, nickname = None, email = None, registration_error = None):
        try:
            web.header('Content-Type','text/html;charset=utf-8')
            templates = web.template.render(os.path.join(abspath,'templates'))
            content = templates.register_form(
                    nickname, 
                    email, 
                    registration_error
                )
            return templates.index(content,login_block = False)
        except BaseException, e:
            return raise_internal_server_error(e,traceback.format_exc())
        raise web.seeother(config.host_url)
        
    ## Method for a HTTP GET request. 
    def GET(self):
        return self.show()
            
    ## Method for a HTTP POST request. 
    def POST(self):
        web.header('Content-Type','text/html;charset=utf-8')
        try:
            import hashlib
            i = web.input()
            nickname = i.nickname
            password = i.password
            email = i.email
            if password != i.conf_password:
                return self.show(
                        nickname,
                        email,
                        "Password and confirmation of password " + 
                        "were not equal."
                    )
            password = dbh.hash_password(nickname,password)
            db_handler.create_user(nickname,password,email)
        except AssertionError, e:
            i = web.input()
            nickname = i.nickname
            email = i.email
            return self.show(nickname,email,e)
        except dbh.UserException, e:
            i = web.input()
            nickname = i.nickname
            email = i.email
            return self.show(nickname,email,e)
        except BaseException, e:
            return raise_internal_server_error(e,traceback.format_exc())
        raise web.seeother(config.host_url)

## Class for the <tt>/users</tt> URL
class users:
    ## Method for a HTTP GET request.
    def GET(self):
        web.header('Content-Type','text/html;charset=utf-8')
        templates = web.template.render(os.path.join(abspath,'templates'))
        try:
            users = db_handler.get_users()
            return templates.users(users)
        except BaseException, e:
            return raise_internal_server_error(e,traceback.format_exc())

## Class for the <tt>/widget</tt> URL.
class widget:
    ## Method for a HTTP GET request. 
    def GET(self):
        web.header('Content-Type','text/html;charset=utf-8')
        templates = web.template.render(os.path.join(abspath,'templates'))
        try:
            i = web.input()
            nickname = ''
            if(hasattr(i,'random')):    
                nickname = random_nickname().GET()
            else:
                nickname = i.user
            error = i.get('error')
            received_love = db_handler.get_received_love(nickname)
            return templates.widget(nickname,received_love,error)
        except dbh.UserException,e:
            i = web.input()
            nickname = i.user
            return templates.widget(nickname,0,e)
        except AttributeError:
            raise web.seeother(config.host_url)
        except BaseException, e:
            return raise_internal_server_error(e,traceback.format_exc())

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
            if not db_handler.session_associated_to_any_user(session_id):
                templates = web.template.render(
                        os.path.join(abspath,'templates')
                    )
                
                if to_user in session.spend_love:
                    session.spend_love[to_user] += 1
                else:
                    session.spend_love[to_user] = 1
                return templates.no_login_widget()
            from_user, _, _, _ = db_handler.get_session(session_id)
        except BaseException, e:
            return raise_internal_server_error(e,traceback.format_exc())
        if logged_in:
            try:
                db_handler.send_datalove(from_user,to_user,session_id)
            except AssertionError,e:
                raise web.seeother(
                        url_path_join(
                                config.host_url,'widget?user=%s&error=%s' 
                                        % (to_user,e)
                            )
                    )
            except dbh.NotEnoughDataloveException, e:
                raise web.seeother(
                        url_path_join(
                                config.host_url,'widget?user=%s&error=%s' 
                                        % (to_user,e)
                            )
                    )
            except BaseException, e:
                return raise_internal_server_error(e,traceback.format_exc())
            raise web.seeother(
                    url_path_join(
                            config.host_url,'widget?user=%s' % to_user
                        )
                )
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
            return raise_internal_server_error(e,traceback.format_exc())
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
            return raise_internal_server_error(e,traceback.format_exc())
        raise web.seeother(config.host_url)

## Class for the <tt>/reset_password_form</tt> URL.
class reset_password:
    ## Shows the page
    # @param nickname Nickname for the account the password must be reset.
    # @param error Possible errors during reset.
    # @return String in HTML code of what the side looks like
    def show(self, nickname = None, error = None, success = False):
        try:
            web.header('Content-Type','text/html;charset=utf-8')
            session_id = get_session_id()
            templates = web.template.render(os.path.join(abspath,'templates'))
            content = templates.reset_password_form(nickname,error,success)
            return templates.index(
                    content,
                    logged_in = False,
                    login_block = True
                )
        except BaseException, e:
            return raise_internal_server_error(e,traceback.format_exc())
        raise web.seeother(config.host_url)
    
    def reset_password_action(self):
        try:
            import smtplib
            from email.mime.text import MIMEText
            i = web.input()
            try:
                new_password, email_to = db_handler.reset_password(i.nickname)
            except UserException, e:
                nickname = web.input().get('nickname')
                return self.show(nickname,e)
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
            
            return self.show(success = True)
        except BaseException, e:
            return raise_internal_server_error(e,traceback.format_exc())
    
    ## Method for a HTTP GET request. 
    def GET(self):
        return self.show()
    
    ## Method for a HTTP POST request. 
    def POST(self):
        return self.reset_password_action()

## Class for the <tt>/api/([^?$/\\#%\s]+)/random_user</tt> where the regular
# expression stands for the username.
#
class random_nickname:
    ## Method for a HTTP GET request.
    #
    def GET(self):
        web.header('Content-Type','text/html;charset=utf-8')
        return db_handler.random_nickname()

## Class for the <tt>/api/([^?$/\\#%\s]+)/</tt> URL where the regular 
#  expression stands for the user's name.
class get_users_love:
    ## Method for a HTTP GET request. 
    # @param nickname The user's nickname
    def GET(self,nickname):
        web.header('Content-Type','text/html;charset=utf-8')
        try:
            if not db_handler.user_exists(nickname):
                return raise_not_found(
                        "User '%s' does not exist." % nickname
                    )
            available_love = db_handler.get_available_love(nickname)
            received_love = db_handler.get_received_love(nickname)
            return str(available_love) + ',' + str(received_love)
        except BaseException, e:
            return raise_internal_server_error(e,traceback.format_exc())

## Class for the <tt>/api/([^?$/\\#%\s]+)/available_datalove</tt> URL where the 
#  regular expression stands for the user's name.
class get_users_available_love:
    ## Method for a HTTP GET request. 
    # @param nickname The user's nickname
    def GET(self,nickname):
        web.header('Content-Type','text/html;charset=utf-8')
        try:
            if not db_handler.user_exists(nickname):
                return raise_not_found(
                        "User '%s' does not exist." % nickname
                    )
            available_love = db_handler.get_available_love(nickname)
            return str(available_love)
        except BaseException, e:
            return raise_internal_server_error(e,traceback.format_exc())

## Class for the <tt>/api/([^?$/\\#%\s]+)/received_datalove</tt> URL where the 
#  regular expression stands for the user's name.
class get_users_received_love:
    ## Method for a HTTP GET request. 
    # @param nickname The user's nickname
    def GET(self,nickname):
        web.header('Content-Type','text/html;charset=utf-8')
        try:
            if not db_handler.user_exists(nickname):
                return raise_not_found(
                        "User '%s' does not exist." % nickname
                    )
            received_love = db_handler.get_received_love(nickname)
            return str(received_love)
        except BaseException, e:
            return raise_internal_server_error(e,traceback.format_exc())

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
                return raise_not_found(
                        "User '%s' does not exist." % nickname
                    )
            session_id = get_session_id()
            from_user, _, _, _ = db_handler.get_session(session_id)
        except BaseException, e:
            return raise_internal_server_error(e,traceback.format_exc())
        if logged_in:
            try:
                db_handler.send_datalove(from_user,nickname,session_id)
            except AssertionError,e:
                return e
            except dbh.NotEnoughDataloveException, e:
                return e
            except BaseException, e:
                return raise_internal_server_error(e,traceback.format_exc())
            return 'SEND'
        else:
            raise web.seeother(config.host_url)
