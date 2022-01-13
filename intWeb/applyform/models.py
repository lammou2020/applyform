from datetime import datetime
from flask import Flask
from sqlalchemy.sql.elements import between
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

builtin_list = list

#db = SQLAlchemy()
from intWeb import db

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

# AppForm
class AppForm(db.Model):
    __tablename__ = 'AppForm'
    id= db.Column(db.Integer,primary_key=True) # 編號
    acno = db.Column(db.String(16),unique=True,nullable=True)  #按項目/發票定義 ACC[FA2021-xxx-001/-00[1-9]
    apply_name =db.Column(db.String(80))  # 憑單編號
    name1=db.Column(db.String(80))  # 憑單編號
    name2 =db.Column(db.String(80))  # 憑單編號
    tel =db.Column(db.String(80))  # 憑單編號
    captcha =db.Column(db.String(80))  # 憑單編號
    time_period =db.Column(db.Integer)  # 憑單編號
    regSDate= db.Column(db.DateTime, nullable=False,default=datetime.utcnow) #登記日期
    createdById = db.Column(db.String(255))    
    utime    = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)  #更新时间

    def __init__(self, 
                acno=None, 
                apply_name=None, 
                name1=None, 
                name2=None, 
                tel=None, 
                time_period=None,
                regSDate=None,
                captcha=None,
                createdById=None
        ):
        self.acno=acno
        self.apply_name=apply_name
        self.name1=name1
        self.name2=name2
        self.tel=tel
        self.time_period=time_period
        self.regSDate=regSDate
        self.captcha=captcha
        self.createdById=createdById

    def __repr__(self):
        return "<AppForm(no='%s', name=%s)" % (self.acno, self.apply_name)    

# [ ACC crud]
def read(id):
    result = AppForm.query.get(id)
    if not result:
        return None
    return from_sql(result)

def readUid(Uid):
    result = AppForm.query.filter_by(acno=Uid)
    if not result:
        return None
    return result


def create(data):
    acc = AppForm(**data)
    db.session.add(acc)
    db.session.commit()
    return from_sql(acc)

def update(data, id):
    acc = AppForm.query.get(id)
    for k, v in data.items():
        setattr(acc, k, v)
    db.session.commit()
    return from_sql(acc)

def delete(id):
    AppForm.query.filter_by(id=id).delete()
    db.session.commit()

def createAppForm_Blank(data,cnt):
    for i in range(cnt):
        acc = AppForm(**data)
        db.session.add(acc)
    db.session.commit()
    return from_sql(acc)

def updateAppForm_DataSet(data):
    for id in data:
        acc = AppForm.query.get(id)
        for k, v in data[id].items():
            setattr(acc, k, v)
    db.session.commit()
    return ""


# [START list_asc]
def list(limit=10, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (AppForm.query
             #.filter_by(Open=1)
             .order_by(AppForm.id)
             .limit(limit)
             .offset(cursor))
    lessons = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(lessons) == limit else None
    return (lessons, next_page)

# [START list_desc]
def list_desc(limit=10, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (AppForm.query
             #.filter_by(Open=1)
             .order_by(desc(AppForm.id))
             .limit(limit)
             .offset(cursor))
    lessons = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(lessons) == limit else None
    return (lessons, next_page)

# [START list_by_user]
def list_by_user(user_id, limit=10, cursor=None):
    cursor = int(cursor) if cursor else 0
    query = (AppForm.query
             .filter_by(createdById=user_id)
             .order_by(AppForm.id)
             .limit(limit)
             .offset(cursor))
    lessons = builtin_list(map(from_sql, query.all()))
    next_page = cursor + limit if len(lessons) == limit else None
    return (lessons, next_page)
# [END list_by_user]


# maintian tools [ Read rows by tablename, for backup data.]
def readAllFromTable(tablename):
    if tablename=="AppForm":
        query = (AppForm.query
                 .order_by(AppForm.id))
        lessons = builtin_list(map(from_sql, query.all()))
        return (lessons)

    return None

def _create_database():
    """
    If this script is run directly, create all the tables necessary to run the application.
    """
    app = Flask(__name__)
    app.config.from_pyfile('../../config.py')
    init_app(app)
    with app.app_context():
        #db.drop_all()
        #db.create_all()
        db.session.commit()
    print("All tables created")

if __name__ == '__main__':
    _create_database()