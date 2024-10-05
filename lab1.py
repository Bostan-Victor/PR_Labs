import requests
from bs4 import BeautifulSoup

url = 'https://darwin.md/telefoane' 

response = requests.get(url)

if response.status_code == 200:
    # Task 1 (HTTP GET request)
    print("HTTP GET request successful!")
    # print("Response Status Code:", response.status_code)
    # print("Response Headers:", response.headers)
    # print("\nHTML Content/Body (First 500 characters):\n")
    # print(response.text[:500] + "...") 

    # Task 2 (Extract name and price)
    soup = BeautifulSoup(response.text, 'html.parser')

    products = soup.find_all('figure', class_='card card-product border-0')

    print("\nPrinting all products found on the page:\n")
    for index, product in enumerate(products):
        if index == 3:
            break

        name = product.find('a', class_='d-block mb-2 ga-item').text  
        name = name.strip()  # Validation: strip whitespace
        price_container = product.find('span', class_='price-new')
        price_text = price_container.find('b').text if price_container else "Price not found" 
        print(f"Product Name: {name}")
        # Validation: Ensure the price is an integer and remove non-numeric characters
        try:
            price = int(price_text.replace(',', '').replace(' ', '').replace('MDL', ''))
            print(f"Product Price: {price}")
        except ValueError:
            print(f"Invalid price format: {price_text}")
            price = "Invalid price"

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
else:
    print("Failed to retrieve the website. Status Code:", response.status_code)
