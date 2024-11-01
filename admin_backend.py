from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

# Database connection function
def db_connection():
    conn = sqlite3.connect("products.db")
    return conn

# Admin page route
@app.route('/')
def admin():
    return render_template("admin.html")

# Fetch all products
@app.route('/products', methods=['GET'])
def get_products():
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return jsonify(products)

# Add a new product
@app.route('/product', methods=['POST'])
def add_product():
    new_product = request.json
    name = new_product["name"]
    description = new_product["description"]
    price = new_product["price"]
    image_url = new_product["image_url"]

    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO products (name, description, price, image_url) VALUES (?, ?, ?, ?)''',
                   (name, description, price, image_url))
    conn.commit()
    conn.close()
    return jsonify({"message": "Product added successfully!"}), 201

# Update an existing product
@app.route('/product/<int:id>', methods=['PUT'])
def update_product(id):
    conn = db_connection()
    cursor = conn.cursor()
    updated_product = request.json
    cursor.execute('''
        UPDATE products SET name = ?, description = ?, price = ?, image_url = ?
        WHERE id = ?
    ''', (updated_product["name"], updated_product["description"], updated_product["price"], updated_product["image_url"], id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Product updated successfully!"})

# Delete a product
@app.route('/product/<int:id>', methods=['DELETE'])
def delete_product(id):
    conn = db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Product deleted successfully!"})

# Run the Flask app
if __name__ == "__main__":
    app.run(port=5000)
