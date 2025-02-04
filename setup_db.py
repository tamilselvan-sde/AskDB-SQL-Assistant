import sqlite3

# Connect to the Ecommerce database (or create it if it doesn't exist)
conn = sqlite3.connect("Ecommerce.db")
cursor = conn.cursor()

# Drop the table if it exists (Optional: Only use if you want a fresh start)
cursor.execute("DROP TABLE IF EXISTS orders")

# Create the orders table with the provided schema
cursor.execute('''
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_name TEXT,
        product_name TEXT,
        category TEXT,
        quantity INTEGER,
        price REAL,
        offer REAL,
        rating REAL,
        order_date TEXT,
        status TEXT
    )
''')

# Insert 50 rows of unique sample data into the orders table
cursor.executemany('''
    INSERT INTO orders (order_id, customer_name, product_name, category, quantity, price, offer, rating, order_date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', [
    (1, "Alice Johnson", "Wireless Mouse", "Electronics", 1, 29.99, 10.00, 4.5, "2024-01-20", "Shipped"),
    (2, "Bob Smith", "Bluetooth Headphones", "Electronics", 2, 79.99, 5.00, 4.2, "2024-01-21", "Delivered"),
    (3, "Charlie Brown", "Running Shoes", "Footwear", 1, 49.99, 15.00, 4.0, "2024-01-22", "Pending"),
    (4, "David Wilson", "Smartwatch", "Electronics", 1, 199.99, 20.00, 4.8, "2024-01-23", "Shipped"),
    (5, "Emma Davis", "Office Chair", "Furniture", 1, 149.99, 12.00, 4.3, "2024-01-24", "Processing"),
    (6, "Frank White", "Laptop Stand", "Accessories", 1, 39.99, 8.00, 4.1, "2024-01-25", "Delivered"),
    (7, "Grace Hall", "LED Monitor", "Electronics", 1, 179.99, 18.00, 4.7, "2024-01-26", "Pending"),
    (8, "Henry Adams", "Gaming Keyboard", "Electronics", 1, 99.99, 10.00, 4.4, "2024-01-27", "Shipped"),
    (9, "Isabel Lee", "Yoga Mat", "Fitness", 1, 19.99, 5.00, 4.0, "2024-01-28", "Delivered"),
    (10, "Jack Turner", "Smartphone Case", "Accessories", 2, 10.99, 2.00, 3.9, "2024-01-29", "Processing"),
    (11, "Liam Davis", "Wireless Headphones", "Electronics", 1, 59.99, 15.00, 4.5, "2024-02-01", "Shipped"),
    (12, "Olivia Johnson", "Fitness Tracker", "Electronics", 1, 99.99, 10.00, 4.4, "2024-02-02", "Delivered"),
    (13, "James Brown", "Sports Shoes", "Footwear", 2, 79.99, 10.00, 4.3, "2024-02-03", "Pending"),
    (14, "Sophia Smith", "Smartphone", "Electronics", 1, 699.99, 50.00, 4.8, "2024-02-04", "Shipped"),
    (15, "Mia Wilson", "Dining Table", "Furniture", 1, 499.99, 20.00, 4.6, "2024-02-05", "Processing"),
    (16, "Benjamin Lee", "Gaming Chair", "Furniture", 1, 199.99, 25.00, 4.4, "2024-02-06", "Delivered"),
    (17, "Avery Adams", "LED TV", "Electronics", 1, 799.99, 40.00, 4.9, "2024-02-07", "Shipped"),
    (18, "Chloe Turner", "Keyboard", "Accessories", 2, 29.99, 5.00, 4.3, "2024-02-08", "Pending"),
    (19, "Jackson Brown", "Wrist Watch", "Accessories", 1, 149.99, 10.00, 4.2, "2024-02-09", "Delivered"),
    (20, "Charlotte Davis", "Tablet", "Electronics", 1, 299.99, 15.00, 4.7, "2024-02-10", "Processing"),
    (21, "Ethan White", "Air Purifier", "Home Appliances", 1, 129.99, 8.00, 4.5, "2024-02-11", "Shipped"),
    (22, "Amelia Lee", "Electric Kettle", "Home Appliances", 1, 39.99, 12.00, 4.4, "2024-02-12", "Delivered"),
    (23, "Harper Turner", "Smartphone Stand", "Accessories", 3, 19.99, 5.00, 4.2, "2024-02-13", "Pending"),
    (24, "Sebastian Smith", "Vacuum Cleaner", "Home Appliances", 1, 199.99, 10.00, 4.3, "2024-02-14", "Shipped"),
    (25, "Lily Johnson", "Portable Charger", "Electronics", 2, 49.99, 8.00, 4.6, "2024-02-15", "Processing"),
    (26, "Alexander Wilson", "Coffee Maker", "Home Appliances", 1, 99.99, 20.00, 4.4, "2024-02-16", "Delivered"),
    (27, "Jack Lee", "Desk Lamp", "Furniture", 1, 39.99, 7.00, 4.2, "2024-02-17", "Shipped"),
    (28, "Aiden Brown", "Microwave", "Home Appliances", 1, 129.99, 15.00, 4.5, "2024-02-18", "Pending"),
    (29, "Levi Adams", "Smart Watch", "Electronics", 1, 199.99, 20.00, 4.8, "2024-02-19", "Delivered"),
    (30, "Scarlett Turner", "Blender", "Home Appliances", 1, 89.99, 10.00, 4.3, "2024-02-20", "Shipped"),
    (31, "Nora White", "Electric Toothbrush", "Home Appliances", 2, 29.99, 5.00, 4.1, "2024-02-21", "Processing"),
    (32, "Elliot Smith", "Smartphone Cover", "Accessories", 2, 14.99, 3.00, 4.3, "2024-02-22", "Delivered"),
    (33, "Mason Brown", "Bluetooth Speaker", "Electronics", 1, 59.99, 12.00, 4.6, "2024-02-23", "Shipped"),
    (34, "Archer Johnson", "Refrigerator", "Home Appliances", 1, 799.99, 50.00, 4.7, "2024-02-24", "Delivered"),
    (35, "Evelyn Lee", "Cooking Pan", "Home Appliances", 1, 29.99, 7.00, 4.0, "2024-02-25", "Shipped"),
    (36, "Carter White", "Iron", "Home Appliances", 1, 59.99, 10.00, 4.2, "2024-02-26", "Processing"),
    (37, "Gabriella Turner", "Hand Mixer", "Home Appliances", 1, 69.99, 15.00, 4.4, "2024-02-27", "Delivered"),
    (38, "Harrison Adams", "Camera", "Electronics", 1, 299.99, 20.00, 4.6, "2024-02-28", "Shipped"),
    (39, "Zoe Wilson", "Washing Machine", "Home Appliances", 1, 499.99, 25.00, 4.7, "2024-03-01", "Pending"),
    (40, "Lucas Brown", "Air Conditioner", "Home Appliances", 1, 799.99, 30.00, 4.8, "2024-03-02", "Shipped"),
    (41, "Grace Johnson", "Electric Grill", "Home Appliances", 1, 129.99, 10.00, 4.2, "2024-03-03", "Delivered"),
    (42, "Nolan Lee", "Guitar", "Music", 1, 199.99, 20.00, 4.4, "2024-03-04", "Shipped"),
    (43, "Benjamin Turner", "Wall Clock", "Furniture", 1, 39.99, 5.00, 4.1, "2024-03-05", "Pending"),
    (44, "Luca Smith", "Power Bank", "Electronics", 3, 29.99, 8.00, 4.3, "2024-03-06", "Delivered"),
    (45, "Isaac Adams", "Office Desk", "Furniture", 1, 299.99, 15.00, 4.5, "2024-03-07", "Shipped"),
    (46, "Elijah Johnson", "Fitness Tracker", "Electronics", 1, 129.99, 20.00, 4.6, "2024-03-08", "Delivered"),
    (47, "Aubrey Lee", "Air Purifier", "Home Appliances", 1, 79.99, 12.00, 4.2, "2024-03-09", "Processing"),
    (48, "Samantha White", "Smartphone Case", "Accessories", 2, 19.99, 3.00, 4.0, "2024-03-10", "Shipped"),
    (49, "Aidan Turner", "Headphones", "Electronics", 1, 59.99, 10.00, 4.3, "2024-03-11", "Delivered"),
    (50, "Katherine Smith", "Home Theater", "Electronics", 1, 399.99, 30.00, 4.7, "2024-03-12", "Shipped")
])

# Commit the transaction
conn.commit()

# Close the connection
conn.close()

print("Ecommerce database reset complete, and orders table with 50 unique rows added successfully!")
