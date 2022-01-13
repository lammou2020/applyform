from intWeb import storage, login_required_auth
from intWeb import get_applyform_model
from flask import flash,Blueprint, current_app, redirect, render_template, request, \
    session, url_for,send_file,Flask,send_from_directory,jsonify
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
@login_required_auth
def home():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')
    books, next_page_token = get_applyform_model().list(cursor=token)
    return render_template(
        "applyform/index.html",
        books=books,
        next_page_token=next_page_token)

@crud.route("/list")
@login_required_auth
def list():
    token = request.args.get('page_token', None)
    if token:
        token = token.encode('utf-8')
    books, next_page_token = get_applyform_model().list_desc(cursor=token)
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
    book = get_applyform_model().readUid(uid)
    return render_template("applyform/view.html", book=book)

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
    
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        ## If an image was uploaded, update the data to point to the new image.
        #path = current_app.config['HW_UPLOAD_FOLDER']
        #image_url = upload_image_file(request.files.get('image'),path,str(data["acno"]))
        #if image_url:
        #    data['imageUrl'] = image_url
        ## If the user is logged in, associate their profile with the new book.
        #if 'profile' in session:
        #    data['createdById'] = session['profile']['id']
        #book = get_applyform_model().create(data)
        #return redirect(url_for('.view', id=book['id']))
        captcha=str(session["captcha"])
        data['regSDate']=datetime.strptime(data['regSDate'].replace(" 00:00:00",""), '%Y-%m-%d')
        Error=None
        if data["captcha"]!=captcha :
            Error="captcha error!"
        if Error==None:
            data['acno']=str(hex(int(datetime.utcnow().timestamp())))
            book = get_applyform_model().create(data)
            return redirect(url_for('.view', uid=data['acno']))
        else:
            session["captcha"]=random.randint(100,648)            
            return render_template("applyform/form.html", action="Add", book=data, describ=Error)        
    session["captcha"]=random.randint(100,648)
    book={
        "time_period": id,
        "regSDate":datetime.today().strftime( '%Y-%m-%d')
        }
        
    return render_template("applyform/form.html", action="Add", book=book, describ="")
# [END add]


@crud.route('/<id>/edit', methods=['GET', 'POST'])
@login_required_auth
def edit(id):
    book = get_applyform_model().read(id)

    book["regSDate"]=book["regSDate"].strftime( '%Y-%m-%d')
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        path = current_app.config['HW_UPLOAD_FOLDER']
        image_url = upload_image_file(request.files.get('image'),path,str(data["acno"]))

        if image_url:
            data['imageUrl'] = image_url
        data['regSDate']=datetime.strptime(data['regSDate'], '%Y-%m-%d')
        book = get_applyform_model().update(data, id)

        return redirect(url_for('.view', id=book['id']))

    return render_template("applyform/form.html", action="Edit", book=book)


@crud.route('/<id>/delete')
@login_required_auth
def delete(id):
    book = get_applyform_model().read(id)
    Err=CheckOwnRecordErr(book,session)
    if Err != None:  return Err
    crspath=book["Path"]
    if (book["createdById"]==str(session['profile']['id']))  :

        path = current_app.config['HW_UPLOAD_FOLDER']
        UPLOAD_FOLDER = os.path.join(path, crspath)
        for root,dirs, files in os.walk(UPLOAD_FOLDER):
           for file in files:      
               os.remove(UPLOAD_FOLDER+"/"+file)
        get_assest_model().delete(id)        
    return redirect(url_for('.list'))


@crud.route("/<id>/itemgrid")
@login_required_auth
def itemgrid(id):
    book = get_applyform_model().read(id)
    Err=CheckOwnRecordErr(book,session)
    if Err != None:  return Err
    book["regSDate"]=book["regSDate"].strftime( '%Y-%m-%d')
    items= get_applyform_model().Itemlist_by_acno(book["acno"])
    filenames=[]
    #Get_FileList(book,filenames)             
    
    return render_template("applyform/grid.html", book=book,items=items,lecturesfile=[],filenames=filenames)

@crud.route("/itemCateGrid")
@login_required_auth
def itemCateGrid():
    items= get_applyform_model().ItemCatlist()
    return render_template("applyform/itemCategory/grid.html", items=items)

@crud.route('/itemCateGrid_/addbatch/<cnt>', methods=['GET', 'POST'])
@login_required_auth
def itemcataddbatch(cnt):
    items= get_applyform_model().createItemCat_blank(int(cnt))
    return f"{cnt}"

@crud.route('/itemCateGrid_/api/JSON/update/<itemcat_id>', methods=['GET', 'POST'])
@login_required_auth
def itemCateGridJsonUpdate(itemcat_id):
    data=request.get_json()
    #if 'regSDate' in data:
    #    data['regSDate']=datetime.strptime(data['regSDate'], '%Y-%m-%d')
    #if 'itemno' in data:   
    #    if data["itemno"]=="" or data["itemno"]=="None" or data["itemno"]==None:
    #        data["itemno"]=None
    #    else:
    #        pass
    #if 'itemcatno' in data:   
    #    if data["itemcatno"]=="" or data["itemcatno"]=="None" or data["itemcatno"]==None:
    #        data["itemcatno"]=None
    #    else:
    #        pass            
    book = get_applyform_model().updateItemCat(data, itemcat_id)
    return jsonify( book)

@crud.route('/itemCateGrid_/api/OUTJSON', methods=['GET', 'POST'])
@login_required_auth
def itemCateGridApiOUTJSON():
    items= get_applyform_model().ItemCatlist()
    return jsonify(items)

@crud.route('/JSON/db/<tablename>')
@login_required_auth
def JSON_DB(tablename):
    book = get_applyform_model().readAllFromTable(tablename)
    return jsonify(book)

def convert_timestamp(item_date_object):
    if isinstance(item_date_object, (date, datetime)):
        return item_date_object.timestamp()

@crud.route('/JSON/file/<tablename>')
@login_required_auth
def JSON_DBFILE(tablename):
    book = get_applyform_model().readAllFromTable(tablename)
    xml =json.dumps(book,default=convert_timestamp)
    return Response(xml, mimetype='text/json',content_type="text/plain;charset=UTF-8")

@crud.route("/qrcode",methods=["GET"])
def get_qrcode():
    data = request.args.get("data", "")
    return send_file(qrcode(data, mode="raw"), mimetype="image/png")
