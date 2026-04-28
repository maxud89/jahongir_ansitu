from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"


# 🔗 DB
def connect():
    return sqlite3.connect("database.db")


# 🧱 TABLES
def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        category TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        menu_id INTEGER,
        quantity INTEGER,
        portion REAL,
        waiter TEXT,
        table_no TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


# 🍽️ MENU DATA
def seed_data():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM menu")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO menu VALUES (NULL,'Борщ',20,'Первое блюдо')")
        cursor.execute("INSERT INTO menu VALUES (NULL,'Суп куриный',18,'Первое блюдо')")

        cursor.execute("INSERT INTO menu VALUES (NULL,'Плов',30,'Второе блюдо')")
        cursor.execute("INSERT INTO menu VALUES (NULL,'Шашлык',35,'Второе блюдо')")

        cursor.execute("INSERT INTO menu VALUES (NULL,'Цезарь',25,'Салаты')")
        cursor.execute("INSERT INTO menu VALUES (NULL,'Оливье',20,'Салаты')")

        cursor.execute("INSERT INTO menu VALUES (NULL,'Чизкейк',15,'Десерты')")
        cursor.execute("INSERT INTO menu VALUES (NULL,'Мороженое',10,'Десерты')")

        cursor.execute("INSERT INTO menu VALUES (NULL,'Кофе',10,'Напитки')")
        cursor.execute("INSERT INTO menu VALUES (NULL,'Чай',5,'Напитки')")
        cursor.execute("INSERT INTO menu VALUES (NULL,'Сок',12,'Напитки')")

    conn.commit()
    conn.close()


# 👨‍🍳 WAITER
@app.route("/waiter", methods=["GET", "POST"])
def waiter():
    if request.method == "POST":
        session["waiter"] = request.form["name"]
        return redirect("/")
    return render_template("waiter.html")


# 🪑 TABLE
@app.route("/table", methods=["GET", "POST"])
def select_table():
    if request.method == "POST":
        session["table"] = request.form["table"]
        return redirect("/")
    return render_template("table.html")


# 🔄 CHANGE WAITER
@app.route("/change_waiter")
def change_waiter():
    session.pop("waiter", None)
    return redirect("/waiter")

@app.route("/change_table")
def change_table():
    session.pop("table", None)
    session.pop("cart", None)
    return redirect("/table")

# 🌐 MAIN PAGE
@app.route("/")
def index():
    if "waiter" not in session:
        return redirect("/waiter")

    if "table" not in session:
        return redirect("/table")

    conn = connect()
    cursor = conn.cursor()

    items = cursor.execute("SELECT * FROM menu").fetchall()

    # 📦 статусҳо барои официант
    cursor.execute("""
    SELECT menu.name, order_items.status
    FROM order_items
    JOIN menu ON menu.id = order_items.menu_id
    WHERE order_items.table_no=?
    ORDER BY order_items.id DESC
    """, (session["table"],))

    statuses = cursor.fetchall()

    conn.close()

    menu = {}
    for item in items:
        menu.setdefault(item[3], []).append(item)

    cart = session.get("cart", [])
    total_sum = sum(item["total"] for item in cart)

    return render_template(
        "index.html",
        menu=menu,
        waiter=session["waiter"],
        table=session["table"],
        cart=cart,
        total_sum=total_sum,
        statuses=statuses
    )

@app.route("/menu_manage", methods=["GET", "POST"])
def menu_manage():
    if "admin" not in session:
        return redirect("/admin_login")

    conn = connect()
    cursor = conn.cursor()

    # ➕ илова
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        category = request.form["category"]

        cursor.execute(
            "INSERT INTO menu (name, price, category) VALUES (?, ?, ?)",
            (name, price, category)
        )
        conn.commit()

    # 📋 гирифтани меню
    items = cursor.execute("SELECT * FROM menu").fetchall()

    conn.close()

    return render_template("menu_manage.html", items=items)

# 🛒 Нест кардани хурок аз меню
@app.route("/delete_item/<int:id>")
def delete_item(id):
    conn = connect()
    conn.execute("DELETE FROM menu WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/menu_manage")

@app.route("/report")
def report():
    if "admin" not in session:
        return redirect("/admin_login")

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        order_items.waiter,
        SUM(menu.price * order_items.quantity * order_items.portion) as total
    FROM order_items
    JOIN menu ON menu.id = order_items.menu_id
    GROUP BY order_items.waiter
    """)

    data = cursor.fetchall()
    conn.close()

    # ҳисоб 10%
    report_data = []
    for waiter, total in data:
        percent = round(total * 0.10, 2)   # 👈 ИН ҶО МУҲИМ
        total = round(total, 2)

        report_data.append((waiter, total, percent))

# ИВАЗИ НАРХ (UPDATE)
@app.route("/edit_item/<int:id>", methods=["GET", "POST"])
def edit_item(id):
    conn = connect()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]

        cursor.execute(
            "UPDATE menu SET name=?, price=? WHERE id=?",
            (name, price, id)
        )
        conn.commit()
        return redirect("/menu_manage")

    item = cursor.execute("SELECT * FROM menu WHERE id=?", (id,)).fetchone()
    conn.close()

    return render_template("edit_item.html", item=item)

# 🛒 ADD TO CART
@app.route("/order", methods=["POST"])
def order():
    item_id = int(request.form["item_id"])
    quantity = int(request.form["quantity"])
    portion = float(request.form["portion"])

    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT name, price FROM menu WHERE id=?", (item_id,))
    name, price = cur.fetchone()
    conn.close()

    total = price * quantity * portion

    if "cart" not in session:
        session["cart"] = []

    session["cart"].append({
        "name": name,
        "quantity": quantity,
        "portion": portion,
        "total": total
    })

    session.modified = True

    return redirect("/")


# 🧾 CHECKOUT
@app.route("/checkout")
def checkout():
    if "cart" not in session or len(session["cart"]) == 0:
        return redirect("/")

    waiter = session.get("waiter", "Unknown")
    table = session.get("table", "Unknown")

    conn = connect()
    cursor = conn.cursor()

    for item in session["cart"]:
        cursor.execute("SELECT id FROM menu WHERE name=?", (item["name"],))
        result = cursor.fetchone()

        if result:
            menu_id = result[0]

            cursor.execute("""
            INSERT INTO order_items (menu_id, quantity, portion, waiter, table_no, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                menu_id,
                item["quantity"],
                item["portion"],
                waiter,
                table,
                "готовится"
            ))

    conn.commit()
    conn.close()

    session.pop("cart", None)

    return redirect("/")


# 🔄 UPDATE STATUS
@app.route("/update_status/<int:order_id>/<status>")
def update_status(order_id, status):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE order_items SET status=? WHERE id=?",
        (status, order_id)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# 📊 ADMIN LOGIN
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["admin"] = True
            return redirect("/admin")

    return render_template("admin_login.html")


# 🚪 LOGOUT
@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin_login")


# 📊 ADMIN PANEL
@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/admin_login")

    table_filter = request.args.get("table")

    conn = connect()
    cursor = conn.cursor()

    if table_filter:
        cursor.execute("""
        SELECT 
            order_items.id,
            menu.name,
            order_items.quantity,
            order_items.portion,
            order_items.waiter,
            order_items.table_no,
            order_items.status
        FROM order_items
        JOIN menu ON menu.id = order_items.menu_id
        WHERE order_items.table_no=?
        ORDER BY order_items.id DESC
        """, (table_filter,))
    else:
        cursor.execute("""
        SELECT 
            order_items.id,
            menu.name,
            order_items.quantity,
            order_items.portion,
            order_items.waiter,
            order_items.table_no,
            order_items.status
        FROM order_items
        JOIN menu ON menu.id = order_items.menu_id
        ORDER BY order_items.id DESC
        """)

    orders = cursor.fetchall()
    conn.close()

    return render_template("admin.html", orders=orders)


# 🧾 RECEIPT
@app.route("/receipt/<int:order_id>")
def receipt(order_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        menu.name,
        order_items.quantity,
        order_items.portion,
        order_items.waiter,
        order_items.table_no
    FROM order_items
    JOIN menu ON menu.id = order_items.menu_id
    WHERE order_items.id=?
    """, (order_id,))

    order = cursor.fetchone()
    conn.close()

    return render_template("receipt.html", order=order)


# 🗑 CLEAR CART
@app.route("/clear")
def clear_cart():
    session.pop("cart", None)
    return redirect("/")


# 🚀 INIT
create_tables()
seed_data()


if __name__ == "__main__":
    app.run(debug=True)