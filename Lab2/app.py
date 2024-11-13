from flask import Flask, request, jsonify
from models import db, Product
import threading
import asyncio
import websockets
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@db:5432/mydatabase'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

# CREATE
@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = Product(
        name=data['name'],
        price_mdl=data['price_mdl'],
        price_eur=data['price_eur']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product created'}), 201

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

        print(file_contents)

        return jsonify({'message': 'File content received', 'contents': file_contents}), 200
    
# In-memory structure for the chat rooms
chat_rooms = {"general": set()}  # Default chat room

async def chat_handler(websocket, path):
    current_room = None
    try:
        async for message in websocket:
            data = json.loads(message)
            command = data.get("command")
            username = data.get("username")

            # User joins a room
            if command == "join_room":
                room = data.get("room", "general")
                current_room = room
                if room not in chat_rooms:
                    chat_rooms[room] = set()
                chat_rooms[room].add(websocket)
                join_msg = f"{username} joined {room}"
                await broadcast(room, json.dumps({"message": join_msg}))

            # User sends a message
            elif command == "send_msg" and current_room:
                msg = data.get("message")
                if msg:
                    broadcast_message = json.dumps({"username": username, "message": msg})
                    await broadcast(current_room, broadcast_message)

            # User leaves the room
            elif command == "leave_room" and current_room:
                chat_rooms[current_room].discard(websocket)
                leave_msg = f"{username} left {current_room}"
                await broadcast(current_room, json.dumps({"message": leave_msg}))
                current_room = None

    except websockets.ConnectionClosed:
        # Handle disconnection
        if current_room:
            chat_rooms[current_room].discard(websocket)

async def broadcast(room, message):
    # Send the message to all clients in the room
    clients = chat_rooms.get(room, set())
    for ws in clients:
        if ws.open:  # Only to active connections
            await ws.send(message)

async def start_websocket_server():
    async with websockets.serve(chat_handler, "localhost", 6790):
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    # Start WebSocket server in a new thread
    websocket_thread = threading.Thread(target=lambda: asyncio.run(start_websocket_server()))
    websocket_thread.start()

    # Start Flask HTTP server
    app.run(port=5000)
