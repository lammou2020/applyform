from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from intWeb.applyform.models import AppForm
from datetime import datetime
#datetime.strptime(start, '%Y-%m-%d')

builtin_list = list

def initdb_data(db,app):
    print("do it")
    db.drop_all()
    db.create_all()
    db.session.commit()

def from_sql(row):
    """Translates a SQLAlchemy model instance into a dictionary"""
    data = row.__dict__.copy()
    data['id'] = row.id
    data.pop('_sa_instance_state')
    return data

