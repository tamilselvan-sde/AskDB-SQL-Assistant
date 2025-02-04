import sqlite3

# Connect to the Ecommerce database
conn = sqlite3.connect("Ecommerce.db")
cursor = conn.cursor()

# Drop tables if they exist (Optional: to start fresh)
cursor.execute("DROP TABLE IF EXISTS orders")
cursor.execute("DROP TABLE IF EXISTS payment")

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

# Create the payment table with the provided schema and different names
cursor.execute('''
    CREATE TABLE payment (
        order_id INTEGER PRIMARY KEY,
        customer_name TEXT,
        product_name TEXT,
        phone_number TEXT,
        amount REAL,
        payment_status TEXT,
        quantity INTEGER,
        payment_date TEXT,
        payment_type TEXT,
        refund_status TEXT
    )
''')

# Insert 50 rows of unique sample data into the payment table with different names
cursor.executemany('''
    INSERT INTO payment (order_id, customer_name, product_name, phone_number, amount, payment_status, quantity, payment_date, payment_type, refund_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', [
    (1, "John Carter", "Wireless Keyboard", "123-456-1111", 35.99, "Completed", 1, "2024-01-20", "Debit Card", "No"),
    (2, "Nancy Hill", "Gaming Headset", "234-567-2222", 129.99, "Completed", 1, "2024-01-21", "Credit Card", "No"),
    (3, "Oliver Green", "Sports Shoes", "345-678-3333", 69.99, "Pending", 2, "2024-01-22", "PayPal", "Yes"),
    (4, "Rachel King", "Smartphone", "456-789-4444", 499.99, "Completed", 1, "2024-01-23", "Debit Card", "No"),
    (5, "Sophia Brown", "Desk Chair", "567-890-5555", 199.99, "Completed", 2, "2024-01-24", "Credit Card", "No"),
    (6, "Kevin Walker", "Monitor Stand", "678-901-6666", 49.99, "Pending", 1, "2024-01-25", "PayPal", "No"),
    (7, "Laura Clark", "Projector", "789-012-7777", 399.99, "Completed", 1, "2024-01-26", "Debit Card", "No"),
    (8, "Ethan Lewis", "Mechanical Keyboard", "890-123-8888", 129.99, "Completed", 1, "2024-01-27", "Credit Card", "No"),
    (9, "Mia Harris", "Yoga Mat", "901-234-9999", 24.99, "Completed", 1, "2024-01-28", "PayPal", "No"),
    (10, "Daniel Carter", "Smartphone Stand", "012-345-0000", 15.99, "Completed", 3, "2024-01-29", "Debit Card", "No"),
    (11, "Liam Scott", "Wireless Earbuds", "123-456-1112", 79.99, "Pending", 1, "2024-02-01", "PayPal", "Yes"),
    (12, "Olivia Mitchell", "Fitness Tracker", "234-567-2223", 89.99, "Completed", 1, "2024-02-02", "Credit Card", "No"),
    (13, "James Johnson", "Tennis Shoes", "345-678-3334", 79.99, "Pending", 2, "2024-02-03", "Debit Card", "Yes"),
    (14, "Megan Wilson", "Smart TV", "456-789-4445", 699.99, "Completed", 1, "2024-02-04", "PayPal", "No"),
    (15, "Ethan Brown", "Gaming Chair", "567-890-5556", 219.99, "Completed", 1, "2024-02-05", "Debit Card", "No"),
    (16, "Benjamin Clark", "Gaming Console", "678-901-6667", 299.99, "Completed", 1, "2024-02-06", "Credit Card", "No"),
    (17, "Ella Miller", "LED Projector", "789-012-7778", 499.99, "Completed", 1, "2024-02-07", "PayPal", "No"),
    (18, "Chloe Davis", "Laptop", "890-123-8889", 799.99, "Pending", 1, "2024-02-08", "Debit Card", "Yes"),
    (19, "Jack Thompson", "Digital Watch", "901-234-9990", 129.99, "Completed", 1, "2024-02-09", "Credit Card", "No"),
    (20, "Charlotte Lee", "Smartphone Charger", "012-345-0001", 19.99, "Pending", 2, "2024-02-10", "PayPal", "Yes"),
    (21, "Sebastian Wright", "Washing Machine", "123-456-2222", 549.99, "Completed", 1, "2024-02-11", "Debit Card", "No"),
    (22, "Isabelle Turner", "Air Purifier", "234-567-3333", 99.99, "Completed", 1, "2024-02-12", "PayPal", "No"),
    (23, "Vincent Clark", "Microwave", "345-678-4444", 159.99, "Pending", 1, "2024-02-13", "Credit Card", "Yes"),
    (24, "Georgia Barnes", "Smartphone Stand", "456-789-5555", 49.99, "Completed", 1, "2024-02-14", "Debit Card", "No"),
    (25, "Nina Cole", "Electric Grill", "567-890-6666", 129.99, "Completed", 1, "2024-02-15", "PayPal", "No"),
    (26, "Zane Mitchell", "Wall Clock", "678-901-7777", 39.99, "Pending", 1, "2024-02-16", "Debit Card", "Yes"),
    (27, "Lucas Young", "Refrigerator", "789-012-8888", 699.99, "Completed", 1, "2024-02-17", "Credit Card", "No"),
    (28, "Eliza Cooper", "Blender", "890-123-9999", 89.99, "Completed", 1, "2024-02-18", "PayPal", "No"),
    (29, "Victor Stone", "Electric Toothbrush", "901-234-1111", 29.99, "Pending", 1, "2024-02-19", "Debit Card", "Yes"),
    (30, "Brianna Hayes", "Vacuum Cleaner", "012-345-2222", 229.99, "Completed", 1, "2024-02-20", "Credit Card", "No"),
    (31, "Theo Harrison", "Electric Kettle", "123-456-3333", 34.99, "Completed", 1, "2024-02-21", "PayPal", "No"),
    (32, "Amos Powell", "Desk Lamp", "234-567-4444", 39.99, "Pending", 1, "2024-02-22", "Debit Card", "Yes"),
    (33, "Isabel Parker", "Smart Watch", "345-678-5555", 199.99, "Completed", 1, "2024-02-23", "Credit Card", "No"),
    (34, "Mason Bryant", "Hand Mixer", "456-789-6666", 79.99, "Pending", 1, "2024-02-24", "PayPal", "Yes"),
    (35, "Sophia Richards", "Smartphone Case", "567-890-7777", 19.99, "Completed", 2, "2024-02-25", "Debit Card", "No"),
    (36, "Tyler Walker", "Smartphone Screen Protector", "678-901-8888", 9.99, "Completed", 1, "2024-02-26", "Credit Card", "No"),
    (37, "Jade Murphy", "Camera", "789-012-9999", 299.99, "Completed", 1, "2024-02-27", "PayPal", "No"),
    (38, "Ryan Sullivan", "Portable Charger", "890-123-0000", 49.99, "Pending", 2, "2024-02-28", "Debit Card", "Yes"),
    (39, "Liam Gray", "Tablet Stand", "901-234-1112", 19.99, "Completed", 1, "2024-03-01", "Credit Card", "No"),
    (40, "Olivia Dean", "Power Bank", "012-345-2222", 29.99, "Completed", 3, "2024-03-02", "PayPal", "No"),
    (41, "Gabriel Ford", "Cooking Pan", "123-456-3334", 29.99, "Completed", 1, "2024-03-03", "Debit Card", "No"),
    (42, "Eve Brooks", "Iron", "234-567-4444", 59.99, "Completed", 1, "2024-03-04", "Credit Card", "No"),
    (43, "Freya Green", "Coffee Maker", "345-678-5555", 99.99, "Pending", 1, "2024-03-05", "PayPal", "Yes"),
    (44, "Elijah Wilson", "Camera Lens", "456-789-6666", 199.99, "Completed", 1, "2024-03-06", "Debit Card", "No"),
    (45, "Chloe Taylor", "Fridge Organizer", "567-890-7777", 29.99, "Completed", 1, "2024-03-07", "Credit Card", "No"),
    (46, "Jason Brown", "Fitness Tracker", "678-901-8888", 119.99, "Pending", 1, "2024-03-08", "PayPal", "No"),
    (47, "Madison Carter", "Smartphone Cover", "789-012-9999", 14.99, "Completed", 2, "2024-03-09", "Debit Card", "No"),
    (48, "Parker Brooks", "Hand Mixer", "890-123-1111", 69.99, "Completed", 1, "2024-03-10", "Credit Card", "No"),
    (49, "Zara Hill", "Blender", "901-234-2222", 89.99, "Completed", 1, "2024-03-11", "PayPal", "No"),
    (50, "Xander Lewis", "Air Purifier", "012-345-3333", 119.99, "Pending", 1, "2024-03-12", "Debit Card", "Yes")
])

# Commit the transaction
conn.commit()

# Close the connection
conn.close()

print("Both orders and payment tables have been created and populated with 50 unique rows each!")
