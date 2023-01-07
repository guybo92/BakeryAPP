from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from flask_migrate import Migrate

# Customer and Product list from DB - into a dictionary
customer = ["קפה קפה", "לחמים", "המשפחה"]
product = []
first_connect = psycopg2.connect(host='localhost', database='bakery', user='postgres', password='123', port='5432')
cursor = first_connect.cursor()
cursor.execute('SELECT item FROM product order by id')
items = cursor.fetchall()
for row in items:
    product.append(row[0])
product = dict.fromkeys(product, 0)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/postgres'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.secret_key = 'holly molly'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# First page - Login (with validity of user name and password)
@app.route('/', methods=['POST', 'GET'])
def main():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        if user_name != "nitzan" or password != "123":
            flash("User name or Password is incorrect")
            print("wrong")
            return render_template("Login.html")
        print("Login successfully")
        session['logged_in'] = True
        return redirect("/welcome")
    return render_template("Login.html")


# first page - welcome
@app.route('/welcome', methods=['POST', 'GET'])
def welcome_page():
    return render_template("main-page.html")


# Make order (Table with quantity)
@app.route('/neworder', methods=['GET', 'POST'])
def new_order():  # form
    global customer, product, items
    check = 0
    conn = psycopg2.connect(host='localhost', database='bakery', user='postgres', password='123', port='5432')
    cur = conn.cursor()
    cur.execute('SELECT MAX(ID) FROM orders')
    max_id = cur.fetchall()[0][0] + 1
    cur.execute("select id, item, to_char(price, 'L99D99') from product order by id;")
    product_list = cur.fetchall()
    key_list = list(product.keys())
    if request.method == "POST":
        selected_customer = request.form.get("customer")
        order_date = request.form.get("book_date")
        for i in range(len(items)):
            if request.form.get(str(key_list[i])) != "":
                check += 1
                product[(key_list[i])] = request.form.get(str(key_list[i]))
        # print(selected_customer + "\n" + str(product) + "\n" + order_date)
        add_to_db = "INSERT INTO orders VALUES(%s, %s, %s"
        for i in range(0, len(items)):
            add_to_db += ', %s'
        add_to_db += ")"
        insert_var = "max_id , selected_customer, order_date"
        for i in range(len(items)):
            insert_var += ", product[str(key_list[" + str(i) + "])]"
        if check > 0:
            print(add_to_db, eval(insert_var))
            cur.execute(add_to_db, eval(insert_var))
            conn.commit()
            conn.close()
            add_to_db = ''
            insert_var = ''
            return render_template("summary.html")
    return render_template("New-Order.html", customer=customer, product_list=product_list)


# summary page - "order successfully"
@app.route('/summary', methods=['POST', 'GET'])
def form():
    return render_template("summary.html")


# Manage order page - Table with all previous orders
@app.route("/manageorder", methods=['GET', 'POST'])
def manage():
    global customer
    conn = psycopg2.connect(host='localhost', database='bakery', user='postgres', password='123', port='5432')
    cur = conn.cursor()
    cur.execute("select * from orders")
    all_orders = cur.fetchall()
    conn.commit()
    cur.execute("select price from product order by id")
    price = cur.fetchall()
    # print("All orders\n", all_orders)
    manage_table_result = "select id, client, date, to_char(p1*" + str(price[0][0])
    for i in range(2, len(items) + 1):
        manage_table_result += " +p" + str(i) + "*" + str(price[i - 1][0])
    manage_table_result += ", '₪FM99G999D0') AS total from orders order by date desc"
    print(manage_table_result)
    cur.execute(manage_table_result)
    manage_viewer = cur.fetchall()
    print(manage_viewer)
    conn.commit()
    conn.close()
    return render_template("manage.html", manage_viewer=manage_viewer, customer=customer)


# delete from db per row
@app.route('/delete_order/<string:id>', methods=['GET', 'POST'])
def delete_order(id):
    conn = psycopg2.connect(host='localhost', database='bakery', user='postgres', password='123', port='5432')
    cur = conn.cursor()
    cur.execute("DELETE FROM orders WHERE id = %s", [id])
    conn.commit()
    conn.close()
    flash("Deleted")
    return redirect(url_for('manage'))


# Invoices page
@app.route('/invoice', methods=['POST', 'GET'])
def invoices():
    return render_template("invoices.html")


# update employee
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    print("hi")
    conn = psycopg2.connect(host='localhost', database='bakery', user='postgres', password='123', port='5432')
    cur = conn.cursor()
    cur.execute("SELECT * from orders WHERE id = %s", [id])
    data = cur.fetchall()
    conn.commit()
    conn.close()
    print(data)
    if request.method == 'POST':
        flash("Employee Updated Successfully")
        return redirect(url_for('Index'))

    return render_template('edit.html', data=data, customer=customer)


if __name__ == '__main__':
    app.run(debug=True, port=8080, host="0.0.0.0")

# cur.execute(add_to_db, (max_id + 1, selected_customer, order_date, product[str(key_list[0])],
#                         product[str(key_list[1])], product[str(key_list[2])], product[str(key_list[3])],
#                         product[str(key_list[4])], product[str(key_list[5])], product[str(key_list[6])]))


#  https://tutorial101.blogspot.com/2020/02/python-flask-datatable-using-sqlalchemy.html - edit
# https://www.youtube.com/watch?v=I0Zu-Jtp898&t=302s - edit

# https://www.youtube.com/watch?v=z3109C_xDP8&t=824s - edit good guide

# check again maybe..https://www.youtube.com/watch?v=galc9j2Q4FA&t=243s
