import socket
import ssl
from bs4 import BeautifulSoup
from functools import reduce
from datetime import datetime, timezone
import pika
import json

MDL_TO_EUR_RATE = 19.5  
EUR_TO_MDL_RATE = 1 / MDL_TO_EUR_RATE  

def mdl_to_eur(price_mdl):
    return price_mdl / MDL_TO_EUR_RATE

def process_products(products):
    # Map: Convert MDL prices to EUR
    mapped_products = map(lambda p: {**p, 'price_eur': mdl_to_eur(p['price_mdl'])}, products)
    
    # Filter: Products within a certain price range in EUR
    filtered_products = list(filter(lambda p: 100 <= p['price_eur'] <= 700, mapped_products))
    
    # Reduce: Sum up the EUR prices of the filtered products
    total_price_eur = reduce(lambda acc, p: acc + p['price_eur'], filtered_products, 0)
    
    # UTC timestamp
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
    
    return {
        'filtered_products': filtered_products,
        'total_price_eur': total_price_eur,
        'timestamp': timestamp
    }

def serialize_to_json(products):
    json_string = "[\n"
    for i, product in enumerate(products):
        json_string += "  {\n"
        json_string += f'    "name": "{product["name"]}",\n'
        json_string += f'    "price_mdl": {product["price_mdl"]},\n'
        json_string += f'    "price_eur": {product["price_eur"]:.2f}\n'
        json_string += "  }"
        if i < len(products) - 1:
            json_string += ",\n"
        else:
            json_string += "\n"
    json_string += "]"
    print("\nSerialized to JSON:\n", json_string)

def serialize_to_xml(products):
    xml_string = "<products>\n"
    for product in products:
        xml_string += "  <product>\n"
        xml_string += f'    <name>{product["name"]}</name>\n'
        xml_string += f'    <price_mdl>{product["price_mdl"]}</price_mdl>\n'
        xml_string += f'    <price_eur>{product["price_eur"]:.2f}</price_eur>\n'
        xml_string += "  </product>\n"
    xml_string += "</products>"
    print("\nSerialized to XML:\n", xml_string)

def serialize_products(products):
    serialize_to_json(products)
    serialize_to_xml(products)

def custom_serialize(data):
    if isinstance(data, dict):
        serialized_data = "Dict:["
        for key, value in data.items():
            serialized_data += f"key:{custom_serialize(key)};value:{custom_serialize(value)};"
        serialized_data = serialized_data.rstrip(';') + "]"
        return serialized_data
    elif isinstance(data, list):
        serialized_data = "List:["
        for item in data:
            serialized_data += f"{custom_serialize(item)};;"
        serialized_data = serialized_data.rstrip(';;') + "]"
        return serialized_data
    elif isinstance(data, str):
        return f"str({data})"
    elif isinstance(data, int):
        return f"int({data})"
    elif isinstance(data, float):
        return f"float({data})"
    else:
        raise TypeError(f"Unsupported data type: {type(data)}")


def custom_deserialize(serialized_data):
    if serialized_data.startswith("Dict:["):
        serialized_data = serialized_data[6:-1]  
        items = serialized_data.split(";")
        deserialized_dict = {}
        i = 0
        while i < len(items):
            if items[i].startswith("key:"):
                key = custom_deserialize(items[i][4:])  
                i += 1
            if i < len(items) and items[i].startswith("value:"):
                value = custom_deserialize(items[i][6:]) 
                deserialized_dict[key] = value
                i += 1
        return deserialized_dict
    elif serialized_data.startswith("List:["):
        # Deserialize list
        serialized_data = serialized_data[6:-1]
        items = serialized_data.split(";;")
        deserialized_list = []
        for item in items:
            if item:
                deserialized_list.append(custom_deserialize(item))
        return deserialized_list
    elif serialized_data.startswith("str("):
        return serialized_data[4:-1]
    elif serialized_data.startswith("int("):
        return int(serialized_data[4:-1])
    elif serialized_data.startswith("float("):
        return float(serialized_data[6:-1])
    else:
        raise ValueError(f"Unrecognized format: {serialized_data}")


def custom_serialization_workflow(products):
    serialized_data = custom_serialize(products)
    print("\nSerialized Data (Custom Format):\n", serialized_data)

    deserialized_products = custom_deserialize(serialized_data)
    print("\nDeserialized Data (Back to Objects):")
    for product in deserialized_products:
        print(f"Name: {product['name']}, Price (MDL): {product['price_mdl']}, Price (EUR): {product['price_eur']:.2f}")

# Function to make a socket-based HTTP GET request
def get_http_response(host, port, request, use_ssl=False):
    if use_ssl:
        context = ssl.create_default_context()
        with socket.create_connection((host, port)) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                ssock.sendall(request.encode())
                response = b""
                while True:
                    chunk = ssock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            sock.sendall(request.encode())
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
    return response.decode(errors='ignore')

host = 'darwin.md'
port = 80  

request = f"GET /telefoane/smartphone HTTP/1.1\r\n" \
          f"Host: {host}\r\n" \
          f"Connection: close\r\n\r\n"

# Get the full HTTP response
http_response = get_http_response(host, port, request)
if "301 Moved Permanently" in http_response:
    # Extract the 'Location' header to get the new URL (HTTPS version)
    location_header = next(line for line in http_response.splitlines() if "Location:" in line)
    redirect_url = location_header.split(" ")[1]
    print(f"Redirected to: {redirect_url}")
    
    # Update to HTTPS request
    host = 'darwin.md'
    port = 443  # HTTPS port

    # Make the HTTPS request to the redirected URL
    request = f"GET /telefoane/smartphone HTTP/1.1\r\n" \
              f"Host: {host}\r\n" \
              f"Connection: close\r\n\r\n"
    http_response = get_http_response(host, port, request, use_ssl=True)

# Extract the HTTP body (everything after the first double newline)
http_body = http_response.split("\r\n\r\n", 1)[1]  # Split headers and body

# Pass the response body to BeautifulSoup for scraping
soup = BeautifulSoup(http_body, 'html.parser')

products = soup.find_all('div', class_='product-card bg-color-1c br-20 position-relative h-100 product-item')

print("\nPrinting all products found on the page:\n")
product_list = []
for product in products[:3]:
        name = product.find('div', class_='title-product fs-16 lh-19 mb-sm-2').text  
        name = name.strip()
        price_text = product.find('div', class_='price-new fw-600 fs-16 lh-19 align-self-end').text
        print(f"Product Name: {name}")
        try:
            price_mdl = int(price_text.replace(',', '').replace(' ', '').replace('lei', ''))
            print(f"Product Price (MDL): {price_mdl}")
        except ValueError:
            print(f"Invalid price format: {price_text}")
            price_mdl = 0

        product_list.append({
            'name': name,
            'price_mdl': price_mdl
        })

        product_link_tag = product.find('a', class_='d-block stretched-link text-white text-decoration-none') 
        product_link = product_link_tag['href'] if product_link_tag else "Link not found"
        print(f"Product Link: {product_link}")

        product_response = get_http_response(host, port, f"GET {product_link} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n", use_ssl=True)
        product_body = product_response.split("\r\n\r\n", 1)[1]
        product_soup = BeautifulSoup(product_body, 'html.parser')

        print("-------")

processed_result = process_products(product_list)
print(processed_result)

# RabbitMQ section 

def publish_to_rabbitmq(queue, message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=queue)

    channel.basic_publish(exchange='', routing_key=queue, body=json.dumps(message))

    print(f"Published message to RabbitMQ: {message}")
    connection.close()

publish_to_rabbitmq('product_queue', processed_result)
