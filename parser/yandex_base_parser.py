import requests
from bs4 import BeautifulSoup

url = 'https://yandex.com/maps/org/betulla/228633125544/'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    restaurant_name = soup.find('h1', class_='orgpage-header-view__header')  # Use the appropriate class or tag for the restaurant's name
    if restaurant_name:
        print(f"Restaurant Name: {restaurant_name.get_text()}")

    address = soup.find('a', class_='orgpage-header-view__address')  # Adjust to match the correct tag and class for address
    if address:
        print(f"Address: {address.get_text()}")

    rating = soup.find('div', class_='business-rating-badge-view__rating')  # Find the correct tag/class for the rating
    if rating:
        print(f"Rating: {rating.get_text()}")
        
    reviews = soup.find_all('div', class_='business-review-view__body-text _collapsed')  # Find the correct tag/class for the reviews
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")