import os
PORT=86
MAX_CONTENT_LENGTH = 8 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
# Image Path
UPLOAD_FOLDER=os.getcwd()+"\\TEMP"
HW_UPLOAD_FOLDER="c:/ASSET_FOLDER/DOC/"
HW_TEMP_FOLDER="c:/ASSET_FOLDER/TEMP/"

# [START secret_key]
SECRET_KEY = 'catcat'
SESSION_COOKIE_NAME='connect.sid'
REDIS_PORT=6379
# [END secret_key]

#DATA_BACKEND = 'mysql'
DATA_BACKEND = 'sqlite'

SQLITE_PATH=f"{os.getcwd()}\\bookshelf.db"
SQLALCHEMY_SQLITE_URI = ( 'sqlite:///{path}').format(path=SQLITE_PATH)

MYSQL_HOST='127.0.0.1'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_DATABASE = 'bookshelf'
SQLALCHEMY_MYSQL_URI = (
    'mysql+pymysql://{user}:{password}@{host}:3306/{database}?charset=utf8mb4').format(
        user=MYSQL_USER, password=MYSQL_PASSWORD,host=MYSQL_HOST,
        database=MYSQL_DATABASE)

if DATA_BACKEND=='mysql':  
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_MYSQL_URI
else:
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_SQLITE_URI

