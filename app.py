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
from log import log
from log import get_ctx
import db_handling as dbh

web.config.debug = False
web.config.session_parameters['cookie_name'] = 'give_datalove_session_id'
web.config.session_parameters['timeout'] = 2 * 7 * 24 * 60 * 60
        # 2 weeks in seconds
web.config.session_parameters['ignore_expiry'] = False

## URL-Map that maps the urls to the respective classes 
# @see <a href="http://webpy.org/docs/0.3/">Web.py Documentation</a>
urls = (
    '/', 'index',
    '/manage_account', 'manage_account',
    '/register', 'register',
    '/history', 'history',
    r'/user/([^?$/\\#%\s]+)','user',
    r'/user_give_([^?$/\\#%\s]+)_datalove', 'user_give_user_datalove',
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

ses_templates = web.template.render(os.path.join(abspath,'templates'))
content = ses_templates.session_expired(get_session_id())
web.config.session_parameters['expired_message'] = \
        str(ses_templates.index(content))
ses_templates = None

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

## Session management that works with session IDs in URL to
class CookieIndependentSession(web.session.Session):
    def __init__(self, app, store, initializer=None):
        self.__dict__['store'] = store
        self.__dict__['_initializer'] = initializer
        self.__dict__['_last_cleanup_time'] = 0
        self.__dict__['_config'] = \
                web.utils.storage(web.config.session_parameters)

        if app:
            app.add_processor(self._processor)
        
    def _load(self):
        """Load the session from the store, by the id from cookie"""
        cookie_name = self._config.cookie_name
        cookie_domain = self._config.cookie_domain
        self.session_id = web.cookies().get(cookie_name) or \
                            web.input().get('sid')
                
        # protection against session_id tampering
        if self.session_id and not self._valid_session_id(self.session_id):
            self.session_id = None

        self._check_expiry()
        if self.session_id:
            d = self.store[self.session_id]
            self.update(d)
            self._validate_ip()
        
        if not self.session_id:
            self.session_id = self._generate_session_id()

            if self._initializer:
                if isinstance(self._initializer, dict):
                    self.update(self._initializer)
                elif hasattr(self._initializer, '__call__'):
                    self._initializer()
 
        self.ip = web.ctx.ip

## The applications session object.
session = CookieIndependentSession(
        app, 
        store, 
        initializer={'spend_love': dict()}
    )
# spend_love counts the amount of love spend to a user when not logged in
# if the user is logged in, this love is automatically spend.
session_cookie = True

## Get the session id from a cookie (or in later implementations the URL).
#  @returns The current session's session ID.
def get_session_id():
    log.debug("%s Try to get session_id", get_ctx())
    global session_cookie
    session_id = web.cookies().get(web.config.session_parameters['cookie_name'])
    if not session_id:
        session_cookie = False
        session_id = web.input().get('sid')
        log.info(
                "%s Get session_id = '%s' from %s query",
                get_ctx(),
                session_id,
                web.ctx.method
            )
    else:
        session_cookie = True
        log.info(
                "%s Get session_id = '%s' from cookie",
                get_ctx(),
                session_id
            )
    if not session_id:
        session_id = session.session_id
        log.info(
                "%s Get session_id = '%s' from local session",
                get_ctx(),
                session_id
            )
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

## HTTP 500 Internal Server Error with a message and an error stack.
# @param msg (optional) The error message to this error.
# @param error_stack (optional) The error stack of 
# @return The content of the HTTP 500 Internal Server Error message.
def internalerror(msg = None):
    error_stack = str(traceback.format_exc())
    log.critical(
            "%s Internal Server Error on '%s' Cause:\n %s",
            get_ctx(),
            web.ctx.path,
            error_stack
        )
    web.header('Content-Type','text/html;charset=utf-8')
    web.ctx.status = '500 Internal Server Error'
    templates = web.template.render(os.path.join(abspath,'templates'))
    return web.internalerror(
            templates.internal_server_error(msg,error_stack)
        )

## HTTP 404 Not Found with a message.
# @param msg (optional) A message that explains how the searched item was not
#        found.
# @return The content of the HTTP 404 Not Found message.
def notfound(msg = None):
    if not msg:
        msg = "Oops... maybe you shold check what you've typed in."
    log.warning(
            "%s '%s' not found (%s)",
            get_ctx(),
            web.ctx.path,
            str(msg)
        )
    web.header('Content-Type','text/html;charset=utf-8')
    web.ctx.status = '404 Not Found'
    templates = web.template.render(os.path.join(abspath,'templates'))
    return web.notfound(templates.not_found(msg))

app.internalerror = internalerror
app.notfound = notfound

## Class for the <tt>/index</tt> URL.
class index:
    ## Shows the page
    # @param login_error Possible errors (as string) that happened during login.
    # @return String in HTML code of what the side looks like
    def show(self, login_error = None):
        log.debug(
                "%s Show index with with login_error = %s",
                get_ctx(),
                repr(login_error)
            )
        try:
            web.header('Content-Type','text/html;charset=utf-8')
            session_id = get_session_id()
            templates = web.template.render(os.path.join(abspath,'templates'))
            total_loverz = db_handler.get_total_loverz()
            log.debug(
                    "%s Got total_loverz = %d",
                    get_ctx(),
                    total_loverz
                )
            if not session_id or \
                    not db_handler.session_associated_to_any_user(session_id):
                log.debug("%s not logged in.",get_ctx())
                content = templates.welcome()
                if session_cookie:
                    return templates.index(
                            content, 
                            total_loverz = total_loverz,
                            login_error = login_error
                        )
                else:
                    return templates.index(
                            content,
                            total_loverz = total_loverz,
                            session_id = session_id,
                            login_error = login_error,
                        )
            else:
                user = db_handler.get_session_user(session_id)
                log.debug("%s Got user for session %s", get_ctx(), session_id)
                content = templates.userpage(user)
                if session_cookie:
                    return templates.index(
                            content,
                            total_loverz = total_loverz,
                            logged_in = True,
                            login_block = False
                        )
                else:
                    return templates.index(
                            content,
                            total_loverz = total_loverz,
                            session_id = session_id,
                            logged_in = True,
                            login_block = False
                        )
        except BaseException, e:
            raise internalerror(e)
    
    ## Handles what happens on login
    def login_action(self):
        log.info("%s User login.",get_ctx())
        import hashlib
        i = web.input()
        session_id = get_session_id()
        nickname = i.nickname
        password = dbh.hash_password(nickname,i.password)
        db_handler.user_login(nickname,password,session_id)
        log.debug("%s User login successful.",get_ctx())
        # spend love that was spend, while not logged in
        while len(session.spend_love):
            to_user, nickname = session.spend_love.popitem()
            if not db_handler.get_available_love(nickname):
                break
            if to_user != nickname:
                log.debug(
                        "%s Give love which was given by now: %s -> %d",
                        get_ctx(),
                        to_user,
                        datalovez
                    )
                db_handler.send_datalove(nickname,to_user,session_id,datalovez)
        
    ## Method for a HTTP GET request. 
    def GET(self):
        log.info(
                "%s \"%s %s %s\"", 
                get_ctx(),
                web.ctx.method, 
                web.ctx.path, 
                web.ctx.env['SERVER_PROTOCOL'])
        return self.show()
    
    ## Method for a HTTP POST request. 
    def POST(self):
        log.info(
                "%s \"%s %s %s\"", 
                get_ctx(),
                web.ctx.method, 
                web.ctx.path, 
                web.ctx.env['SERVER_PROTOCOL'])
        try:
            self.login_action()
        except AssertionError, e:
            return self.show(e)
        except dbh.IllegalSessionException,e:
            return self.show(e)
        except dbh.LoginException:
            return self.show(
                    'Password not associated to nickname.'
                )
        except BaseException, e:
            raise internalerror(e)
        if session_cookie:
            raise web.seeother(config.host_url)
        else:
            session_id = get_session_id()
            raise web.seeother(config.host_url+"?sid="+str(session_id))

## Class for the <tt>/manage_account</tt> URL, i. e. forms for changing email
#  address and password.
class manage_account:
    ## Shows the page
    # @param email_change_error Possible errors (as string) that happened 
    #        during the change of the email address.
    # @param pw_change_error Possible errors (as string) that happened 
    #        during the change of the password.
    # @return String in HTML code of what the side looks like
    def show(self, email_change_error = None, pw_change_error = None, website_change_error = None):
        try:
            web.header('Content-Type','text/html;charset=utf-8')
            session_id = get_session_id()
            templates = web.template.render(os.path.join(abspath,'templates'))
            if session_id and \
                    db_handler.session_associated_to_any_user(session_id):
                user = db_handler.get_session_user(session_id)
                websites = ''
                for website in user.websites:
                    websites += website + '\n'
                user.websites = websites
                total_loverz = db_handler.get_total_loverz()
                if session_cookie:
                    content = templates.manage_account(
                            user,
                            email_change_error = email_change_error,
                            pw_change_error = pw_change_error,
                            website_change_error = None
                        )
                    return templates.index(
                            content,
                            total_loverz = total_loverz,
                            logged_in = True,
                            login_block = False
                        )
                else:
                    content = templates.manage_account(
                            user,
                            session_id = session_id,
                            email_change_error = email_change_error,
                            pw_change_error = pw_change_error,
                            website_change_error = website_change_error
                        )
                    return templates.index(
                            content,
                            total_loverz = total_loverz,
                            session_id = session_id,
                            logged_in = True,
                            login_block = False
                        )
        except BaseException, e:
            raise internalerror(e)
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
            user = db_handler.get_session_user(session_id)
            i = web.input()
            if i.get('change_mail'):
                email = i.get('email')
                try:
                    db_handler.change_email_address(
                            user.nickname,
                            session_id,
                            email
                        )
                except dbh.LoginException, e:
                    return self.show(email_change_error = e)
                except AssertionError, e:
                    return self.show(email_change_error = e)
            elif i.get('change_pw'):
                old_password = i.get('old_password')
                new_password = i.get('new_password')
                new_password_conf = i.get('new_password_conf')
                self.change_password_action(
                        user.nickname,
                        old_password, 
                        new_password,
                        new_password_conf
                    )
            elif i.get('profile'):
                websites = i.get('websites')
                websites = websites.split('\n')
                try:
                    db_handler.change_websites(
                            user.nickname,
                            session_id,
                            websites
                        )
                except dbh.LoginException, e:
                    return self.show(website_change_error = e)
                except AssertionError, e:
                    return self.show(website_change_error = e)
                    
        except BaseException, e:
            raise internalerror(e)
        if session_cookie:
            raise web.seeother(url_path_join(config.host_url,'manage_account'))
        else:
            session_id = get_session_id()
            raise web.seeother(
                    url_path_join(config.host_url,'manage_account') +
                    '?sid=' + session_id
                )
        
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
            content = ''
            total_loverz = db_handler.get_total_loverz()
            if session_cookie:
                content = templates.register_form(
                        nickname, 
                        email, 
                        registration_error = registration_error
                    )
                return templates.index(
                        content, 
                        total_loverz = total_loverz, 
                        login_block = False
                    )
            else:
                session_id = get_session_id()
                content = templates.register_form(
                        nickname, 
                        email, 
                        session_id = session_id,
                        registration_error = registration_error
                    )
                return templates.index(
                        content, 
                        total_loverz = total_loverz, 
                        session_id = session_id,
                        login_block = False
                    )
        except BaseException, e:
            raise internalerror(e)
        print 'show', session_cookie
        if session_cookie:
            raise web.seeother(config.host_url)
        else:
            session_id = get_session_id()
            raise web.seeother(config.host_url+'?sid='+session_id)
        
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
            raise internalerror(e)
        print 'POST', session_cookie
        if session_cookie:
            raise web.seeother(config.host_url)
        else:
            session_id = get_session_id()
            raise web.seeother(config.host_url+'?sid='+session_id)

## Class for the <tt>/users</tt> URL
class users:
    ## Method for a HTTP GET request.
    def GET(self):
        web.header('Content-Type','text/html;charset=utf-8')
        try:
            session_id = get_session_id()
            users = db_handler.get_users()
            templates = web.template.render(os.path.join(abspath,'templates'))
            total_loverz = db_handler.get_total_loverz()
            
            logged_in = db_handler.session_associated_to_any_user(session_id)
            
            if session_cookie:
                content = templates.users(users)
                return templates.index(
                        content,
                        total_loverz = total_loverz,
                        login_block = not logged_in, 
                        logged_in = logged_in
                    )
            else:
                content = templates.users(users,session_id)
                return templates.index(
                        content,
                        total_loverz = total_loverz,
                        session_id = session_id,
                        login_block = not logged_in, 
                        logged_in = logged_in
                    )
        except BaseException, e:
            raise internalerror(e)

## Class for the <tt>/widget</tt> URL.
class widget:
    ## Shows the page
    # @param login_error Possible errors (as string) that happened during login.
    # @return String in HTML code of what the side looks like
    def show(self, login_error = None):
        try:
            web.header('Content-Type','text/html;charset=utf-8')
            #web.setcookie(name='test_cookie',value=test_cookie_test, expires=60*60)
            session_id = get_session_id()
            templates = web.template.render(os.path.join(abspath,'templates'))
            total_loverz = db_handler.get_total_loverz()
            if not session_id or \
                    not db_handler.session_associated_to_any_user(session_id):
                content = templates.widgetpage()
                if session_cookie:
                    return templates.index(content, total_loverz = total_loverz,login_error = login_error)
                else:
                    return templates.index(
                            content,
                            total_loverz = total_loverz,
                            session_id = session_id,
                            login_error = login_error,
                        )
            else:
                user = db_handler.get_session_user(
                        session_id
                    )
                content = templates.widgetpage(user.nickname)
                if session_cookie:
                    return templates.index(
                            content,
                            total_loverz = total_loverz,
                            logged_in = True,
                            login_block = False
                        )
                else:
                    return templates.index(
                            content,
                            total_loverz = total_loverz,
                            session_id = session_id,
                            logged_in = True,
                            login_block = False
                        )
        except BaseException, e:
            raise internalerror(e)
    ## Method for a HTTP GET request. 
    def GET(self):
        web.header('Content-Type','text/html;charset=utf-8')
        templates = web.template.render(os.path.join(abspath,'templates'))
        session_id = get_session_id()
        try:
            i = web.input()
            nickname = ''
            if(hasattr(i,'random')):    
                nickname = random_nickname().GET()
            else:
                try:
                    nickname = i.user
                except:
                    return self.show()
            error = i.get('error')
            received_love = db_handler.get_received_love(nickname)
            return templates.widget(nickname,session_id,received_love,error)
        except dbh.LoginException,e:
            i = web.input()
            nickname = i.user
            return templates.widget(nickname,session_id,0,e)
        except AttributeError:
            i = web.input()
            return templates.widget(
                    '',
                    0,
                    "No user given."
                )
        except BaseException, e:
            raise internalerror(e)

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
            print session_id
            if not db_handler.session_associated_to_any_user(session_id):
                templates = web.template.render(
                        os.path.join(abspath,'templates')
                    )
                
                if to_user in session.spend_love:
                    session.spend_love[to_user] += 1
                else:
                    session.spend_love[to_user] = 1
                return templates.no_login_widget(session_id)
            from_user = db_handler.get_session_user(session_id)
        except BaseException, e:
            raise internalerror(e)
        if logged_in:
            try:
                db_handler.send_datalove(from_user.nickname,to_user,session_id)
            except AssertionError,e:
                if session_cookie:
                    raise web.seeother(
                            url_path_join(
                                    config.host_url,
                                    'widget?user=%s&error=%s' % (to_user,e)
                                )
                        )
                else:
                    raise web.seeother(
                            url_path_join(
                                    config.host_url,
                                    'widget?user=%s&error=%s&sid=%s' 
                                            % (to_user,e,session_id)
                                )
                        )
            except dbh.NotEnoughDataloveException, e:
                if session_cookie:
                    raise web.seeother(
                            url_path_join(
                                    config.host_url,
                                    'widget?user=%s&error=%s' % (to_user,e)
                                )
                        )
                else:
                    raise web.seeother(
                            url_path_join(
                                    config.host_url,
                                    'widget?user=%s&error=%s&sid=%s' 
                                            % (to_user,e,session_id)
                                )
                        )
            except BaseException, e:
                raise internalerror(e)
            if session_cookie:
                raise web.seeother(
                        url_path_join(
                                config.host_url,'widget?user=%s' % to_user
                            )
                    )
            else:
                raise web.seeother(
                        url_path_join(
                                config.host_url,'widget?user=%s&sid=%s' 
                                        % (to_user,session_id)
                            )
                    )
            
## Class for the <tt>/logoff</tt> URL.
class logoff:
    ## Method for a HTTP GET request. 
    def GET(self):
        web.header('Content-Type','text/html;charset=utf-8')
        try:
            session_id = get_session_id()
            user = db_handler.get_session_user(session_id)
            db_handler.user_logoff(user.nickname,session_id)
            session.kill()
        except BaseException, e:
            raise internalerror(e)
        raise web.seeother(config.host_url)

## Class for the <tt>/unregister</tt> URL.
class unregister:
    ## Method for a HTTP GET request. 
    def GET(self):
        try:
            web.header('Content-Type','text/html;charset=utf-8')
            
            session_id = get_session_id()
            user = db_handler.get_session_user(session_id)
            db_handler.drop_user(user.nickname,session_id)
        except BaseException, e:
            raise internalerror(e)
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
            total_loverz = db_handler.get_total_loverz()
            if session_cookie:
                content = templates.reset_password_form(
                        nickname,
                        error = error,
                        success = success
                    )
                return templates.index(
                        content,
                        total_loverz = total_loverz,
                        logged_in = False,
                        login_block = False
                    )
            else:
                content = templates.reset_password_form(
                        nickname,
                        session_id = session_id,
                        error = error,
                        success = success
                    )
                return templates.index(
                        content,
                        total_loverz = total_loverz,
                        session_id = session_id,
                        logged_in = False,
                        login_block = False
                    )
        except BaseException, e:
            raise internalerror(e)
        raise web.seeother(config.host_url)
    
    def reset_password_action(self):
        try:
            import smtplib
            from email.mime.text import MIMEText
            i = web.input()
            try:
                new_password, email_to = db_handler.reset_password(i.nickname)
            except dbh.UserException, e:
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
            raise internalerror(e)
    
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
                raise notfound(
                        "User '%s' does not exist." % nickname
                    )
            available_love = db_handler.get_available_love(nickname)
            received_love = db_handler.get_received_love(nickname)
            return str(available_love) + ',' + str(received_love)
        except BaseException, e:
            raise internalerror(e)

## Class for the <tt>/api/([^?$/\\#%\s]+)/available_datalove</tt> URL where the 
#  regular expression stands for the user's name.
class get_users_available_love:
    ## Method for a HTTP GET request. 
    # @param nickname The user's nickname
    def GET(self,nickname):
        web.header('Content-Type','text/html;charset=utf-8')
        try:
            if not db_handler.user_exists(nickname):
                raise notfound(
                        "User '%s' does not exist." % nickname
                    )
            available_love = db_handler.get_available_love(nickname)
            return str(available_love)
        except BaseException, e:
            raise internalerror(e)

## Class for the <tt>/api/([^?$/\\#%\s]+)/received_datalove</tt> URL where the 
#  regular expression stands for the user's name.
class get_users_received_love:
    ## Method for a HTTP GET request. 
    # @param nickname The user's nickname
    def GET(self,nickname):
        web.header('Content-Type','text/html;charset=utf-8')
        try:
            if not db_handler.user_exists(nickname):
                raise notfound(
                        "User '%s' does not exist." % nickname
                    )
            received_love = db_handler.get_received_love(nickname)
            return str(received_love)
        except BaseException, e:
            raise internalerror(e)

## Class for the <tt>/api/([^?$/\\#%\s]+)/give_datalove</tt> URL where the 
#  regular expression stands for the user's name.
class give_user_datalove_api:
    ## Method for a HTTP GET request. 
    # @param to_user User the datalove should be given to.
    def GET(self,to_user):
        web.header('Content-Type','text/html;charset=utf-8')
        try:
            logged_in = True
            if not db_handler.user_exists(to_user):
                raise notfound(
                        "User '%s' does not exist." % to_user
                    )
            session_id = get_session_id()
            from_user = db_handler.get_session_user(session_id)
        except dbh.IllegalSessionException:
            web.ctx.status = '401 Unauthorized'
            return 'You are not logged in yet.'
        except BaseException, e:
            raise internalerror(e)
        if logged_in:
            try:
                db_handler.send_datalove(from_user.nickname,to_user,session_id)
            except AssertionError,e:
                web.ctx.status = '412 Precondition Failed'
                return e
            except dbh.NotEnoughDataloveException, e:
                web.ctx.status = '412 Precondition Failed'
                return e
            except BaseException, e:
                raise internalerror(e)
            return ''
        else:
            raise web.seeother(config.host_url)

## Class for the <tt>/history/tt> URL.
class history:
    def alter_timestamp(self, timestamp):
        timestamp = timestamp.strftime("%a %d %b,  %H:%M")
        return timestamp
    ## Shows the page
    # @return String in HTML code of what the site looks like
    def show(self, login_error = None):
        try:
            web.header('Content-Type','text/html;charset=utf-8')
            #web.setcookie(name='test_cookie',value=test_cookie_test, expires=60*60)
            session_id = get_session_id()
            templates = web.template.render(
                                os.path.join(abspath,'templates'), 
                                globals={'alter_time':self.alter_timestamp}
                            )
            total_loverz = db_handler.get_total_loverz()
            if not session_id and \
                    not db_handler.session_associated_to_any_user(session_id):
                content = templates.welcome()
                if session_cookie:
                    return templates.index(content, total_loverz = total_loverz)
                else:
                    return templates.index(
                            content, 
                            session_id = session_id,
                            total_loverz = total_loverz
                        )
            else:
                user = db_handler.get_session_user(
                        session_id
                    )
                received, sent = db_handler.get_history(
                        user.nickname
                )
                if session_cookie:
                    content = templates.historypage(received, sent)
                    return templates.index(
                            content,
                            total_loverz = total_loverz,
                            logged_in = True,
                            login_block = False
                        )
                else:
                    content = templates.historypage(received, sent, session_id)
                    return templates.index(
                            content,
                            total_loverz = total_loverz,
                            session_id = session_id,
                            logged_in = True,
                            login_block = False
                        )
        except BaseException, e:
            raise internalerror(e)

    ## Method for a HTTP GET request. 
    def GET(self):
        return self.show()

## Class for the <tt>/user/([^?$/\\#%\s]+)/</tt> URL where the regular 
#  expression stands for the user's name.
class user:
    def show(self, nickname, login_error = None):
        try:
            web.header('Content-Type','text/html;charset=utf-8')
            if not db_handler.user_exists(nickname):
                raise notfound(
                        "User '%s' does not exist." % nickname
                    )
            #web.setcookie(name='test_cookie',value=test_cookie_test, expires=60*60)
            session_id = get_session_id()
            templates = web.template.render(os.path.join(abspath,'templates'))
            total_loverz = db_handler.get_total_loverz()
            user = db_handler.get_profile(nickname)
            i = web.input()
            error = i.get('error')
            if not session_id or \
                    not db_handler.session_associated_to_any_user(session_id):
                logged_in = False
                login_block = True
            else:
                logged_in = True
                login_block = False
            
            if session_cookie:
                content = templates.profilepage(
                        nickname,
                        user,
                        error,
                        logged_in = logged_in,
                        login_block = login_block,
                    )
                return templates.index(
                        content,
                        total_loverz = total_loverz,
                        logged_in = logged_in,
                        login_block = login_block
                    )
            else:
                content = templates.profilepage(
                        nickname,
                        user,
                        error,
                        logged_in = logged_in,
                        login_block = login_block,
                        session_id = session_id
                    )
                return templates.index(
                        content,
                        total_loverz = total_loverz,
                        session_id = session_id,
                        logged_in = logged_in,
                        login_block = login_block
                    )
        except BaseException, e:
            raise internalerror(e)
    ## Method for a HTTP GET request. 
    # @param nickname The user's nickname
    def GET(self,nickname):
        return self.show(nickname)

## Class for the <tt>/give_([^?$/\\#%\s]+)_datalove</tt> URL where the regular 
#  expression stands for the user's name.
class user_give_user_datalove:
    ## Method for a HTTP GET request. 
    # @param to_user User the datalove should be given to.
    def GET(self,to_user):
        web.header('Content-Type','text/html;charset=utf-8')
        try:
            logged_in = True
            if not db_handler.user_exists(to_user):
                return "User does not exist."
            session_id = get_session_id()
            print session_id
            if not db_handler.session_associated_to_any_user(session_id):
                templates = web.template.render(
                        os.path.join(abspath,'templates')
                    )
                
                if to_user in session.spend_love:
                    session.spend_love[to_user] += 1
                else:
                    session.spend_love[to_user] = 1
                return templates.no_login_widget(session_id)
            from_user = db_handler.get_session_user(session_id)
        except BaseException, e:
            raise internalerror(e)
        if logged_in:
            try:
                db_handler.send_datalove(from_user.nickname,to_user,session_id)
            except AssertionError,e:
                if session_cookie:
                    raise web.seeother(
                            url_path_join(
                                    config.host_url,
                                    '/user/%s?error=%s' % (to_user,e)
                                )
                        )
                else:
                    raise web.seeother(
                            url_path_join(
                                    config.host_url,
                                    '/user/%s?error=%s&sid=%s' 
                                            % (to_user,e,session_id)
                                )
                        )
            except dbh.NotEnoughDataloveException, e:
                if session_cookie:
                    raise web.seeother(
                            url_path_join(
                                    config.host_url,
                                    '/user/%s?error=%s' % (to_user,e)
                                )
                        )
                else:
                    raise web.seeother(
                            url_path_join(
                                    config.host_url,
                                    '/user/%s?error=%s&sid=%s' 
                                            % (to_user,e,session_id)
                                )
                        )
            except BaseException, e:
                raise internalerror(e)
            if session_cookie:
                raise web.seeother(
                        url_path_join(
                                config.host_url,'/user/%s' % to_user
                            )
                    )
            else:
                raise web.seeother(
                        url_path_join(
                                config.host_url,'/user/%s?sid=%s' 
                                        % (to_user,session_id)
                            )
                    )
            

if __name__ == '__main__': app.run()
