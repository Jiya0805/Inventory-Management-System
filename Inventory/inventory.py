from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import hashlib
import matplotlib.pyplot as plt
import io
import json

from datetime import datetime, timedelta

# Database setup
Base = declarative_base()
db_url = "sqlite:///ecommerce.db"
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# Password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Define models
class Admin(Base):
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class User(Base):
    __tablename__ = 'user'
    userid = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Product(Base):
    __tablename__ = 'product'
    productid = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    costprice = Column(Float, nullable=False)
    sellingprice = Column(Float, nullable=False)

class Order(Base):
    __tablename__ = 'orders'
    orderid = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(Integer, ForeignKey('user.userid'), nullable=False)
    products = Column(JSON, nullable=False)  # Stores product list as JSON
    total_price = Column(Float, nullable=False)
    discount_per = Column(Float, nullable=False)
    time = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="orders")

# Create tables
Base.metadata.create_all(engine)
class Wishlist(Base):
    __tablename__ = 'wishlist'
    id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(Integer, ForeignKey('user.userid'), nullable=False)
    productid = Column(Integer, ForeignKey('product.productid'), nullable=False)

    user = relationship("User", backref="wishlist")
    product = relationship("Product", backref="wishlisted_by")

# User registration
def register_user():
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = hash_password(input("Enter password: "))

    if session.query(User).filter_by(username=username).first():
        print("Username already exists.")
        return
    
    new_user = User(username=username, email=email, password=password)
    session.add(new_user)
    session.commit()
    print("User registered successfully.")

# User login
def login_user():
    username = input("Username: ")
    password = hash_password(input("Password: "))
    # print("Debug: Entered password hash:", password)  # Debugging

    user = session.query(User).filter_by(username=username, password=password).first()
    # print("Debug: Retrieved user:", user)  # Check if user is fetched

    if user:
        print(f"Welcome, {user.username}!")
        user_menu(user)
    else:
        print("Invalid credentials.")




# Admin login
def login_admin():
    username = input("Enter admin username: ")
    password = hash_password(input("Enter password: "))
    admin = session.query(Admin).filter_by(username=username, password=password).first()
    if admin:
        print("Admin login successful.")
        admin_menu()
    else:
        print("Invalid credentials.")

        

# View Products
def view_products():
    products = session.query(Product).all()
    print("Available Products:")
    for product in products:
        print(f"{product.productid}: {product.name} - ${product.sellingprice} (Stock: {product.quantity})")

# Add/Remove from Wishlist
def manage_wishlist(user):
    print("(1) Add to Wishlist\n(2) Remove from Wishlist\n(3) View Wishlist")
    choice = input("Choose: ")

    if choice == "1":
        product_id = int(input("Enter product ID to add: "))

        # Check if product exists
        product = session.query(Product).filter_by(productid=product_id).first()
        if not product:
            print("Invalid product ID.")
            return

        # Check if already in wishlist
        existing_wishlist = session.query(Wishlist).filter_by(userid=user.userid, productid=product_id).first()
        if existing_wishlist:
            print("Product is already in your wishlist.")
            return

        new_wishlist_item = Wishlist(userid=user.userid, productid=product_id)
        session.add(new_wishlist_item)
        session.commit()
        print("Product added to wishlist.")

    elif choice == "2":
        product_id = int(input("Enter product ID to remove: "))

        wishlist_item = session.query(Wishlist).filter_by(userid=user.userid, productid=product_id).first()
        if wishlist_item:
            session.delete(wishlist_item)
            session.commit()
            print("Product removed from wishlist.")
        else:
            print("Product not found in wishlist.")

    elif choice == "3":
        wishlist_items = session.query(Wishlist).filter_by(userid=user.userid).all()
        if not wishlist_items:
            print("Your wishlist is empty.")
            return

        print("Your Wishlist:")
        for item in wishlist_items:
            product = session.query(Product).filter_by(productid=item.productid).first()
            if product:
                print(f"{product.productid}: {product.name} - ${product.sellingprice}")

    else:
        print("Invalid choice.")



# Add to Cart
def add_to_cart(cart):
    product_id = int(input("Enter product ID to add to cart: "))
    product = session.query(Product).filter_by(productid=product_id).first()

    if not product:
        print("Product not found.")
        return

    quantity = int(input("Enter quantity: "))

    if quantity > product.quantity:
        print("Not enough stock available.")
        return

    cart[product_id] = cart.get(product_id, 0) + quantity
    print("Product added to cart.")


# Recommend Products
def recommend_products(user):
    past_orders = session.query(Order).filter_by(userid=user.userid).all()
    recommendations = set()
    for order in past_orders:
        ordered_products = json.loads(order.products)
        recommendations.update(map(int, ordered_products.keys()))  # Convert keys to int

    print("Recommended Products:")
    for product_id in recommendations:
        product = session.query(Product).filter_by(productid=product_id).first()
        if product:
            print(f"{product.name} - ${product.sellingprice}")


# Checkout
def checkout(user, cart):
    if not cart:
        print("Cart is empty.")
        return

    total = sum(session.query(Product).filter_by(productid=pid).first().sellingprice * qty for pid, qty in cart.items())
    discount = 0.1 * total if total > 100 else 0  # 10% discount if total > $100
    final_total = total - discount

    print(f"Total: ${total:.2f}, Discount: ${discount:.2f}, Final Total: ${final_total:.2f}")
    session.add(Order(userid=user.userid, products=json.dumps(cart), total_price=final_total, discount_per=(10 if discount else 0)))
    session.commit()
    print("Order placed successfully.")
    cart.clear()


# User Menu
def user_menu(user):
    cart = {}
    while True:
        print("\n(1) View Products\n(2) Manage Wishlist\n(3) Add to Cart\n(4) View Recommendations\n(5) Checkout\n(6) Logout")
        choice = input("Choose: ")
        if choice == "1":
            view_products()
        elif choice == "2":
            manage_wishlist(user)
        elif choice == "3":
            add_to_cart(cart)
        elif choice == "4":
            recommend_products(user)
        elif choice == "5":
            checkout(user, cart)
        elif choice == "6":
            print("Logging out...")
            break
        else:
            print("Invalid choice.")

def admin_menu():
    while True:
        print("\nAdmin Dashboard")
        print("1. View Products")
        print("2. Manage Products")
        print("3. View Orders")
        print("4. Analysis")
        print("5. Validate Payment")
        print("6. Logout")

        choice = input("Select an option: ")

        if choice == '1':
            view_product()
        elif choice == '2':
            manage_products()
        elif choice == '3':
            view_orders()
        elif choice == '4':
            analysis()
        elif choice == '5':
            validate_payment()
        elif choice == '6':
            print("Logging out...")
            return  # Exit the function properly
        else:
            print("Invalid option.")

def view_product():
    products = session.query(Product).all()
    print("\nAvailable Products:")
    for p in products:
        print(f"ID: {p.productid}, Name: {p.name}, Cost Price: {p.costprice}, Selling Price: {p.sellingprice}, Stock: {p.quantity}")

    plot_stock_graph(products)

def plot_stock_graph(products):
    names = [p.name for p in products]
    stocks = [p.quantity for p in products]
    plt.bar(names, stocks)
    plt.xlabel('Products')
    plt.ylabel('Stock Level')
    plt.title('Stock Analysis')
    plt.show()

def manage_products():
    while True:
        print("1. Add Product")
        print("2. Update Product")
        print("3. Delete Product")
        print("4. Exit")
        option = input("Select an option: ")
        if option == '1':
            name = input("Product name: ")
            quantity = int(input("Product quantity: "))
            cost_price = float(input("Product cost price: "))
            selling_price = float(input("Product selling price: "))

            new_product = Product(name=name, quantity=quantity, costprice=cost_price, sellingprice=selling_price)
            session.add(new_product)
            session.commit()
            print("Product added successfully.")

        elif option == '2':
            product_id = int(input("Product ID to update: "))
            product = session.get(Product, product_id)  # Updated line

            if product:
                product.name = input("New name: ")
                product.costprice = float(input("New cost price: "))
                product.sellingprice = float(input("New selling price: "))
                product.quantity = int(input("New stock: "))
                session.commit()
                print("Product updated successfully.")
            else:
                print("Product not found.")

        elif option == '3':
            product_id = int(input("Product ID to delete: "))
            product = session.get(Product, product_id)  # Updated line

            if product:
                session.delete(product)
                session.commit()
                print("Product deleted successfully.")
            else:
                print("Product not found.")

        elif option == '4':
                print("Exiting...")
                break
        else:
            print("Invalid choice!")
       


def view_orders():
    orders = session.query(Order).all()
    print("\nOrder History:")
    for o in orders:
        print(f"Order ID: {o.orderid}, User ID: {o.userid}, Total: {o.total_price}, Time: {o.time}")

def analysis():
    revenue = session.query(func.sum(Order.total_price)).scalar()
    print(f"Total Revenue: {revenue}")

    most_bought = session.query(Order.products, func.count(Order.orderid)).group_by(Order.products).order_by(func.count(Order.orderid).desc()).first()
    if most_bought:
        print(f"Most Bought Product: {most_bought[0]} (Quantity: {most_bought[1]})")

def validate_payment():
    try:
        order_id = int(input("Enter order ID to validate: "))
        order = session.get(Order, order_id)  # Updated line

        if order:
            print(f"Order Validated: {order.orderid}, Total: {order.total_price}")
        else:
            print("Invalid Order ID.")
    except ValueError:
        print("Please enter a valid integer for the order ID.")


def add_dummy_data():
    # Check if data already exists
    if session.query(Admin).count() == 0:
        admin1 = Admin(username="admin", password=hash_password("admin123"))
        session.add(admin1)

    if session.query(Product).count() == 0:
        product1 = Product(name="Laptop", quantity=10, costprice=500.00, sellingprice=700.00)
        product2 = Product(name="Phone", quantity=15, costprice=300.00, sellingprice=500.00)
        product3 = Product(name="Headphones", quantity=25, costprice=50.00, sellingprice=80.00)
        session.add_all([product1, product2, product3])

    session.commit()
    print("Dummy data added.")

def main():
    add_dummy_data()
    while True:
        print("Choose: \n(1) User \n(2) Admin \n(3) Exit")
        choice = input()
        if choice == "1":
            print("Choose: \n(1) Register \n(2) Login ")
            action = input()
            if action == "1":
                register_user()  # Implement this function
            elif action == "2":
                login_user()  # This will take the user to the user menu
            else:
                print("Invalid choice.")
        elif choice == "2":
            admin = login_admin()
            if admin:
                print(f"Welcome, Admin {admin.username}!")
                admin_menu()
        elif choice == "3":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
