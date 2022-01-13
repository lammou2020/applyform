import intWeb
import config
import sys
from waitress import serve

args = sys.argv[1:]

if "--help" in args:
    print("--initdb")
    print("--inititemcat")
    print(f"default: run on {config.PORT}.")

if "--initdb" in args:
    intWeb.init_db_flag=True
    from shutil import copyfile
    import re
    import datetime
    import os
    datetime_str=re.sub("[ .:]","_",datetime.datetime.now().isoformat())
    filepath="bookshelf.db"
    if os.path.isfile(filepath):
        copyfile(filepath, f"bookshelf{datetime_str}.db")

if "--inititemcat" in args:
    import sqlite3
    con = sqlite3.connect('c:/code/EsAsset/bookshelf.db')
    cur = con.cursor()
    cnt=0
    with open("c:/code/EsAsset/intWeb/templates/esasset/control/itemcategory.html", "w", encoding='utf-8') as outfile:
        for row in cur.execute(f"select * from itemCategory;"):
            if row[1]==0: break
            if row[2]==0:
                cnt=cnt+1
                rcnt=0
                if cnt>1: outfile.write("</div></div></div>")
                outfile.write(f"<div id='PTYPE{row[1]}_menudialog'><div id='PTYPE{row[1]}_accordion'>")
            if row[4]==-1:
                rcnt=rcnt+1
                if rcnt>1 : outfile.write("</div>")
                h3=row[3] 
                outfile.write(f'<h3><a href=#>{row[1]} {h3}</a></h3>')
                outfile.write('<div style="margin:0;padding:0;">')
            if row[4]>-1:
                outfile.write(f'<h4><a href=# onclick="GetNewItemNo({row[1]}{row[2]:03d},{row[4]},this);">{row[1]}{row[2]:03d} {row[3]}</a></h4>');
        outfile.write("</div></div></div>")
    pass        

app = intWeb.create_app(config)

if "--inscat" in args:
    from intWeb import db
    from intWeb.esasset.models import ItemCategory
    with app.app_context():
        for i in range(650):
            u_= ItemCategory(
                  itemcat_pri='0',
                 itemcat_sec='0',
                 name="",
                 depr_year=0)
            db.session.add(u_)
        db.session.commit()
    print("ins rows!")



# This is only used when running locally. When running live, gunicorn runs
# the application.

if __name__ == '__main__':
    if "--help" in args:
        pass
    elif "--initdb" in args:
        pass
    elif "--inscat" in args:
        pass
    elif "--inititemcat" in args:
        pass
    else:
        app.run( host="0.0.0.0",port=config.PORT, debug=True) #serve(app, host="0.0.0.0",port=83)
