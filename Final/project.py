import sqlite3
import datetime
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate

# table definitions
def create_tables():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT CHECK(role IN ('user', 'admin'))
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price REAL,
        stock INTEGER
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wishlist (
        user_id INTEGER,
        product_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        products TEXT,
        total_price REAL,
        discount_per INTEGER,
        time TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")

    conn.commit()
    conn.close()

# menu 
def main_menu():
    print("\nWelcome to Inventory Management System")
    print('1. Login')
    print('2. Signup')
    print('3. Exit')
    choice = input("Enter your choice: ")
    if choice == '1':
        login_menu()
    elif choice == '2':
        signup_menu()
    elif choice=='3':
        exit()
    else:
        print("Invalid choice. Please enter a valid option.")
        main_menu()
        
# login
def login_menu():
    print("\nLogin")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    role = input("Enter your role: ")
        
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email=? AND password=? AND role=?",(email,password,role))
    user = cursor.fetchone()
    if user and role=='admin':
        admin_dashboard()
    elif user and role=='user':
        user_dashboard(user[0])
    else:
        print('Invalid credentials')
        login_menu()
    conn.close()
    
# signup 
def signup_menu():
    print("\nSignup")
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    role = input("Enter your role (user/admin): ").lower()

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute('SELECT email FROM users')
    existing_emails = [row[0] for row in cursor.fetchall()]

    if email in existing_emails:
        print('Email already exists.')
        conn.close()
        main_menu()

    if role == "admin":
        if not email.endswith("@inventory.com"):
            print("Only company emails can be used for admin accounts.")
            conn.close()
            main_menu()
        
        secret_key = input("Enter the admin secret key: ")
        if secret_key != "InventoryAdmin123":  
            print("Invalid admin secret key.")
            conn.close()
            main_menu()

    try:
        cursor.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)", 
                       (name, email, password, role))
        conn.commit()
        print("Signup successful!")
        login_menu()
    except:
        print('Could not add user. Try again.')
        main_menu()
    conn.close()
# admin dashboard
def admin_dashboard():
    print("\nWelcome to Admin Dashboard")
    print('1. Manage Products')
    print('2. View Orders')
    print('3. View Analysis')
    print('4. Exit')
    choice = input("Enter your choice: ")
    if choice == '1':
        manage_products()
    elif choice == '2':
        view_orders()
    elif choice == '3':
        view_analysis()
    elif choice == '4':
        main_menu()
    else:
        print("Invalid choice. Please enter a valid option.")
        admin_dashboard()

# admin functions
def manage_products():
    print('\nManage Products')
    print('1. Add Product')
    print('2. Delete Product')
    print('3. Update Product')
    print('4. View Product')
    print('5. Exit')
    choice = input("Enter your choice: ")
    if choice == '1':
        add_product()
    elif choice == '2':
        delete_product()
    elif choice == '3':
        update_product()
    elif choice =='4':
        view_product()
    elif choice == '5':
        admin_dashboard()
    else:
        print("Invalid choice. Please enter a valid option.")
        manage_products()
def add_product():
    print("Adding product\n")
    name = input('Enter product name : ')
    category = input('Enter product category : ')
    price = int(input('Enter product price : '))
    stock = input('Enter product stock : ')
    
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (name,category,price,stock) VALUES (?,?,?,?)",(name,category,price,stock))
    except:
        print('Could not add product')
    conn.commit()
    conn.close()
    manage_products()
def delete_product():
    print('Delete product\n')
    id = int(input('Enter product ID to be deleted : '))
    
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id=?', (id,))
    row = cursor.fetchone()
    if row:
        cursor.execute('DELETE FROM products WHERE id=?', (id,))
        print(f'Product ID {id} deleted successfully.')
    else:
        print('Product not found')
        
    conn.commit()
    conn.close()
    manage_products()
def update_product():
    print('\nUpdate product\n')
    id = int(input('Enter product ID to be updated: '))

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products WHERE id=?', (id,))
    row = cursor.fetchone()
    
    if row:
        current_name, current_category, current_price, current_stock = row[1], row[2], row[3], row[4]
        
        name = input(f'Enter new product name ({current_name}): ') or current_name
        category = input(f'Enter new product category ({current_category}): ') or current_category
        
        price_input = input(f'Enter new product price ({current_price}): ')
        price = int(price_input) if price_input else current_price

        stock_input = input(f'Enter new product stock ({current_stock}): ')
        stock = int(stock_input) if stock_input else current_stock

        cursor.execute('UPDATE products SET name=?, category=?, price=?, stock=? WHERE id=?',(name, category, price, stock, id))
        conn.commit()
        print(f'Product ID {id} updated successfully.')
    else:
        print('Product not found.')

    conn.close()
    manage_products()

def view_product():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products')
    rows = cursor.fetchall()
    
    if not rows:
        print("\nNo Products Available")
    else:
        headers = ["Product ID", "Name", "Category", "Price (₹)", "Stock"]
        table = tabulate(rows, headers=headers, tablefmt="fancy_grid")
        print("\nProduct List:\n")
        print(table)
    conn.close()
    manage_products() 

def view_orders():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders')
    rows = cursor.fetchall()

    if not rows:
        print("\nNo orders found.")
    else:
        headers = ["Order ID", "User ID", "Products", "Total Price (₹)", "Discount (%)", "Time"]
        table = tabulate(rows, headers=headers, tablefmt="fancy_grid") 
        print("\nOrder List:\n")
        print(table)
    conn.close()
    admin_dashboard()

def view_analysis():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    while True:
        print("\nInventory Analysis Menu")
        print("1. Revenue Analysis (Weekly & Monthly)")
        print("2. Top 5 Most Bought Products")
        print("3. Low Stock Products")
        print("4. Most Active Order Hours")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            show_revenue_analysis(cursor)
        elif choice == '2':
            show_top_products(cursor)
        elif choice == '3':
            show_low_stock(cursor)
        elif choice == '4':
            show_peak_hours(cursor)
        elif choice == '5':
            conn.close()
            admin_dashboard()
            return
        else:
            print("Invalid choice. Please enter a valid option.")
            admin_dashboard()

def show_revenue_analysis(cursor):
    cursor.execute("SELECT total_price, time FROM orders")
    orders = cursor.fetchall()

    weekly_revenue = {}
    monthly_revenue = {}

    for total_price, time in orders:
        order_date = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        week = order_date.strftime("%Y-W%W")
        month = order_date.strftime("%Y-%m")

        weekly_revenue[week] = weekly_revenue.get(week, 0) + total_price
        monthly_revenue[month] = monthly_revenue.get(month, 0) + total_price

    weeks = sorted(weekly_revenue.keys())
    months = sorted(monthly_revenue.keys())

    plt.figure(figsize=(8, 5))
    plt.bar(weeks, [weekly_revenue[w] for w in weeks], color='b', alpha=0.6, label="Weekly Revenue")
    plt.bar(months, [monthly_revenue[m] for m in months], color='g', alpha=0.6, label="Monthly Revenue")
    plt.title("Revenue Analysis")
    plt.xticks(rotation=45)
    plt.xlabel("Time Period")
    plt.ylabel("Revenue (₹)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.show()

def show_top_products(cursor):
    cursor.execute("SELECT products FROM orders")
    product_orders = cursor.fetchall()

    product_count = {}
    for order in product_orders:
        products = order[0].split(", ")
        for product in products:
            name = product.split(" (x")[0]
            product_count[name] = product_count.get(name, 0) + 1

    top_products = sorted(product_count.items(), key=lambda x: x[1], reverse=True)[:5]
    product_names, order_counts = zip(*top_products) if top_products else ([], [])

    plt.figure(figsize=(7, 5))
    plt.bar(product_names, order_counts, color="orange")
    plt.title("Top 5 Most Bought Products")
    plt.xticks(rotation=30)
    plt.ylabel("Orders Count")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.show()

def show_low_stock(cursor):
    cursor.execute("SELECT name, stock FROM products ORDER BY stock ASC LIMIT 5")
    low_stock = cursor.fetchall()

    product_names, stock_counts = zip(*low_stock) if low_stock else ([], [])

    plt.figure(figsize=(7, 5))
    plt.bar(product_names, stock_counts, color="red")
    plt.title("Low Stock Products")
    plt.xticks(rotation=30)
    plt.ylabel("Stock Remaining")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.show()

def show_peak_hours(cursor):
    cursor.execute("SELECT time FROM orders")
    order_times = cursor.fetchall()

    hours = [datetime.datetime.strptime(t[0], "%Y-%m-%d %H:%M:%S").hour for t in order_times]
    hour_ranges = ["0-4 AM", "5-8 AM", "9-12 PM", "1-4 PM", "5-8 PM", "9-12 AM"]
    hour_bins = [0, 5, 9, 13, 17, 21, 24]
    hist, _ = np.histogram(hours, bins=hour_bins)

    plt.figure(figsize=(7, 5))
    plt.bar(hour_ranges, hist, color="purple", alpha=0.7, edgecolor="black")
    plt.title("Most Active Order Hours (Grouped)")
    plt.xlabel("Time of Day")
    plt.ylabel("Order Count")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.show()

# user dashboard
def user_dashboard(userid):
    print('\nWelcome to User Dashboard')
    print('1. View Products')
    print('2. Wishlist')
    print('3. Add to Cart')
    print('4. Remove From Cart')
    print('5. View Cart')
    print('6. Check Out')
    print('7. Exit')
    choice = input("Enter your choice: ")
    if choice == '1':
        view_products(userid)
    elif choice == '2':
        wishlist(userid)
    elif choice == '3':
        add_to_cart(userid)
    elif choice == '4':
       remove_from_cart(userid)
    elif choice == '5':
        view_cart(userid)
    elif choice == '6':
        check_out(userid)
    elif choice == '7':
        main_menu()
    else:
        print("Invalid choice. Please enter a valid option.")
        user_dashboard()
        
# user functions
def view_products(userid):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products')
    rows = cursor.fetchall()
    
    if not rows:
        print("\nNo Products Available")
    else:
        headers = ["Product ID", "Name", "Category", "Price (₹)", "Stock"]
        table = tabulate(rows, headers=headers, tablefmt="fancy_grid")
        print("\nProduct List:\n")
        print(table)
    conn.close()
    user_dashboard(userid) 

def wishlist(userid):
    print('\nWishlist')
    print('1. Add product')
    print('2. Remove product')
    print('3. View wishlist')
    print('4. Exit')
    choice = int(input('Enter your choice : '))
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    if choice == 1:
        print('\nAdding Product')
        id = int(input('Enter product ID: '))

        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()

        # Check if product exists in products table
        cursor.execute('SELECT * FROM products WHERE id=?', (id,))
        row = cursor.fetchone()

        if not row:
            print('Product not found.')
            conn.close()
            return wishlist(userid)

        cursor.execute('SELECT 1 FROM wishlist WHERE user_id=? AND product_id=?', (userid, id))
        exists = cursor.fetchone()

        if exists:
            print("Product is already in your wishlist.")
        else:
            cursor.execute('INSERT INTO wishlist (user_id, product_id) VALUES (?, ?)', (userid, id))
            conn.commit()
            print("Product added to wishlist.")

        conn.close()
        wishlist(userid)
    elif choice == 2:
        print('\nRemoving Product')
        id = int(input('Enter product ID: '))
        cursor.execute('DELETE FROM wishlist WHERE user_id=? AND product_id=?', (userid, id))
        conn.commit()
        print("Product removed from wishlist.")
        wishlist(userid)
    elif choice == 3:
        cursor.execute('''
            SELECT p.id, p.name, p.category, p.price 
            FROM wishlist w
            JOIN products p ON w.product_id = p.id
            WHERE w.user_id = ?
        ''', (userid,))
        rows = cursor.fetchall()

        if rows:
            print("\nYour Wishlist:")
            for row in rows:
                print(f'Product ID: {row[0]}, Name: {row[1]}, Category: {row[2]}, Price: ₹{row[3]}')
        else:
            print("Your wishlist is empty.")
        wishlist(userid)
    elif choice == 4: 
        user_dashboard(userid)
    else:
        print("Invalid choice. Please enter a valid option.")
        wishlist(userid)

    conn.close()
    
def add_to_cart(userid):
    print('\nAdding Product to Cart')
    id = int(input("Enter product ID: "))
    quantity = int(input("Enter quantity: "))

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    # Check if product exists in inventory
    cursor.execute("SELECT stock FROM products WHERE id=?", (id,))
    row = cursor.fetchone()

    if not row:
        print("Product not found.")
        conn.close()
        user_dashboard(userid)
        return

    stock = row[0]  # Available stock

    # Check if the product is already in the cart
    cursor.execute("SELECT quantity FROM cart WHERE user_id=? AND product_id=?", (userid, id))
    cart_row = cursor.fetchone()

    if cart_row:  # If product is already in the cart
        new_quantity = cart_row[0] + quantity  # Increase quantity
        if new_quantity > stock:
            print(f"Only {stock} units available. Cannot add more than that.")
        else:
            cursor.execute("UPDATE cart SET quantity=? WHERE user_id=? AND product_id=?", 
                           (new_quantity, userid, id))
            print(f"Updated cart: {new_quantity} units of Product ID {id}.")
    else:  # If product is not in the cart, insert new entry
        if quantity > stock:
            print(f"Only {stock} units available. Cannot add more than that.")
        else:
            cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)", 
                           (userid, id, quantity))
            print(f"Added {quantity} units of Product ID {id} to cart.")

    conn.commit()
    conn.close()
    user_dashboard(userid)  # Return to dashboard

def remove_from_cart(userid):
    print('\nRemoving Product from Cart')
    id = int(input('Enter product ID to remove: '))

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cart WHERE user_id=? AND product_id=?', (userid, id))
    row = cursor.fetchone()

    if row:
        cursor.execute('DELETE FROM cart WHERE user_id=? AND product_id=?', (userid, id))
        conn.commit()
        print(f'Product ID {id} removed from cart successfully.')
    else:
        print('Product not found in cart.')

    conn.close()
    view_cart(userid) 
def view_cart(userid):
    print("\nYour Cart")
    conn=sqlite3.connect('inventory.db')
    cursor=conn.cursor()
    cursor.execute("""
        SELECT p.id, p.name, p.category, p.price, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    """, (userid,))

    rows = cursor.fetchall()

    if rows:
        for row in rows:
            print(f"Product ID: {row[0]}, Name: {row[1]}, Price: ₹{row[3]}, Quantity: {row[4]}")
        recommend_products(userid)
    else:
        print("Your cart is empty.")
    conn.close()
    user_dashboard(userid)
def check_out(userid):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, p.name, p.category, p.price, c.quantity
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    """, (userid,))
    
    cart_items = cursor.fetchall()

    if not cart_items:
        print("\nYour cart is empty. Add items before checking out.")
        conn.close()
        return
    total_price = sum(row[3] * row[4] for row in cart_items)
    # Inside your checkout function
    discount_per = 15
    discount_amount = (discount_per / 100) * total_price
    # Apply conditional discount
    if total_price < 500:
        discount_per = 0 
    elif 500 <= total_price < 1000:
        discount_per = 5 
    elif 1000 <= total_price < 2000:
        discount_per = 10 
    else:
        discount_per = 15
    discount_amount = (discount_per / 100) * total_price
    final_price = total_price - discount_amount
    products_str = ', '.join([f"{row[1]} (x{row[4]})" for row in cart_items])
    order_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Display the bill
    print("\n===== BILL =====")
    for item in cart_items:
        print(f"Product: {item[1]}, Quantity: {item[4]}, Price: ₹{item[3] * item[4]}")
    print(f"Total: ₹{total_price}")
    print(f"Discount ({discount_per}%): -₹{discount_amount}")
    print(f"Final Amount: ₹{final_price}")
    print("================\n")

    # Start transaction
    try:
        cursor.execute("""
            INSERT INTO orders (user_id, products, total_price, discount_per, time)
            VALUES (?, ?, ?, ?, ?)
        """, (userid, products_str, final_price, discount_per, order_time))

        for item in cart_items:
            cursor.execute("""
                UPDATE products SET stock = stock - ? WHERE id = ?
            """, (item[4], item[0])) 

        cursor.execute("""
            DELETE FROM cart WHERE user_id = ?
        """, (userid,))

        conn.commit() 
        print("Checkout successful! Your order has been placed.")

    except Exception as e:
        conn.rollback() 
        print("Error during checkout:", e)

    conn.close()
    user_dashboard(userid)
def recommend_products(user_id):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT product_id FROM cart WHERE user_id=?", (user_id,))
    cart_products = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT products FROM orders WHERE user_id=?", (user_id,))
    past_products = []
    for order in cursor.fetchall():
        past_products += order[0].split(", ")

    cursor.execute("SELECT products FROM orders")
    all_orders = [row[0] for row in cursor.fetchall()]

    recommended = set()
    for order in all_orders:
        products = order.split(", ")
        for product in products:
            if product in cart_products or product in past_products:
                recommended.update(products) 

    recommended.difference_update(cart_products) 
    recommended.difference_update(past_products)

    if recommended:
        placeholders = ', '.join(['?'] * len(recommended))
        cursor.execute(f"SELECT id, name FROM products WHERE name IN ({placeholders})", tuple(recommended))
        results = cursor.fetchall()
    else:
        results = []

    conn.close()

    if results:
        print("\nRecommended Products for You:")
        for prod_id, name in results[:5]:
            print(f"{name} (Product ID: {prod_id})")
    else:
        print("\nNo recommendations available.")
        
create_tables()
main_menu()