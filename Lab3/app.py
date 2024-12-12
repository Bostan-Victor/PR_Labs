from flask import Flask, request, jsonify
from models import db, Product

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/products', methods=['POST'])
def create_products():
    data = request.get_json()

    filtered_products = data.get('filtered_products', [])

    if not isinstance(filtered_products, list) or not filtered_products:
        return jsonify({'error': 'Invalid or missing filtered_products'}), 400

    created_products = []
    for product in filtered_products:
        try:
            new_product = Product(
                name=product['name'],
                price_mdl=product['price_mdl'],
                price_eur=product['price_eur']
            )
            db.session.add(new_product)
            created_products.append(new_product.name)
        except KeyError as e:
            return jsonify({'error': f'Missing key in product: {e}'}), 400

    db.session.commit()

    return jsonify({
        'message': f'{len(created_products)} products created',
        'created_products': created_products
    }), 201

# READ
@app.route('/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int) 
    limit = request.args.get('limit', 5, type=int) 

    offset = (page - 1) * limit

    products = Product.query.offset(offset).limit(limit).all()

    result = [{'id': p.id, 'name': p.name, 'price_mdl': p.price_mdl, 'price_eur': p.price_eur} for p in products]

    total_products = Product.query.count()
    total_pages = (total_products + limit - 1) // limit

    response = {
        'products': result,
        'page': page,
        'limit': limit,
        'total_pages': total_pages,
        'total_products': total_products
    }

    return jsonify(response)

# UPDATE
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    product = Product.query.get(id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    product.name = data['name']
    product.price_mdl = data['price_mdl']
    product.price_eur = data['price_eur']
    db.session.commit()
    return jsonify({'message': 'Product updated'})

# DELETE
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'})

# UPLOAD FILE
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file:
        file_contents = file.read().decode('utf-8')
        print(f"Received file content: {file_contents}")
        return jsonify({'message': 'File content received', 'contents': file_contents}), 200

if __name__ == '__main__':
    app.run(port=5000)
