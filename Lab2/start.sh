#!/bin/sh
# Start the Flask app
flask run &

# Start the WebSocket server
python -c "import asyncio; import app; asyncio.run(app.start_websocket_server())"
