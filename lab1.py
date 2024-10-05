import requests

url = 'https://darwin.md/' 

response = requests.get(url)

if response.status_code == 200:
    print("HTTP GET request successful!")
    print("Response Status Code:", response.status_code)
    print("Response Headers:", response.headers)
    print("\nHTML Content/Body (First 500 characters):\n")
    print(response.text[:500] + "...")  
else:
    print("Failed to retrieve the website. Status Code:", response.status_code)
