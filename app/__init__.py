import datetime
from flask import *
import MySQLdb
import gc

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user="root",
                           passwd="admin",
                           db="inventory")
    c = conn.cursor()
    return c, conn


app = Flask(__name__)
@app.route('/', methods=["GET", "POST"])
def login():
    error=''
    try:
      c,conn = connection()
      if request.method == "POST":

         attempted_username = request.form['username']
         attempted_password = request.form['password']


         if attempted_username == "admin" and attempted_password == "admin":
             return render_template('home.html')

         data = c.execute("SELECT * FROM users WHERE username = (%s)",
                              request.form['username'])
         data = c.fetchone()


         if attempted_username == data[0] and attempted_password == data[1]:
             return render_template('home.html')
         else:
             error="Invalid Credentials , try again."
      gc.collect()
      return render_template('login.html',error =error)
    except Exception as e:
        # flash(e)
        error = "Invalid credentials, try again."
        return render_template('login.html', error=error)

@app.route('/stock/')
def print_stock():
        c, conn = connection()
        cursor = c.execute('SELECT * FROM stock')
        item = [dict(pid=row[0],
                        pname=row[1],
                        quantity=row[2],
                        price=row[3]) for row in c.fetchall()]
        return render_template('stock.html', items=item)


@app.route('/home/')
def home():
  return render_template('home.html')

@app.route('/bill/',methods = ["GET","POST"])
def bill():
    error =''
    try:
      c, conn = connection()
      cursor = c.execute('SELECT * FROM stock')
      item = [dict(pname=row[1], price=row[3]) for row in c.fetchall()]
      if request.method == "POST":
            i = 0
            name = "123"
            productarr = []
            qtyarr = []
            pricearr =[]

            while 'product_name' + str(i) in request.form:
                 n = "product_name" + str(i)
                 q = "qty" + str(i)
                 p = "price" + str(i)

                 name = request.form[n]
                 qty = request.form[q]
                 price = request.form[p]

                 productarr.append(name)
                 qtyarr.append(qty)
                 pricearr.append(price)
                 i=i+1

            sql=[]

            date = request.form['date']
            total =  request.form['total']

            data = c.execute('SELECT * FROM bill ORDER BY bill_no DESC LIMIT 1')
            data = c.fetchone()
            bill_number = data[0]
            bill_number = bill_number + 1

            for j in range(1, len(productarr) + 1):
                pname = productarr[j - 1]
                qty = qtyarr[j - 1]
                data = c.execute("SELECT * FROM stock WHERE pname = '%s'" % (pname))
                data = c.fetchone()
                qty_total = int(data[2]) - int(qty)
                if qty_total < 0:
                    error = "Product Out Of Stock!!"
                    return render_template('bill.html',items=item,error=error)

            sql.append("INSERT INTO bill VALUES('%s','%s','%s')" %(bill_number,date,total))
            cursor = c.execute(sql[0])
            conn.commit()

            for j in range(1,len(productarr)+1) :
                 pname = productarr[j - 1]
                 qty = qtyarr[j - 1]
                 price = pricearr[j - 1]
                 sql.append("INSERT INTO items VALUES('%s','%s','%s','%s')" %(bill_number,pname,qty,price))
                 cursor = c.execute(sql[j])
                 conn.commit()

            for j in range(1, len(productarr) + 1):
                pname = productarr[j - 1]
                qty = qtyarr[j - 1]
                data = c.execute("SELECT * FROM stock WHERE pname = '%s'" % (pname))
                data = c.fetchone()
                qty_total = int(data[2]) - int(qty)
                sqlBill="UPDATE stock SET qty ='%s' WHERE pname='%s'" % (qty_total, pname)
                cursor = c.execute(sqlBill)
                conn.commit()

            return render_template('success.html')
      return render_template('bill.html',items=item,error=error)
    except Exception as e:
         print(e)
         return render_template('error.html')


@app.route('/ae/',methods = ["GET","POST"])
def add_employee():
    error=''
    try:
        c, conn = connection()
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            confirmpassword = request.form['confirmpassword']

            if( password != confirmpassword):
                error='Password Mismatch'
                return render_template('add_employee.html', error=error)

            firstname = request.form['firstname']
            middlename = request.form['middlename']
            lastname = request.form['lastname']
            dob = request.form['dob']
            dob = datetime.datetime.strptime(dob, "%d-%m-%Y").strftime("%Y-%m-%d")
            ph_number = request.form['ph_number']
            address = request.form['address']

            data = c.execute('SELECT * FROM person ORDER BY id DESC LIMIT 1')
            data = c.fetchone()
            id = data[0]
            id = id + 1

            salary = request.form['salary']

            sqllogin = "INSERT INTO users VALUES('%s','%s')" %(username,password)
            cursor = c.execute(sqllogin)
            conn.commit()

            sqlpersonal = "INSERT INTO person VALUES('%s','%s','%s','%s','%s')" % (id,firstname,middlename,lastname,ph_number)
            cursor = c.execute(sqlpersonal)
            conn.commit()

            sqlothers = "INSERT INTO employee VALUES('%s','%s','%s','%s')" % (id,salary,address,dob)
            cursor = c.execute(sqlothers)
            conn.commit()

            return render_template('home.html')

        return render_template('add_employee.html',error=error)

    except Exception as e:
          print(e)
          return render_template('error.html')

@app.route('/as/',methods = ["GET","POST"])
def add_supplier():
    try:
        c, conn = connection()
        if request.method == "POST":
            firstname = request.form['fname']
            middlename = request.form['mname']
            lastname = request.form['lname']
            ph_number = request.form['ph_number']
            email = request.form['email']

            data = c.execute('SELECT * FROM person ORDER BY id DESC LIMIT 1')
            data = c.fetchone()
            id = data[0]
            id = id + 1

            sqlpersonal = "INSERT INTO person VALUES('%s','%s','%s','%s','%s')" % (id, firstname, middlename, lastname, ph_number)
            cursor = c.execute(sqlpersonal)
            conn.commit()

            sqlsupplier = "INSERT INTO supplier VALUES('%s','%s')" %(id,email)
            cursor = c.execute(sqlsupplier)
            conn.commit()

            return render_template('home.html')

        return render_template('add_supplier.html')

    except Exception as e:
        print(e)
        return render_template('error.html')


@app.route('/vs/',methods = ["GET","POST"])
def view_supplier():
    try:
        c, conn = connection()
        cursor = c.execute('SELECT * FROM person NATURAL JOIN supplier')
        item = [dict(id=row[0], name=row[1] + " " + row[3],ph_number = row[4],email = row[5]) for row in c.fetchall()]
        return render_template('view_supplier.html',items = item)
    except Exception as e:
        print(e)
        return render_template('error.html')

@app.route('/ve/',methods = ["GET","POST"])
def view_employee():
    try:
        c, conn = connection()
        cursor = c.execute('SELECT * FROM person NATURAL JOIN employee')
        item = [dict(id=row[0], name=row[1] + " " + row[3],ph_number = row[4],salary = row[5],dob=row[7]) for row in c.fetchall()]
        return render_template('view_employee.html',items=item)
    except Exception as e:
        print(e)
        return render_template('error.html')


@app.route('/order/',methods = ["GET","POST"])
def order():
    try:
          c, conn = connection()
          cursor = c.execute('SELECT * FROM stock')
          item = [dict(pname=row[1]) for row in c.fetchall()]
          if request.method == "POST":
              i = 0
              name = "123"
              productarr = []
              qtyarr = []
              pricearr = []

              while 'product_name' + str(i) in request.form:
                  n = "product_name" + str(i)
                  q = "qty" + str(i)
                  p = "price" + str(i)

                  name = request.form[n]
                  qty = request.form[q]
                  price = request.form[p]

                  productarr.append(name)
                  qtyarr.append(qty)
                  pricearr.append(price)
                  i = i + 1

              sql = []

              date = request.form['date']
              total = request.form['total']

              data = c.execute('SELECT * FROM purchase ORDER BY oid DESC LIMIT 1')
              data = c.fetchone()
              oid = data[0]
              oid = oid + 1

              sql.append("INSERT INTO purchase VALUES('%s','%s','%s')" % (oid, date, total))
              cursor = c.execute(sql[0])
              conn.commit()

              for j in range(1, len(productarr) +1 ):
                  pname = productarr[j - 1]
                  qty = qtyarr[j - 1]
                  price = pricearr[j - 1]
                  data = c.execute("SELECT * FROM stock WHERE pname = '%s'" %(pname))
                  data = c.fetchone()
                  pid = data[0]
                  sqlOrder = "INSERT INTO order_table VALUES('%s','%s','%s','%s')" % (oid, pid, qty, price)
                  cursor = c.execute(sqlOrder)
                  conn.commit()

              for j in range(1, len(productarr) + 1):
                  pname = productarr[j - 1]
                  qty = qtyarr[j - 1]
                  price = pricearr[j - 1]
                  data = c.execute("SELECT * FROM stock WHERE pname = '%s'" % (pname))
                  data = c.fetchone()
                  nullCheck = data[2]
                  if nullCheck is None:
                      qty_total =  qty
                      sql.append("UPDATE stock SET qty ='%s' WHERE pname='%s'" % (qty_total, pname))
                      cursor = c.execute(sql[j])
                      conn.commit()
                      c.execute("UPDATE stock SET price ='%s' WHERE pname='%s'" %(price, pname))
                      conn.commit()
                  else:
                      qty_total = int(data[2]) + int(qty)
                      sql.append("UPDATE stock SET qty ='%s' WHERE pname='%s'" % (qty_total,pname))
                      cursor = c.execute(sql[j])
                      conn.commit()


              return render_template('success.html')
          return render_template('order.html', items=item)
    except Exception as e:
         print(e)
         return render_template('error.html')

@app.route('/ue/',methods = ["GET","POST"])
def update_employee():
     try:
          c, conn = connection()
          cursor = c.execute("SELECT id FROM employee")
          item = [dict(id=row[0]) for row in c.fetchall()]
          if request.method == "POST":

              if request.form['submit'] == "Show Details":
                  id = request.form['id']
                  c.execute("SELECT * FROM employee NATURAL JOIN person WHERE id ='%s'" %id )
                  row = c.fetchone()
                  salary = int(row[1])
                  address = str(row[2])
                  dob = str(row[3])
                  firstanme = str(row[4])
                  middlename =str(row[5])
                  lastname= str(row[6])
                  ph_number = str(row[7])
                  return render_template('update_employee.html',id=id, items=item, salary=salary, address=address, dob=dob,
                                         firstname=firstanme,userid=id,
                                         middlename=middlename, lastname=lastname, ph_number=ph_number)


              if request.form['submit'] == "DELETE" :
                   id = request.form['id']
                   c.execute("DELETE FROM person WHERE id ='%s'" %id)
                   conn.commit()
                   return render_template('home.html')


              if  request.form['submit'] == "Submit" :
                   id = request.form['userid']

                   firstname = request.form['firstname']
                   middlename = request.form['middlename']
                   lastname = request.form['lastname']
                   dob = request.form['dob']
                   ph_number = request.form['ph_number']
                   address = request.form['address']
                   salary = request.form['salary']

                   c.execute("UPDATE person SET firstname='%s' WHERE id='%s'" %(firstname,id))
                   conn.commit()

                   c.execute("UPDATE person SET middlename='%s' WHERE id='%s'" % (middlename, id))
                   conn.commit()

                   c.execute("UPDATE person SET lastname='%s' WHERE id='%s'" % (lastname, id))
                   conn.commit()

                   c.execute("UPDATE person SET ph_number='%s' WHERE id='%s'" % (ph_number, id))
                   conn.commit()

                   c.execute("UPDATE employee SET salary='%s' WHERE id='%s'" % (salary, id))
                   conn.commit()

                   c.execute("UPDATE employee SET address='%s' WHERE id='%s'" % (address, id))
                   conn.commit()

                   c.execute("UPDATE employee SET dob='%s' WHERE id='%s'" % (dob, id))
                   conn.commit()

                   return  render_template('home.html')
          return render_template('update_employee.html',items=item)

     except Exception as e:
          print(e)
          return render_template('error.html')

@app.route('/new_product/',methods = ["GET","POST"])
def new_product():
     try:
         c, conn = connection()
         if request.method == "POST":
             data = c.execute('SELECT * FROM stock ORDER BY pid DESC LIMIT 1')
             data = c.fetchone()
             id = data[0]
             id = id + 1
             i=0;
             productarr = []

             while 'product_name' + str(i) in request.form:
                 n = "product_name" + str(i)
                 name = request.form[n]
                 productarr.append(name)
                 i=i+1

             sql=[]

             for j in range(0, len(productarr)):
                 pname = productarr[j]
                 sqlNewProduct = ("INSERT INTO product VALUES('%s','%s')" % (id, pname))
                 cursor = c.execute(sqlNewProduct)
                 sql.append("INSERT INTO stock VALUES('%s','%s',NULL,NULL)" % (id, pname))
                 cursor = c.execute(sql[j])
                 conn.commit()

                 conn.commit()
                 id=id+1

             return render_template('home.html')

         return render_template('new_product.html')

     except Exception as e:
         print(e)
         return render_template('error.html')


if __name__ == '__main__':
    app.run(debug = True)