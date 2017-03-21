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

@app.route('/bill/')
def bill():
    c, conn = connection()
    cursor = c.execute('SELECT pname FROM product')
    item = c.fetchall()
    return render_template('bill.html', items= item)

if __name__ == '__main__':
    app.run(debug = True)