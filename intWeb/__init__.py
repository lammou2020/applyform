import json
import logging
from functools import wraps
from flask import current_app, Flask, redirect, request, session, url_for, render_template
import click
from flask.cli import with_appcontext
from flask import g

import httplib2
# [START include]
# from oauth2client.contrib.flask_util import UserOAuth2

import redis
pool=redis.ConnectionPool(host='127.0.0.1',port=6379)

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
init_db_flag=False
from flask_session import Session
# from .mySession import MySessionInterface
# oauth2 = UserOAuth2()
# [END include]

def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data

def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)#,  static_url_path="")
    app.config.from_object(config)
    app.debug = debug
    app.testing = testing
    if config_overrides:
        app.config.update(config_overrides)

    # Configure logging
    if not app.testing:
        logging.basicConfig(level=logging.INFO)

    # app.config.from_mapping(
        # default secret that should be overridden in environ or config
        # SQLALCHEMY_TRACK_MODIFICATIONS=False,
    # )

    # Setup the data model.
    with app.app_context():
        model = get_model()
        model.init_app(app)
        model_applyform= get_applyform_model()
        model_applyform.init_app(app)
        if init_db_flag:
            from intWeb.initDB_ import initdb_data
            db.init_app(app)
            initdb_data(db,app)
        
    app.config['SESSION_COOKIE_NAME'] ="connect.sid"
    app.config['SESSION_TYPE'] = 'redis'  # session类型为redis
    app.config['SESSION_PERMANENT'] = False  # 如果设置为True，则关闭浏览器session就失效。
    app.config['SESSION_USE_SIGNER'] = False  # 是否对发送到浏览器上session的cookie值进行加密
    app.config['SESSION_KEY_PREFIX'] = 'sess:'  # 保存到session中的值的前缀
    app.config['SESSION_REDIS'] = redis.Redis(host='127.0.0.1',port=6379)  
    # app.session_interface = MySessionInterface()
    Session(app)
    # se=Session
    # se.init_app(app)
    # [START init_app]
    # Initalize the OAuth2 helper.
    # oauth2.init_app(
    #    app,
    #    scopes=['email', 'profile'],
    #    authorize_callback=_request_user_info)
    #
        
    # [END init_app]
    # Register the Bookshelf CRUD blueprint.
    from intWeb import applyform

    app.register_blueprint(applyform.crud,name="applyform", url_prefix='/applyform')

    # [START logout]
    # Add a logout handler.
    @app.route('/logout')
    def logout():
        # Delete the user's profile and the credentials stored by oauth2.
        del session['profile']
        session.modified = True
        #oauth2.storage.delete()
        return redirect(request.referrer or '/applyform/')
    # [END logout]

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            #user=get_model().readUser(username)
            user=get_model().User.query.filter_by(user=username).first()
            #session['username']
            #for record in records:
            if user:
              #if username == user["user"] and  password == user["Pass"] :
              if user.check_password(password):
                 session["user_id"] = user.id
                 session['profile'] = from_sql(user)
                 #return redirect(url_for('index'))
                 return redirect(url_for('EsAsset.list'))
                 
            
        return '''
            <div style="margin-top: 20%;margin-left:50%;margin-right:50%">
            <form method="post">
                <p>USER:<input type=text name=username>
                <p>PASS:<input type=password name=password>
                <p><input type=submit value=Login>
            </form>
            </div>
        '''
    
    # Add a default root route.
    @app.route("/")
    def index():
        return redirect(url_for('applyform.home'))

    @app.route("/index")
    def list():
        #token = request.args.get('page_token', None)
        #if token:
        #    token = token.encode('utf-8')
        #books, next_page_token = get_model().list(cursor=token)
        return render_template(
            "index.html")
            #books=books,
            #next_page_token=next_page_token)        
    
    @app.route("/sess")
    def showsess():    
        #s = json.dumps(session, indent=4, sort_keys=True)
        print ("*set session aa 1*")
        if (session['profile'] != None):
            if (session['profile'].get('aa') != None) :
               print(session['profile'].get('aa'))
               session["profile"]["aa"]= 1 + session["profile"].get("aa")
            else:
               session["profile"]["aa"]=0
        print(session)     
        print ("*2*")
        return str(session["profile"]["user"])

    @app.route("/profile")
    def showprofile():    
        #s = json.dumps(session, indent=4, sort_keys=True)
        print ("*profile 1*")
        print(session)     
        print ("*profile 2*")
        return str(session["profile"]["user"])

    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_sqlite_database', None)
        if db is not None:
            db.close()

    # Add an error handler. This is useful for debugging the live application,
    # however, you should disable the output of the exception for production
    # applications.
    @app.errorhandler(500)
    def server_error(e):
        return """
        An internal error occurred: <pre>{}</pre>
        See logs for full stacktrace.
        """.format(e), 500

    return app

def get_model():
    import intWeb.auth.models as model_cloudsql
    return model_cloudsql

def get_applyform_model():
    import intWeb.applyform.models as model_applyform
    return model_applyform


# [START request_user_info]
def _request_user_info(credentials):
    """
    Makes an HTTP request to the Google+ API to retrieve the user's basic
    profile information, including full name and photo, and stores it in the
    Flask session.
    """
    csid= request.cookies["connect.sid"]
    mgetdata =session.session_interface.redis.mget(["sess:"+csid[4:csid.find(".")]])
    print( "req user info")
    print( mgetdata)
    if mgetdata is None:
        return 0
    if mgetdata[0] is None:
        return 0
    my_bytes_value = mgetdata[0]
    my_json = my_bytes_value.decode('utf8').replace("'", '"').replace("passport","profile")
    data = json.loads(my_json)        
    if data["profile"] is None:
        return 0
    res_contxt=data["profile"].get("user") or 0  
    return res_contxt
    session['profile'] = data

# [END request_user_info]

def login_required_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('profile') is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


