from intWeb import storage, login_required_auth
from intWeb import get_applyform_model
from flask import flash,Blueprint, current_app, redirect, render_template, request, \
    session, url_for,send_file,Flask,send_from_directory,jsonify
import redis
import os
import zipfile
import math
import random
from urllib.parse import quote
from datetime import datetime,date
from flask import Response
import json


from flask_qrcode import QRcode
qrcode=QRcode(current_app)

crud = Blueprint('crud', __name__)

limits=[210,210,300,210,300]

redis_grpcnt="openday_grpcnt_list"

def upload_hw_file(file,UPLOAD_FOLDER,seat):
    if not file:
        return None
    public_url = storage.upload_hw_file(
        file,
        file.filename,
        file.content_type,
        UPLOAD_FOLDER,
        0,
        seat
    )
    current_app.logger.info(
        "Uploaded file %s as %s.", file.filename, public_url)
    return public_url

def upload_image_file(file,UPLOAD_FOLDER,pixStr=None):
    """
    Upload the user-uploaded file to Google Cloud Storage and retrieve its
    publicly-accessible URL.
    """
    if not file:
        return None
    public_url = storage.upload_file(
        file,#.read(),
        file.filename,
        file.content_type,
        UPLOAD_FOLDER,
        pixStr,
        "applyform",
    )
    current_app.logger.info(
        "Uploaded file %s as %s.", file.filename, public_url)
    return public_url

@crud.route("/")
def home():
    red=redis.Redis()
    res=red.get(redis_grpcnt)
    
    grpcnts=[0,0,0,0,0,0]
    if res==None:
        count_grp=get_applyform_model().count_grp()
        for cgp_ in count_grp:
            grpcnts[cgp_[0]]=cgp_[1]
        red.set(redis_grpcnt,json.dumps(grpcnts))
    else:
        grpcnts=json.loads(res)
        print("redis load")
        
    return render_template(
        "applyform/index.html",
        limits=limits,count_grp=grpcnts)

@crud.route("/list")
@login_required_auth
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')
    books, next_page_token = get_applyform_model().list_desc(cursor=token) #.list
    return render_template(
        "applyform/list.html",
        books=books,
        next_page_token=next_page_token)

def Get_FileList(crspath, filenames, prefix=None):
    path = current_app.config['HW_UPLOAD_FOLDER']
    LECTURE_FOLDER = os.path.join(path, crspath)
    if not os.path.isdir(LECTURE_FOLDER):
        os.mkdir(LECTURE_FOLDER)
    else:
        for root,dirs, files in os.walk(LECTURE_FOLDER):
            for file in files:
                if prefix==None:
                    basename, extension = file.rsplit('.', 1)
                    _file=basename.split('-_')[0]+"."+extension
                    filenames.append({"f":quote(str(file)),"n":_file})    
                elif prefix in file:
                    basename, extension = file.rsplit('.', 1)
                    _file=basename.split('-_')[0]+"."+extension
                    filenames.append({"f":quote(str(file)),"n":_file})    
    pass

#####
# [START add]

#####
@crud.route('/<uid>')
def view(uid):

    if session.get("captcha")!=None and  session.get("re_captcha")!=None and  str(session["captcha"])==str(session["re_captcha"]):
        book = get_applyform_model().readUid(uid)
        qrcode_txt=book["acno"].replace("0x","")
        return render_template("applyform/view.html", book=book,qrcode_txt=qrcode_txt)
    else:
        return render_template("applyform/queryform.html")

@crud.route('/<id>/captcha_text', methods=['GET', 'POST'])
def captcha_text(id):
    return str(session["captcha"])

@crud.route('/<id>/captcha', methods=['GET', 'POST'])
def captcha(id):
    captcha=str(session["captcha"])
    FilePath=f"C:/databucket/captcha/{captcha}.gif"
    if os.path.exists(FilePath):
        return send_file(FilePath,
                mimetype = 'image/*',
                )
    else:
        return captcha

# [START add]
@crud.route('/<id>/add', methods=['GET', 'POST'])
def add(id):
    rnd = int(datetime.utcnow().timestamp())
    if request.method == 'POST':
        if session.get("captcha")==None:
            return "Error !"

        count_grp=get_applyform_model().count_grp()  
        data = request.form.to_dict(flat=True)
        captcha=str(session["captcha"])
        data['regSDate']=datetime.strptime(data['regSDate'].replace(" 00:00:00",""), '%Y-%m-%d')
        Error=None
        grpcnts=[0,0,0,0,0,0]
        if id!=data["time_period"]:
            Error="Error !"
        elif len(data["apply_name"])<2:
            Error="請填申請人 !"
        elif data['attendance']=="2" and len(data["name1"])<2:
            Error="請填 出席2 !"
        elif data['attendance']=="3" and len(data["name2"])<2:
            Error="請填 出席3 !"
        elif data["captcha"]!=captcha :
            Error="驗證碼不正确!"
        else:
            count_grp=get_applyform_model().count_grp()     
            for g_ in count_grp:
                grpcnts[g_[0]]=g_[1]
                if g_[0]==int(id) and g_[1]>=limits[g_[0]-1]:
                    Error=f" {g_[1]} / {limits[g_[0]-1]}  人數太多了,請選擇其他時段!"

        if Error==None:
            data['acno']=str(hex(int(datetime.utcnow().timestamp())))
            book = get_applyform_model().create(data)
            red=redis.Redis()
            res=json.loads(red.get(redis_grpcnt))            
            res[int(id)]=res[int(id)]+int(data['attendance'])
            red.set(redis_grpcnt,json.dumps(res))
            session["re_captcha"]=captcha
            return redirect(url_for('.view', uid=data['acno']))
        else:
            session["captcha"]=random.randint(100,648)            
            return render_template("applyform/form.html", action="Add", book=data, describ=Error,rnd=rnd)        
    session["captcha"]=random.randint(100,648)
    book={
        "time_period": id,
        "regSDate":datetime.today().strftime( '%Y-%m-%d')
        }
        
    return render_template("applyform/form.html", action="Add", book=book, describ="", rnd=rnd)
# [END add]


@crud.route('/update_redis', methods=['GET', 'POST'])
def update_redis():
    red=redis.Redis()
    grpcnts=[0,0,0,0,0,0]
    count_grp=get_applyform_model().count_grp()
    for cgp_ in count_grp:
        grpcnts[cgp_[0]]=cgp_[1]
    red.set(redis_grpcnt,json.dumps(grpcnts))
        
    return render_template(
        "applyform/index.html",
        limits=limits,count_grp=grpcnts)

@crud.route("/qrcode",methods=["GET"])
def get_qrcode():
    data = request.args.get("data", "")
    return send_file(qrcode(data, mode="raw"), mimetype="image/png")
