import socket
import threading
import random
import time
import json
from threading import Lock, Condition

HOST = '127.0.0.1'
PORT = 65432

file_lock = Lock()
write_condition = Condition(file_lock)
readers = 0  

data_file = 'data.json'

def initialize_file():
    with file_lock:
        try:
            with open(data_file, 'x') as file:
                json.dump({}, file)
        except FileExistsError:
            pass

initialize_file()

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    try:
        while True:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                break

            command = data.strip().lower()

            # Check for exit command
            if command == "exit":
                print(f"Client {addr} requested to disconnect.")
                conn.sendall(b"Goodbye!")
                break

            # Handle read command
            elif command == "read":
                handle_read(conn)

            # Handle write command
            elif command.startswith("write"):
                message = command.split(" ", 1)[1]
                handle_write(conn, message)
            else:
                conn.sendall(b"Invalid command\n")
    except (ConnectionResetError, BrokenPipeError):
        print(f"Connection lost with {addr}")
    finally:
        conn.close()
        print(f"Connection closed by {addr}")

def handle_read(conn):
    global readers
    with file_lock:
        # Check if a write operation is happening
        while readers == -1:
            conn.sendall(b"Write operation in progress, please wait...\n")  
            write_condition.wait()
        readers += 1

    time.sleep(random.randint(1, 7))

    with file_lock:
        with open(data_file, 'r') as file:
            data = json.load(file)
        conn.sendall(json.dumps(data).encode('utf-8') + b'\n')

    with file_lock:
        readers -= 1
        if readers == 0:
            write_condition.notify_all()

def handle_write(conn, message):
    global readers
    with file_lock:
        # Wait for all readers to finish
        while readers > 0:
            write_condition.wait() 
        readers = -1 

    time.sleep(random.randint(1, 7))

    with file_lock:
        with open(data_file, 'r+') as file:
            data = json.load(file)
            if 'messages' not in data:
                data['messages'] = []
            data['messages'].append(message)
            file.seek(0)
            json.dump(data, file)
            file.truncate()

    with file_lock:
        readers = 0 
        write_condition.notify_all()

    conn.sendall(b"Write operation successful\n")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    start_server()
