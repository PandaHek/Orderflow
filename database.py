import sqlite3
import uuid

DB = "orderflow.db"

def get_connection():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn



def create_tables():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS customers(
            CUSTOMER_ID   VARCHAR PRIMARY KEY,
            NAME          VARCHAR NOT NULL,
            EMAIL         VARCHAR NOT NULL,
            PHONE         INT NOT NULL
            );


        CREATE TABLE IF NOT EXISTS address(
            ADDRESS_ID   VARCHAR PRIMARY KEY,
            CUSTOMER_ID  VARCHAR NOT NULL,
            STREET       VARCHAR NOT NULL,
            CITY         VARCHAR NOT NULL,
            STATE        VARCHAR NOT NULL,
            PINCODE      INT NOT NULL, 
            COUNTRY      VARCHAR NOT NULL,
            FOREIGN KEY (CUSTOMER_ID) REFERENCES customers(CUSTOMER_ID)
            );
                 
        CREATE TABLE IF NOT EXISTS products(
            SKU         INT PRIMARY KEY,
            NAME        VARCHAR NOT NULL,
            CATEGORY    VARCHAR NOT NULL,
            PRICE       FLOAT NOT NULL,
            STOCK       INT NOT NULL,
            IMAGE_PATH  VARCHAR
            );
                 
        CREATE TABLE IF NOT EXISTS orders(
            ORDER_ID    VARCHAR PRIMARY KEY,
            CUSTOMER_ID VARCHAR NOT NULL,
            ADDRESS_ID  VARCHAR NOT NULL,
            STATUS      VARCHAR NOT NULL,
            TOTAL_PRICE    FLOAT NOT NULL,
            ORDER_DATE  DATE NOT NULL,
            FOREIGN KEY (CUSTOMER_ID) REFERENCES customers(CUSTOMER_ID),
            FOREIGN KEY (ADDRESS_ID) REFERENCES address(ADDRESS_ID)
            );

        CREATE TABLE IF NOT EXISTS order_items(
            ITEM_ID  VARCHAR PRIMARY KEY,
            ORDER_ID       VARCHAR NOT NULL,
            SKU            INT NOT NULL,
            QUANTITY       INT NOT NULL,
            UNIT_PRICE     FLOAT NOT NULL,
            SUBTOTAL       FLOAT NOT NULL,
            FOREIGN KEY (ORDER_ID) REFERENCES orders(ORDER_ID),
            FOREIGN KEY (SKU) REFERENCES products(SKU)
            );
        
        CREATE TRIGGER IF NOT EXISTS reduce_stock_after_order
        AFTER INSERT ON order_items
        FOR EACH ROW
        BEGIN
            UPDATE products
            SET STOCK = STOCK - NEW.QUANTITY
            WHERE SKU = NEW.SKU;
        END;


    """)
    conn.close()


if __name__ == "__main__":
    create_tables()
    print("Tables created successfully.")


#CUSTOMERS OPERATIONS


def add_customer(name, email, phone, street, city, state, pincode, country):
    customer_id = str(uuid.uuid4())[:4]
    address_id  = str(uuid.uuid4())[:4]

    conn = get_connection()
    conn.execute("""
        INSERT INTO customers (CUSTOMER_ID, NAME, EMAIL, PHONE)
        VALUES (?, ?, ?, ?)
    """, (customer_id, name, email, phone))

    conn.execute("""
        INSERT INTO address (ADDRESS_ID, CUSTOMER_ID, STREET, CITY, STATE, PINCODE, COUNTRY)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (address_id, customer_id, street, city, state, pincode, country))

    conn.commit()
    conn.close()
    print(f"Customer added successfully! ID: {customer_id}")




def get_all_customers():
    conn = get_connection()
    cursor = conn.execute("""
        SELECT c.CUSTOMER_ID, c.NAME, c.EMAIL, c.PHONE, a.STREET, a.CITY, a.STATE, a.PINCODE, a.COUNTRY, a.ADDRESS_ID
        FROM customers c JOIN address a
        ON c.CUSTOMER_ID = a.CUSTOMER_ID
    """)
    customers = cursor.fetchall()
    conn.close()
    return customers


def get_address_id(customer_id):
    conn = get_connection()
    cursor = conn.execute("""
        SELECT ADDRESS_ID FROM address WHERE CUSTOMER_ID = ?
    """, (customer_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None



def update_customer(customer_id, phone, street, city, state, pincode, country):
    conn = get_connection()
    conn.execute("""
        UPDATE customers SET PHONE = ? WHERE CUSTOMER_ID = ?
    """, (phone, customer_id))
    conn.execute("""
        UPDATE address SET STREET = ?, CITY = ?, STATE = ?, PINCODE = ?, COUNTRY = ?
        WHERE CUSTOMER_ID = ?
    """, (street, city, state, pincode, country, customer_id))
    conn.commit()
    conn.close()



def search_customer(keyword, filter_by):
    conn = get_connection()

    if filter_by == "name":
        cursor = conn.execute("""
            SELECT c.CUSTOMER_ID, c.NAME, c.EMAIL, c.PHONE, a.STREET, a.CITY, a.STATE, a.PINCODE, a.COUNTRY, a.ADDRESS_ID
            FROM customers c JOIN address a
            ON c.CUSTOMER_ID = a.CUSTOMER_ID
            WHERE c.NAME LIKE ?
        """, (f"%{keyword}%",))

    elif filter_by == "customer_id":
        cursor = conn.execute("""
            SELECT c.CUSTOMER_ID, c.NAME, c.EMAIL, c.PHONE, a.STREET, a.CITY, a.STATE, a.PINCODE, a.COUNTRY, a.ADDRESS_ID
            FROM customers c JOIN address a
            ON c.CUSTOMER_ID = a.CUSTOMER_ID
            WHERE c.CUSTOMER_ID = ?
        """, (keyword,))

    customers = cursor.fetchall()
    conn.close()
    return customers




#PRODUCTS OPERATIONS

def add_product(sku, name, category, price, stock, image_path=None):
    conn = get_connection()
    conn.execute("""
        INSERT INTO products (SKU, NAME, CATEGORY, PRICE, STOCK, IMAGE_PATH)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (sku, name, category, price, stock, image_path))
    conn.commit()
    conn.close()
    print(f"Product added successfully! SKU: {sku}")



def get_all_products():
    conn = get_connection()
    cursor = conn.execute("""SELECT SKU, NAME, CATEGORY, PRICE, STOCK, IMAGE_PATH FROM products""")
    products = cursor.fetchall()
    conn.close()
    return products




def update_product_image(sku, image_path):
    conn = get_connection()
    conn.execute("""
        UPDATE products SET IMAGE_PATH = ? WHERE SKU = ?
    """, (image_path, sku))
    conn.commit()
    conn.close()

def search_product(keyword, filter_by):
    conn = get_connection()
    
    if filter_by == "name":
        cursor = conn.execute("""
            SELECT * FROM products WHERE NAME LIKE ?
        """, (f"%{keyword}%",))
    
    elif filter_by == "category":
        cursor = conn.execute("""
            SELECT * FROM products WHERE CATEGORY LIKE ?
        """, (f"%{keyword}%",))
    
    elif filter_by == "sku":
        cursor = conn.execute("""
            SELECT * FROM products WHERE SKU = ?
        """, (keyword,))
    
    products = cursor.fetchall()
    conn.close()
    return products



# ✅ FIX 1 — Added the missing UPDATE query
def update_product_stock(sku, new_stock):
    conn = get_connection()
    conn.execute("""
        UPDATE products SET STOCK = ? WHERE SKU = ?
    """, (new_stock, sku))
    conn.commit()
    conn.close()
    print(f"Product stock updated successfully! SKU: {sku}, New Stock: {new_stock}")



def update_product_price(sku, new_price):
    conn = get_connection()
    conn.execute("""
        UPDATE products SET PRICE = ? WHERE SKU = ?
    """, (new_price, sku))
    conn.commit()
    conn.close()
    print(f"Product price updated successfully! SKU: {sku}, New Price: {new_price}")


def delete_product(sku):
    conn = get_connection()
    conn.execute("""
        DELETE FROM products WHERE SKU = ?
    """, (sku,))
    conn.commit()
    conn.close()
    print(f"Product deleted successfully! SKU: {sku}")



def delete_customer(customer_id):
    conn = get_connection()
    
    cursor = conn.execute("SELECT COUNT(*) FROM orders WHERE CUSTOMER_ID = ?", (customer_id,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        return False   # has orders, don't delete
    
    conn.execute("DELETE FROM address WHERE CUSTOMER_ID = ?", (customer_id,))
    conn.execute("DELETE FROM customers WHERE CUSTOMER_ID = ?", (customer_id,))
    conn.commit()
    conn.close()
    return True    




def place_order(customer_id, address_id, items):
    conn = get_connection()
    order_id = str(uuid.uuid4())[:4]
    total = 0

    conn.execute("""
        INSERT INTO orders (ORDER_ID, CUSTOMER_ID, ADDRESS_ID, STATUS, TOTAL_PRICE, ORDER_DATE)
        VALUES (?, ?, ?, 'Created', 0, DATE('now'))
    """, (order_id, customer_id, address_id))

    for item in items:
        sku      = item['sku']
        quantity = item['quantity']

        cursor = conn.execute("SELECT PRICE, STOCK FROM products WHERE SKU = ?", (sku,))
        row = cursor.fetchone()

        if row is None:
            print(f"SKU {sku} not found, skipping.")
            continue

        if row[1] < quantity:
            print(f"Not enough stock for SKU {sku} (available: {row[1]}), skipping.")
            continue

        unit_price = row[0]
        subtotal   = unit_price * quantity
        total     += subtotal
        item_id    = str(uuid.uuid4())[:4]

        conn.execute("""
            INSERT INTO order_items (ITEM_ID, ORDER_ID, SKU, QUANTITY, UNIT_PRICE, SUBTOTAL)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item_id, order_id, sku, quantity, unit_price, subtotal))

        # ✅ FIX 2 — Removed manual stock update, trigger handles it now
        # conn.execute("""
        #     UPDATE products SET STOCK = STOCK - ? WHERE SKU = ?
        # """, (quantity, sku))

    conn.execute("""
        UPDATE orders SET TOTAL_PRICE = ? WHERE ORDER_ID = ?
    """, (total, order_id))

    conn.commit()
    conn.close()
    print(f"Order placed! ID: {order_id} | Total: ₹{total}")
    return order_id




def get_all_orders():
    conn = get_connection()
    cursor = conn.execute("""
        SELECT o.ORDER_ID, c.NAME, a.STREET, a.CITY, a.STATE, a.PINCODE, a.COUNTRY, o.STATUS, o.TOTAL_PRICE, o.ORDER_DATE
        FROM orders o JOIN customers c ON o.CUSTOMER_ID = c.CUSTOMER_ID
        JOIN address a ON o.ADDRESS_ID = a.ADDRESS_ID
        ORDER BY o.ORDER_DATE DESC
    """)
    orders = cursor.fetchall()
    conn.close()
    return orders




def search_orders(keyword, filter_by):
    conn = get_connection()

    if filter_by == "order_id":
        cursor = conn.execute("""
            SELECT o.ORDER_ID, c.NAME, a.STREET, a.CITY, a.STATE, a.PINCODE, a.COUNTRY, o.STATUS, o.TOTAL_PRICE, o.ORDER_DATE
            FROM orders o JOIN customers c ON o.CUSTOMER_ID = c.CUSTOMER_ID
            JOIN address a ON o.ADDRESS_ID = a.ADDRESS_ID
            WHERE o.ORDER_ID = ?
        """, (keyword,))
    
    elif filter_by == "customer_name":
        cursor = conn.execute("""
            SELECT o.ORDER_ID, c.NAME, a.STREET, a.CITY, a.STATE, a.PINCODE, a.COUNTRY, o.STATUS, o.TOTAL_PRICE, o.ORDER_DATE
            FROM orders o JOIN customers c ON o.CUSTOMER_ID = c.CUSTOMER_ID
            JOIN address a ON o.ADDRESS_ID = a.ADDRESS_ID
            WHERE c.NAME LIKE ?
        """, (f"%{keyword}%",))

    elif filter_by == "status":
        cursor = conn.execute("""
            SELECT o.ORDER_ID, c.NAME, a.STREET, a.CITY, a.STATE, a.PINCODE, a.COUNTRY, o.STATUS, o.TOTAL_PRICE, o.ORDER_DATE
            FROM orders o JOIN customers c ON o.CUSTOMER_ID = c.CUSTOMER_ID
            JOIN address a ON o.ADDRESS_ID = a.ADDRESS_ID
            WHERE o.STATUS LIKE ?
        """, (f"%{keyword}%",))
    
    elif filter_by == "city":
        cursor = conn.execute("""
            SELECT o.ORDER_ID, c.NAME, a.STREET, a.CITY, a.STATE, a.PINCODE, a.COUNTRY, o.STATUS, o.TOTAL_PRICE, o.ORDER_DATE
            FROM orders o JOIN customers c ON o.CUSTOMER_ID = c.CUSTOMER_ID
            JOIN address a ON o.ADDRESS_ID = a.ADDRESS_ID
            WHERE a.CITY LIKE ?
        """, (f"%{keyword}%",))

    orders = cursor.fetchall()
    conn.close()
    return orders


def get_order_details(order_id):
    conn = get_connection()
    cursor = conn.execute("""
        SELECT oi.SKU, p.NAME, oi.QUANTITY, oi.UNIT_PRICE, oi.SUBTOTAL
        FROM order_items oi JOIN products p ON oi.SKU = p.SKU
        WHERE oi.ORDER_ID = ?
    """, (order_id,))
    items = cursor.fetchall()
    conn.close()
    return items

def update_order_status(order_id, new_status):
    conn = get_connection()
    conn.execute("""
        UPDATE orders SET STATUS = ? WHERE ORDER_ID = ?
    """, (new_status, order_id))
    conn.commit()
    conn.close()
    print(f"Order status updated successfully! ID: {order_id}, New Status: {new_status}")

def total_orders_count():
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM orders")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def total_revenue():
    conn = get_connection()
    cursor = conn.execute("SELECT SUM(TOTAL_PRICE) FROM orders WHERE STATUS = 'Delivered'")
    revenue = cursor.fetchone()[0] or 0
    conn.close()
    return revenue


def total_canceled_orders():
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM orders WHERE STATUS = 'Cancelled'")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def top_selling_products(limit=5):
    conn = get_connection()
    cursor = conn.execute("""
        SELECT p.NAME, SUM(oi.QUANTITY) AS total_sold
        FROM order_items oi JOIN products p ON oi.SKU = p.SKU
        GROUP BY oi.SKU
        ORDER BY total_sold DESC
        LIMIT ?
    """, (limit,))
    products = cursor.fetchall()
    conn.close()
    return products

def orders_by_city():
    conn = get_connection()
    cursor = conn.execute("""
        SELECT a.CITY, COUNT(*) AS order_count
        FROM orders o JOIN address a ON o.ADDRESS_ID = a.ADDRESS_ID
        GROUP BY a.CITY
        ORDER BY order_count DESC
    """)
    city_orders = cursor.fetchall()
    conn.close()
    return city_orders