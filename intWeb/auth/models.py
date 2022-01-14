from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

builtin_list = list
from intWeb import db
#db = SQLAlchemy()

def init_app(app):
    # Disable track modifications, as it unnecessarily uses memory.
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)

def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(255), unique=True, nullable=False)
    _password = db.Column("password", db.String(225), nullable=False)
    #Pass = db.Column(db.String(255))
    Name = db.Column(db.String(255))
    Classno = db.Column(db.String(255))
    Seat = db.Column(db.String(255))
    Role = db.Column(db.String(255))

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        """Store the password as a hash for security."""
        self._password = generate_password_hash(value)

    def check_password(self, value):
        return check_password_hash(self.password, value)

    def __init__(self, user=None, password=None,Name=None,Role=None,Classno=None,Seat=None):
        self.user = user
        self.password = password
        self.Name = Name
        self.Role=Role
        self.Classno=Classno
        self.Seat=Seat

    def __repr__(self):
        return "<User(User='%s', Role=%s)" % (self.user, self.Role)

def readUser(UserName):
    result = User.query.filter_by(user=UserName).first()
    #get(UserName)
    if not result:
        return None
    return from_sql(result)

#insert into user (user,Pass,Name,Role) values('admin','123','admin',1);

def _create_database():
    """
    If this script is run directly, create all the tables necessary to run the application.
    """
    app = Flask(__name__)
    app.config.from_pyfile('../../config.py')
    init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin = User("admin","123","admin","1")
        studa = User("stu","123","stu","8","SC1A","01")
        studb = User("sta","123","stu","8","SC2A","01")
        db.session.add(admin)
        db.session.add(studa)
        db.session.add(studb)
        db.session.commit()
    print("All tables created")

if __name__ == '__main__':
    _create_database()
