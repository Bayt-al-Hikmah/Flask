from flask import Flask, request, jsonify
products_db = {
    "100": {"name": "Laptop", "price": 1200},
    "101": {"name": "Mouse", "price": 25},
    "102": {"name": "Keyboard", "price": 75}
}

app = Flask(__name__)

@app.route('/api/products/<product_id>')
def get_product(product_id):
    product = products_db.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    currency = request.args.get('currency', 'USD')

    response_data = {
        "id": product_id,
        "name": product["name"],
        "price": product["price"],
        "currency": currency
    }
    return jsonify(response_data)


if __name__ == "__main__" :
    app.run(port=3000,debug=True)