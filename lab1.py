import requests
from bs4 import BeautifulSoup

url = 'https://darwin.md/telefoane' 

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
    for product in products:
        name = product.find('a', class_='d-block mb-2 ga-item').text  
        price_container = product.find('span', class_='price-new')
        price = price_container.find('b').text if price_container else "Price not found" 
        print(f"Product Name: {name}")
        print(f"Product Price: {price}")
        print("-------")
else:
    print("Failed to retrieve the website. Status Code:", response.status_code)
