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

         data = c.execute("SELECT * FROM users WHERE username = (%s)",
                              request.form['username'])
         data = c.fetchone()

         if attempted_username == "admin" and attempted_password == "admin":
             return render_template('home.html')

         elif attempted_username == data[0] and attempted_password == data[1]:
             return render_template('home.html')
         else:
             error="Invalid Credentials , try again."
      gc.collect()
      return render_template('login.html',error =error)
    except Exception as e:
        # flash(e)
        error = "Invalid credentials, try again."
        return render_template("login.html", error=error)


if __name__ == '__main__':
    app.run(debug = True)