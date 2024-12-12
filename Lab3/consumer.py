import pika
import requests
import json

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

consume_from_rabbitmq('product_queue')
