import socket
import ssl
from bs4 import BeautifulSoup
from functools import reduce
from datetime import datetime, timezone

MDL_TO_EUR_RATE = 19.5  
EUR_TO_MDL_RATE = 1 / MDL_TO_EUR_RATE  

# Conversion function from MDL to EUR
def mdl_to_eur(price_mdl):
    return price_mdl / MDL_TO_EUR_RATE

# Function to process products using Map/Filter/Reduce
def process_products(products):
    # Map: Convert MDL prices to EUR
    mapped_products = map(lambda p: {**p, 'price_eur': mdl_to_eur(p['price_mdl'])}, products)
    
    # Filter: Products within a certain price range in EUR
    filtered_products = list(filter(lambda p: 100 <= p['price_eur'] <= 500, mapped_products))
    
    # Reduce: Sum up the EUR prices of the filtered products
    total_price_eur = reduce(lambda acc, p: acc + p['price_eur'], filtered_products, 0)
    
    # UTC timestamp
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
    
    # Return the filtered products, total price, and timestamp
    return {
        'filtered_products': filtered_products,
        'total_price_eur': total_price_eur,
        'timestamp': timestamp
    }

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

request = f"GET /telefoane HTTP/1.1\r\n" \
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
    request = f"GET /telefoane HTTP/1.1\r\n" \
              f"Host: {host}\r\n" \
              f"Connection: close\r\n\r\n"
    http_response = get_http_response(host, port, request, use_ssl=True)

# Extract the HTTP body (everything after the first double newline)
http_body = http_response.split("\r\n\r\n", 1)[1]  # Split headers and body

# Pass the response body to BeautifulSoup for scraping
soup = BeautifulSoup(http_body, 'html.parser')

products = soup.find_all('figure', class_='card card-product border-0')

print("\nPrinting all products found on the page:\n")
product_list = []
for product in products[:3]:
        name = product.find('a', class_='d-block mb-2 ga-item').text  
        name = name.strip()  # Validation: strip whitespace
        price_container = product.find('span', class_='price-new')
        price_text = price_container.find('b').text if price_container else "Price not found" 
        print(f"Product Name: {name}")
        # Validation: Ensure the price is an integer and remove non-numeric characters
        try:
            price_mdl = int(price_text.replace(',', '').replace(' ', '').replace('MDL', ''))
            print(f"Product Price (MDL): {price_mdl}")
        except ValueError:
            print(f"Invalid price format: {price_text}")
            price_mdl = 0

        product_list.append({
            'name': name,
            'price_mdl': price_mdl
        })

        # Task 3 (Extract product link and something from product page)
        product_link_tag = product.find('a', class_='d-block mb-2 ga-item') 
        product_link = product_link_tag['href'] if product_link_tag else "Link not found"
        print(f"Product Link: {product_link}")

        product_response = get_http_response(host, port, f"GET {product_link} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n", use_ssl=True)
        product_body = product_response.split("\r\n\r\n", 1)[1]
        product_soup = BeautifulSoup(product_body, 'html.parser')

        specs_list_tag = product_soup.find('ul', class_='features')
        specs_list = specs_list_tag.find_all('li', class_='char_all') if specs_list_tag else []
        specs = [spec.text.strip() for spec in specs_list]  # Validation: strip any extra whitespaces from specs
        print("Device specs:")
        for spec in specs:
            print(spec)

        print("-------")

# Task 5: Process products using Map/Filter/Reduce
processed_result = process_products(product_list)

print("\nFiltered Products (within EUR range 100-500):")
for product in processed_result['filtered_products']:
    print(f"Name: {product['name']}, Price in EUR: {product['price_eur']:.2f} EUR")

print(f"\nTotal Price of Filtered Products: {processed_result['total_price_eur']:.2f} EUR")
print(f"Timestamp: {processed_result['timestamp']}")