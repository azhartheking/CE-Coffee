import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import time

# Initialize data (mock data for menu and inventory)
menu = {
    "Americano": 5.00,
    "Cappuccino": 6.00,
    "Latte": 6.50,
    "Caramel Macchiato": 7.00
}

default_inventory = {
    "coffee_beans": 1000,  # grams
    "milk": 500,           # ml
    "sugar": 200,          # grams
    "cups": 100            # count
}

# Initialize session state for order history, inventory, login status, loyalty points, and ratings
if "order_history" not in st.session_state:
    st.session_state["order_history"] = []
if "inventory" not in st.session_state:
    st.session_state["inventory"] = default_inventory.copy()
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "is_customer" not in st.session_state:
    st.session_state["is_customer"] = False
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "loyalty_points" not in st.session_state:
    st.session_state["loyalty_points"] = {}
if "ratings" not in st.session_state:
    st.session_state["ratings"] = []
if "current_order" not in st.session_state:
    st.session_state["current_order"] = None

# Function to add loyalty points
def add_loyalty_points(customer_name, points):
    if customer_name in st.session_state["loyalty_points"]:
        st.session_state["loyalty_points"][customer_name] += points
    else:
        st.session_state["loyalty_points"][customer_name] = points

# Function to generate an invoice
def generate_invoice(order):
    return f"""
    Invoice
    ---------
    Customer Name: {order['customer_name']}
    Coffee Type: {order['coffee_type']}
    Size: {order['size']}
    Add-ons: {', '.join(order['add_ons']) if order['add_ons'] else 'None'}
    Total Price: ${order['price']:.2f}
    Order Time: {order['order_time']}
    """.encode("utf-8")

# Role selection buttons
st.sidebar.write("Select your role:")
if st.sidebar.button("Customer"):
    st.session_state["is_customer"] = True
    st.session_state["is_admin"] = False
    st.session_state["logged_in"] = True
    st.session_state["user_role"] = "customer"
    st.sidebar.success("Customer Access Granted")

if st.sidebar.button("Admin"):
    st.session_state["is_admin"] = True
    st.session_state["is_customer"] = False

# Show admin login fields if "Admin" button was clicked
if st.session_state["is_admin"]:
    username = st.sidebar.text_input("Username", key="admin_username")
    password = st.sidebar.text_input("Password", type="password", key="admin_password")
    if st.sidebar.button("Login as Admin"):
        if username == "admin" and password == "admin123":
            st.session_state["logged_in"] = True
            st.session_state["user_role"] = "admin"
            st.sidebar.success("Admin Access Granted")
        else:
            st.sidebar.error("Invalid admin credentials.")
            st.session_state["is_admin"] = False  # Reset admin flag if login fails

# App title
st.sidebar.title("BrewMate App Navigation")

# Sidebar for navigation
page = st.sidebar.radio("Go to", ("Home", "About Us", "Contact Us", "Admin Panel"))

# Display appropriate page based on selection
if page == "Home":
    # Display promotions page if user is not logged in
    if not st.session_state["logged_in"]:
        st.title("Welcome to BrewMate!")
        st.subheader("Exclusive Promotions and Benefits!")
        st.image("https://images.unsplash.com/photo-1511920170033-f8396924c348", use_column_width=True)
        promotions = ["**Enjoy 10% off on your first order, earn loyalty points for every dollar spent, get exclusive member promotions, a free birthday coffee, and priority customer support!**"]
        for promotion in promotions:
            st.markdown(promotion)
        st.write("Click below to join our membership and start enjoying the benefits!")
        if st.button("Join Now"):
            st.success("Thank you for joining! You are now a valued member of our coffee shop family.")

elif page == "About Us":
    st.title("About BrewMate")
    st.write("BrewMate is a coffee shop dedicated to providing the best coffee experience. We offer a variety of handcrafted beverages, each made with care and passion. Our goal is to create a welcoming environment for all our customers, where great coffee and community come together.")
    # Team pictures
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image('azhar.jpg', caption='Azhar Ali, Founder', use_column_width=True)
    with col2:
        st.image('adrish.jpg', caption='Adrish Elnes, Co-Founder', use_column_width=True)
    with col3:
        st.image('bolo.jpg', caption='Nabilah Shamshir, Accountant', use_column_width=True)
    col4, col5 = st.columns(2)
    with col4:
        st.image('vv.jpg', caption='Vivian Hwong, Manager', use_column_width=True)
    with col5:
        st.image('dio.jpg', caption='Diocleciana, Executive Chef', use_column_width=True)

elif page == "Contact Us":
    st.title("Contact BrewMate")
    st.write("Have questions or feedback? We'd love to hear from you!")
    st.write("You can reach us at: info@brewmate.com or call us at +123-456-7890.")
    st.text_area("Leave us a message:")
    if st.button("Send Message"):
        st.success("Thank you for reaching out to us! We'll get back to you shortly.")

elif page == "Admin Panel" and st.session_state["logged_in"] and st.session_state["user_role"] == "admin":
    st.title("Admin Panel")
    st.subheader("Inventory Management")
    # Display current inventory levels
    st.write("Inventory Levels")
    for item, qty in st.session_state["inventory"].items():
        st.write(f"{item.capitalize()}: {qty} units")

    # Low stock alert
    for item, qty in st.session_state["inventory"].items():
        if qty < 20:
            st.warning(f"Low stock alert: {item}")

    # Update inventory
    item_to_restock = st.selectbox("Item to Restock", list(st.session_state["inventory"].keys()))
    restock_amount = st.number_input("Restock Amount", min_value=1)
    if st.button("Restock Inventory"):
        st.session_state["inventory"][item_to_restock] += restock_amount
        st.success(f"{item_to_restock.capitalize()} restocked successfully.")

    # Sales Reporting
    st.subheader("Sales Reporting")
    if st.session_state["order_history"]:
        sales_df = pd.DataFrame(st.session_state["order_history"])
        st.write("Total Sales Data")
        st.dataframe(sales_df)

        # Sales Breakdown by Coffee Type
        sales_summary = sales_df["coffee_type"].value_counts()
        st.bar_chart(sales_summary, use_container_width=True)

        # Total Profit Calculation (mock example)
        total_sales = sum(order["price"] for order in st.session_state["order_history"])
        st.write(f"Total Revenue: ${total_sales}")

        # Daily, Weekly, and Monthly Profit Calculation with Graphs
        today = datetime.now()
        sales_df['order_time'] = pd.to_datetime(sales_df['order_time'])

        daily_sales = sales_df[sales_df['order_time'] >= (today - timedelta(days=1))]
        weekly_sales = sales_df[sales_df['order_time'] >= (today - timedelta(weeks=1))]
        monthly_sales = sales_df[sales_df['order_time'] >= (today - timedelta(days=30))]

        daily_profit = daily_sales['price'].sum()
        weekly_profit = weekly_sales['price'].sum()
        monthly_profit = monthly_sales['price'].sum()

        profit_data = pd.DataFrame({
            'Period': ['Daily', 'Weekly', 'Monthly'],
            'Profit': [daily_profit, weekly_profit, monthly_profit]
        })
        st.write(f"Daily Profit: ${daily_profit:.2f}")
        st.write(f"Weekly Profit: ${weekly_profit:.2f}")
        st.write(f"Monthly Profit: ${monthly_profit:.2f}")
        st.bar_chart(profit_data.set_index('Period'), use_container_width=True)

        # Least and Best Selling Product
        st.subheader("Product Performance")
        best_selling = sales_summary.idxmax()
        least_selling = sales_summary.idxmin()
        st.write(f"Best Selling Product: {best_selling}")
        st.write(f"Least Selling Product: {least_selling}")
        st.bar_chart(sales_summary, use_container_width=True, title="Product Sales Performance")

    # Display loyalty points summary
    st.subheader("Loyalty Points Summary")
    loyalty_points_df = pd.DataFrame(st.session_state["loyalty_points"].items(), columns=["Customer", "Points"])
    st.dataframe(loyalty_points_df)

    # Display ratings summary
    st.subheader("Ratings Summary")
    if st.session_state["ratings"]:
        ratings_df = pd.DataFrame(st.session_state["ratings"], columns=["Customer", "Rating", "Feedback"])
        st.dataframe(ratings_df)
        avg_rating = ratings_df["Rating"].mean()
        st.write(f"Average Rating: {avg_rating:.2f} / 5")

# Customer Order Process
if st.session_state["logged_in"] and st.session_state["user_role"] == "customer":
    st.subheader("Place Your Order")
    customer_name = st.text_input("Enter Your Name")
    coffee_type = st.selectbox("Select Coffee Type", list(menu.keys()))
    coffee_size = st.radio("Choose Size", ("Small", "Medium", "Large"))
    add_ons = st.multiselect("Add-ons", ["Extra sugar", "Milk"])

    # Payment Integration before Order Placement
    st.subheader("Payment Integration")
    payment_method = st.selectbox("Choose Payment Method", ["Credit Card", "PayPal"])
    if st.button("Confirm Payment"):
        st.success("Payment successful!")
        order = {
            "customer_name": customer_name,
            "coffee_type": coffee_type,
            "size": coffee_size,
            "add_ons": add_ons,
            "price": menu[coffee_type],
            "order_time": datetime.now()
        }
        st.session_state["current_order"] = order
        st.session_state["order_history"].append(order)
        st.success(f"Order placed! Your coffee will be ready shortly. Order: {coffee_type} ({coffee_size})")

        # Add loyalty points (e.g., 1 point per $1 spent)
        points_earned = int(order["price"])
        add_loyalty_points(customer_name, points_earned)
        st.info(f"{points_earned} loyalty points added. Total points: {st.session_state['loyalty_points'].get(customer_name, 0)}")

        # Update Inventory based on order (basic example)
        st.session_state["inventory"]["coffee_beans"] -= 10  # Adjust amount as per recipe
        st.session_state["inventory"]["cups"] -= 1

        # Start countdown for order preparation
        for i in range(5, 0, -1):
            st.info(f"Your order will be ready in {i} seconds...")
            time.sleep(1)
        st.success(f"{st.session_state['current_order']['customer_name']}, your {st.session_state['current_order']['coffee_type']} is ready!")
