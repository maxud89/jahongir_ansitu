# 🍽️ Food Ordering System (Анситу)

## 📌 Overview

This is a web-based food ordering system developed for a café environment.
It allows waiters to take orders via tablet/mobile and administrators to manage orders, menu, and reports.

---

## 🚀 Features

### 👨‍🍳 Waiter Panel

* Enter waiter name
* Select table
* Choose food from menu
* Select portion and quantity
* Add to cart
* Submit order
* View order status (готовится / готово)

### 📊 Admin Panel

* View all orders
* Update order status
* Filter by table
* Print receipt
* Manage menu:

  * Add item
  * Edit item
  * Delete item

### 📈 Reports

* Total income per waiter
* 10% service commission calculation

---

## ⚙️ Technologies

* Python 3.11
* Flask
* SQLite
* HTML / CSS

---

## 📁 Project Structure

```
project/
│
├── app.py
├── database.db
│
├── templates/
│   ├── index.html
│   ├── admin.html
│   ├── menu_manage.html
│   ├── report.html
│   ├── waiter.html
│   ├── table.html
│   ├── edit_item.html
│
├── static/
│   └── style.css
```

---

## ▶️ Run Project

### 1. Install dependencies

```
pip install flask
```

### 2. Run application

```
python app.py
```

### 3. Open in browser

```
http://127.0.0.1:5000
```

---

## 🔐 Admin Access

```
Username: admin
Password: 1234
```

---

## 💡 Notes

* Orders are stored in SQLite database
* Order status updates in real-time (page refresh)
* Floating values are rounded to 2 decimal places

---

## 🔮 Future Improvements

* Charts & analytics
* Date-based filtering
* Notifications
* Payment integration
* Mobile app version

---
## teken GitHub


## 👨‍💻 Author

Musoev Jahongir – 2026
# jahongir_ansitu
