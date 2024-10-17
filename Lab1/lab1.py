import requests
from bs4 import BeautifulSoup
from functools import reduce
from datetime import datetime, timezone

url = 'https://darwin.md/telefoane' 

MDL_TO_EUR_RATE = 19.5
EUR_TO_MDL_RATE = 1 / MDL_TO_EUR_RATE


def mdl_to_eur(price_mdl):
    return price_mdl / MDL_TO_EUR_RATE


def process_products(products):
    # Map: Convert MDL prices to EUR
    mapped_products = map(lambda p: {**p, 'price_eur': mdl_to_eur(p['price_mdl'])}, products)
    
    # Filter: Products within a certain price range in EUR
    filtered_products = list(filter(lambda p: 100 <= p['price_eur'] <= 500, mapped_products))
    
    # Reduce: Sum up the EUR prices of the filtered products
    total_price_eur = reduce(lambda acc, p: acc + p['price_eur'], filtered_products, 0)
    
    # Attach UTC timestamp
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
    
    return {
        'filtered_products': filtered_products,
        'total_price_eur': total_price_eur,
        'timestamp': timestamp
    }


response = requests.get(url)

if response.status_code == 200:
    # Task 1 (HTTP GET request)
    print("HTTP GET request successful!")
    print("Response Status Code:", response.status_code)
    print("Response Headers:", response.headers)
    print("\nHTML Content/Body (First 500 characters):\n")
    print(response.text[:500] + "...") 

    # Task 2 (Extract name and price)
    soup = BeautifulSoup(response.text, 'html.parser')

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

        product_response = requests.get(product_link)

        if product_response.status_code == 200:
            product_soup = BeautifulSoup(product_response.text, 'html.parser')

            specs_list_tag = product_soup.find('ul', class_='features')
            specs_list = specs_list_tag.find_all('li', class_='char_all')
            specs = [spec.text.strip() for spec in specs_list]  # Validation: strip any extra whitespaces from specs
            print("Device specs:")
            for spec in specs:
                print(spec)
        else:
            print(f"Failed to retrieve the product page. Status Code: {product_response.status_code}\n")
        print("-------")

    # Task 5: Process products using Map/Filter/Reduce
    processed_result = process_products(product_list)

    print("\nFiltered Products (within EUR range 100-500):")
    for product in processed_result['filtered_products']:
        print(f"Name: {product['name']}, Price in EUR: {product['price_eur']:.2f} EUR")
    
    print(f"\nTotal Price of Filtered Products: {processed_result['total_price_eur']:.2f} EUR")
    print(f"Timestamp: {processed_result['timestamp']}")
else:
    print("Failed to retrieve the website. Status Code:", response.status_code)
