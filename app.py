from flask import Flask, render_template, request, redirect
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "liquor_2.db")

# -------------------------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------
def init_db():
    conn = get_db()

    # ===== TABLE 1: CATEGORIES =====
    conn.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)

    # ===== TABLE 2: SUPPLIERS =====
    conn.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL,
        contact TEXT
    )
    """)

    # ===== TABLE 3: LIQUORS (with FK to categories and suppliers) =====
    conn.execute("""
    CREATE TABLE IF NOT EXISTS liquors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL,
        image TEXT,
        stock INTEGER,
        category_id INTEGER,
        supplier_id INTEGER,
        alcohol_content REAL,
        volume INTEGER,
        FOREIGN KEY(category_id) REFERENCES categories(id),
        FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
    )
    """)

    # ===== TABLE 4: CUSTOMERS =====
    conn.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        phone TEXT,
        points INTEGER DEFAULT 0
    )
    """)

    # ===== TABLE 5: ORDERS =====
    conn.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        liquor_id INTEGER NOT NULL,
        customer_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total_price REAL,
        order_date TEXT,
        FOREIGN KEY(liquor_id) REFERENCES liquors(id),
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    )
    """)

    conn.commit()

    # ===== MOCK DATA =====
    # Check if categories already exist
    categories_count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    
    if categories_count == 0:
        # Insert 10+ Categories
        categories = [
            "Whiskey",
            "Wine",
            "Gin",
            "Vodka",
            "Craft Beer",
            "Rum",
            "Tequila",
            "Brandy",
            "Sake",
            "Liqueur"
        ]
        for cat in categories:
            try:
                conn.execute("INSERT INTO categories (name) VALUES (?)", (cat,))
            except:
                pass

        # Insert 10+ Suppliers
        suppliers = [
            ("Jack Daniel's Distillery", "+1-931-759-6357"),
            ("Diageo Global", "+44-131-519-4000"),
            ("Pernod Ricard", "+33-1-41-00-45-00"),
            ("Beam Suntory", "+1-502-774-4200"),
            ("Brown-Forman", "+1-502-585-1100"),
            ("Bacardi Company", "+1-305-573-7500"),
            ("Rémy Cointreau", "+33-1-44-27-11-00"),
            ("Thai Beverage", "+66-2-718-5000"),
            ("Edrington Group", "+44-141-887-0700"),
            ("Allied Blenders & Distillers", "+91-11-4068-6000")
        ]
        for sup_name, contact in suppliers:
            try:
                conn.execute("INSERT INTO suppliers (supplier_name, contact) VALUES (?, ?)", (sup_name, contact))
            except:
                pass

        # Insert 15+ Liquors with Category_id and Supplier_id
        liquors = [
            ("Jack Daniel's Old No. 7", 2500.00, "https://images.unsplash.com/photo-1528823872057-7c5d6c5245b3?w=400", 50, 1, 1, 40.0, 750),
            ("Chateau Margaux 2015", 15000.00, "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=400", 10, 2, 2, 13.5, 750),
            ("Hendrick's Gin", 3200.00, "https://images.unsplash.com/photo-1607622750671-6cd9a99eabd1?w=400", 30, 3, 3, 41.4, 700),
            ("Absolut Vodka", 1800.00, "https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=400", 40, 4, 4, 40.0, 750),
            ("Sierra Nevada Pale Ale", 250.00, "https://images.unsplash.com/photo-1608270586620-248524c67de9?w=400", 100, 5, 5, 5.6, 355),
            ("Bacardi Superior Rum", 1950.00, "https://images.unsplash.com/photo-1559056169-641ef0ac8b55?w=400", 45, 6, 6, 37.5, 750),
            ("Patrón Silver Tequila", 2100.00, "https://images.unsplash.com/photo-1608652245592-1d55a1da9f8c?w=400", 35, 7, 7, 40.0, 750),
            ("Cognac XO", 8500.00, "https://images.unsplash.com/photo-1547936537-96c7b93f11ab?w=400", 20, 8, 8, 40.0, 700),
            ("Sake Premium", 3000.00, "https://images.unsplash.com/photo-1594788318286-3d835c1cab83?w=400", 25, 9, 9, 15.6, 720),
            ("Baileys Irish Cream", 1500.00, "https://images.unsplash.com/photo-1557751608-c0f7b81d5ffd?w=400", 60, 10, 10, 17.0, 750),
            ("Johnnie Walker Blue", 4500.00, "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400", 15, 1, 2, 40.0, 750),
            ("Dom Pérignon Champagne", 12000.00, "https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=400", 8, 2, 2, 12.5, 750),
            ("Tanqueray Gin", 2500.00, "https://images.unsplash.com/photo-1608270586620-248524c67de9?w=400", 40, 3, 2, 47.3, 750),
            ("Grey Goose Vodka", 2800.00, "https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=400", 35, 4, 2, 40.0, 750),
            ("Guinness Draught", 180.00, "https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=400", 150, 5, 5, 4.2, 440)
        ]
        for liq in liquors:
            try:
                conn.execute("""
                INSERT INTO liquors (name, price, image, stock, category_id, supplier_id, alcohol_content, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, liq)
            except:
                pass

        # Insert 12+ Customers
        customers = [
            ("นาย สมชาย ผลดี", "0812345678", 150),
            ("นาย วิชัย สุขสำราญ", "0823456789", 200),
            ("นาง สุจิตรา กวินพันธ์", "0834567890", 100),
            ("นาย ธนพล อดทนพร", "0845678901", 175),
            ("นาย กิตติ ชื่นชมชัย", "0856789012", 220),
            ("นาง วรนา อัศวินวร", "0867890123", 90),
            ("นาย สมเกียรติ สิรินธร", "0878901234", 310),
            ("นาย ประเสริฐ บุญชัย", "0889012345", 140),
            ("นาง นำนิตา เนียมสมชาย", "0890123456", 260),
            ("นาย เดชา มงคลธรรม", "0801234567", 185),
            ("นาย อนุชา พรหมศิริ", "0811234567", 210),
            ("นาง ชลลดา รัตนศิริ", "0822234567", 105)
        ]
        for cust in customers:
            try:
                conn.execute("""
                INSERT INTO customers (customer_name, phone, points)
                VALUES (?, ?, ?)
                """, cust)
            except:
                pass

        # Insert 15+ Orders
        base_date = datetime.now()
        orders = [
            (1, 1, 2, 5000.00, (base_date - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")),
            (2, 2, 1, 15000.00, (base_date - timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S")),
            (3, 3, 3, 9600.00, (base_date - timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S")),
            (4, 4, 5, 9000.00, (base_date - timedelta(days=18)).strftime("%Y-%m-%d %H:%M:%S")),
            (5, 5, 4, 1000.00, (base_date - timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S")),
            (6, 6, 2, 3900.00, (base_date - timedelta(days=12)).strftime("%Y-%m-%d %H:%M:%S")),
            (7, 7, 1, 2100.00, (base_date - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")),
            (8, 8, 2, 17000.00, (base_date - timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S")),
            (9, 9, 1, 3000.00, (base_date - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")),
            (10, 10, 3, 4500.00, (base_date - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")),
            (11, 11, 2, 9000.00, (base_date - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")),
            (1, 12, 1, 2500.00, (base_date - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")),
            (3, 1, 2, 6400.00, (base_date - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")),
            (5, 2, 5, 1250.00, (base_date - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
            (15, 3, 6, 1080.00, base_date.strftime("%Y-%m-%d %H:%M:%S"))
        ]
        for order in orders:
            try:
                conn.execute("""
                INSERT INTO orders (liquor_id, customer_id, quantity, total_price, order_date)
                VALUES (?, ?, ?, ?, ?)
                """, order)
            except:
                pass

    conn.commit()
    conn.close()

init_db()

# -------------------------
@app.route("/")
def index():
    conn = get_db()
    liquors = conn.execute("""
        SELECT 
            liquors.*,
            categories.name as category_name,
            suppliers.supplier_name,
            suppliers.contact as supplier_contact
        FROM liquors
        LEFT JOIN categories ON liquors.category_id = categories.id
        LEFT JOIN suppliers ON liquors.supplier_id = suppliers.id
        ORDER BY liquors.id DESC
    """).fetchall()
    conn.close()
    return render_template("cakemenu.html", liquors=liquors)

# -------------------------
@app.route("/append", methods=["GET", "POST"])
def append():
    conn = get_db()
    categories = conn.execute("SELECT * FROM categories").fetchall()
    suppliers = conn.execute("SELECT * FROM suppliers").fetchall()

    if request.method == "POST":
        name = request.form["name"]
        image = request.form["image"]

        try:
            price = float(request.form["price"])
            stock = int(request.form["stock"])
            alcohol = float(request.form["alcohol"])
            volume = int(request.form["volume"])
        except:
            return "❌ กรอกข้อมูลตัวเลขผิด"

        category_id = request.form.get("category")
        supplier_id = request.form.get("supplier")

        conn.execute("""
        INSERT INTO liquors
        (name, price, image, stock, category_id, supplier_id, alcohol_content, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, price, image, stock, category_id, supplier_id, alcohol, volume))

        conn.commit()
        conn.close()
        return redirect("/")

    conn.close()
    return render_template("append.html", categories=categories, suppliers=suppliers, liquor=None)

# -------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    categories = conn.execute("SELECT * FROM categories").fetchall()
    suppliers = conn.execute("SELECT * FROM suppliers").fetchall()

    if request.method == "POST":
        try:
            price = float(request.form["price"])
            stock = int(request.form["stock"])
            alcohol = float(request.form["alcohol"])
            volume = int(request.form["volume"])
        except:
            return "❌ กรอกข้อมูลผิด"

        conn.execute("""
        UPDATE liquors SET
        name=?, price=?, image=?, stock=?, category_id=?, supplier_id=?, alcohol_content=?, volume=?
        WHERE id=?
        """, (
            request.form["name"],
            price,
            request.form["image"],
            stock,
            request.form["category"],
            request.form["supplier"],
            alcohol,
            volume,
            id
        ))

        conn.commit()
        conn.close()
        return redirect("/")

    liquor = conn.execute("SELECT * FROM liquors WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit.html", liquor=liquor, categories=categories, suppliers=suppliers)

# -------------------------
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM liquors WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

# -------------------------
if __name__ == "__main__":
    app.run(debug=True)