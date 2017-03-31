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

   # try:
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
        return render_template('success.html')
      return render_template('bill.html', items=item)

   # except Exception as e:
    #    print(e)
    #    return render_template('error.html')
if __name__ == '__main__':
    app.run(debug = True)