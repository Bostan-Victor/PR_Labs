import pika
import requests
import json
import threading
import time
import ftplib
import os
import requests

FTP_HOST = 'localhost'
FTP_PORT = 21
FTP_USER = 'testuser'
FTP_PASS = 'testpass'
FTP_FILE = 'processed_data.json'

LAB2_UPLOAD_URL = 'http://localhost:5000/upload'

def fetch_file_from_ftp():
    while True:
        try:
            with ftplib.FTP() as ftp:
                ftp.connect(FTP_HOST, FTP_PORT)
                ftp.login(FTP_USER, FTP_PASS)
                
                local_file = f"./downloads/{FTP_FILE}"
                os.makedirs(os.path.dirname(local_file), exist_ok=True)
                with open(local_file, 'wb') as f:
                    ftp.retrbinary(f"RETR {FTP_FILE}", f.write)

            with open(local_file, 'rb') as f:
                response = requests.post(
                    LAB2_UPLOAD_URL, 
                    files={'file': (FTP_FILE, f)}
                )
                print(f"File uploaded to Lab2 server. Response: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"Error fetching or uploading file: {e}")
        
        # Wait 30 seconds
        time.sleep(30)

def callback(ch, method, properties, body):
    print(f"Received message: {body}")
    data = json.loads(body)

    response = requests.post('http://localhost:5000/products', json=data)
    print(f"Sent to webserver. Response: {response.status_code} - {response.text}")

def consume_from_rabbitmq(queue):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=queue)

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    print(f"Waiting for messages on queue: {queue}")
    channel.start_consuming()

ftp_thread = threading.Thread(target=fetch_file_from_ftp, daemon=True)
ftp_thread.start()

consume_from_rabbitmq('product_queue')
