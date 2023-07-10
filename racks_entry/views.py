from django.shortcuts import render, redirect
from django.http import HttpResponse
import pandas as pd
import sqlite3
import datetime as dt
from io import BytesIO

def download_inv(request):

    conn = sqlite3.connect('racks_entry.sqlite')

    fn = f"racks_entry.xlsx"

    with BytesIO() as b:
        with pd.ExcelWriter(b) as writer:
            df = pd.read_sql(con=conn, sql="SELECT * FROM 'racks';")
            df.to_excel(writer, sheet_name='racks', index=False)
        res = HttpResponse(
            b.getvalue(), # Gives the Byte string of the Byte Buffer object
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    res['Content-Disposition'] = f'attachment; filename={fn}'

    conn.close()

    return res

# Create your views here.
loggedin = False
NAME = None


def rinv(request, notify=None):
    global loggedin
    global NAME
    

    if loggedin ==True:
        if request.method=="POST":
            if "showInventory" in request.POST:
                conn = sqlite3.connect("racks_entry.sqlite")
                df = pd.read_sql(con= conn, sql="SELECT * FROM racks;")
                tab = df.to_html()
                return render(request, 'dashboard/dashboard.html', {'data': tab, 'notify': None})

            elif "sid" in request.POST:
                
                dat = dt.datetime.now().strftime("%d/%m/%Y")
                try:
                    sId = request.POST.get("sid")
                except:
                    sId = 0
                try:
                    edt = request.POST.get("edtas")
                except:
                    edt = 0
                try:
                    rkno = request.POST.get("rackno")
                except:
                    rkno = None
                try:
                    iss = request.POST.get("issue")
                except:
                    iss = None    

                if notify == None:
                        notify = "Unable to add the entry"

                if (sId == None and edt == None) or (sId == '' and edt == '') or (sId == None and rkno == None) or (sId == '' and rkno == ''):

                        return render(
                            request,
                            'dashboard/dashboard.html',
                            {'notify': notify}
                        )        
               

                conn = sqlite3.connect("racks_entry.sqlite")
                df = pd.read_sql(con=conn, sql="SELECT * FROM 'racks';")
                last_row = df.iloc[len(df)-1]
                sno = last_row['Sno']


                qy= f"""INSERT INTO 'racks' VALUES ({sno} ,'{sId}', {edt}, '{rkno}', '{iss}', '{dat}', '{NAME}');"""

                cur = conn.cursor()
                cur.execute(qy)


                conn.commit()
                df = pd.read_sql(con=conn, sql="SELECT * FROM 'racks';")
                tab = df.to_html()
                conn.close()
                notify = "Successfully inserted the record"

                return render(
                    request,
                    'dashboard/dashboard.html',
                    {'data':tab,'notify': notify}
                    ) 

            elif "logout" in request.POST:
                loggedin = False
                return redirect(to='/login/')
            else:
                return render(request, 'dashboard/dashboard.html', {'data': None, 'notify': None})   

            
        return render(request, 'dashboard/dashboard.html', {'data': None, 'notify': None})
    return redirect("/login/")


def auth_login(user, pas):
    con = sqlite3.connect("db.sqlite3")
    cur = con.cursor()
    try:
        q = f"SELECT * FROM users WHERE (user='{user}') AND (password='{pas}')"
        res = cur.execute(q).fetchall()
    except:
        q = """
        CREATE TABLE "users" (
	            "user" TEXT,
	            "password" TEXT
            );
        """
        cur.execute(q)
        res = 0
    con.close()
    if len(res) > 0:
        return True
    return False

def index(request):

    global loggedin
    global NAME

    print(loggedin)

    if loggedin == False:
        if request.method == 'POST':
            if 'user' in request.POST and 'password' in request.POST:
                un = request.POST.get('user')
                pas = request.POST.get('password')
                check = auth_login(un, pas)
                if check == True:
                    loggedin = True
                    NAME = un
                    return redirect(to='/dashboard/')
                else:
                    return render(
                        request,
                        'login/login.html',
                        {'note': 'Wrong User or Password!'}
                    )
            else:
                return render(request, 'login/login.html')
        else:
            return render(request, 'login/login.html')
    else:
        return redirect(to='/dashboard/')



def signup(request):
    global loggedin
    if request.method == "POST":
        print(request.POST)
        un = request.POST.get('username_su')
        pas = request.POST.get('password_su')
        conn = sqlite3.connect("db.sqlite3")
        cur = conn.cursor()
        q = f"INSERT INTO 'users' VALUES('{un}', '{pas}');"
        try:
            cur.execute(q)
        except:
            qn = """
            CREATE TABLE "users" (
                    "user" TEXT,
                    "password" TEXT
                );
            """
            cur.execute(qn)
        cur.execute(q)
        conn.commit()
        conn.close()
        return redirect(to='/login')
    if loggedin == True:
        return redirect(to='/dashboard/')
    return render(request, 'signup/sign_up.html')

