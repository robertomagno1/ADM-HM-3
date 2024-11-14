import requests
import os
import csv
from bs4 import BeautifulSoup
import pandas as pd

def restaurant_list_txt(base_url, output_path):
    restaurant_urls = []
    for page in range(1, 101):  # Cambia il numero massimo di pagine se necessario
        page_url = f"{base_url}/page/{page}" if page > 1 else base_url
        response = requests.get(page_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True, class_='link')
            for link in links:
                href = link['href']
                if '/restaurant/' in href:
                    full_url = "https://guide.michelin.com" + href
                    restaurant_urls.append(full_url)
        else:
            print(f"Failed to retrieve page {page}")

    with open(output_path, 'w') as file:
        for url in restaurant_urls:
            file.write(url + '\n')

    print(f"Found {len(restaurant_urls)} restaurant URLs")


def Crawler(input_file_path, output_path):
    os.makedirs(output_path, exist_ok=True)

    with open(input_file_path, 'r') as file:
        restaurant_urls = file.readlines()

    if not restaurant_urls:
        print("No URLs found in the input file.")
        return

    for index, url in enumerate(restaurant_urls):
        url = url.strip()
        page_number = (index // 20) + 1
        folder_name = f"page_{page_number}"
        folder_path = os.path.join(output_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        try:
            response = requests.get(url)
            if response.status_code == 200:
                file_name = f"restaurant_{index + 1}.html"
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'w', encoding='utf-8') as html_file:
                    html_file.write(response.text)
            else:
                print(f"Failed to download {url} (Status code: {response.status_code})")
        except Exception as e:
            print(f"Error downloading {url}: {e}")

    print("Download completed!")


def parse_restaurant_html(file_path, index):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Index
    index = index

    # Restaurant Name
    restaurant_name = soup.find("h1", {"class": "data-sheet__title"}).get_text(strip=True) if soup.find("h1", {"class": "data-sheet__title"}) else ""

    # Address, City, Postal Code, Country
    divs = soup.find_all("div", {"class": "data-sheet__block--text"})
    address, city, postalCode, country = "", "", "", ""
    if divs:
        text = divs[0].get_text(strip=True)
        parts = text.split(",")
        if len(parts) >= 4:
            address, city, postalCode, country = parts[0], parts[1], parts[2], parts[3]

    # Price Range and Cuisine Type
    price_range, cuisine_type = "", ""
    if len(divs) > 1:
        details = divs[1].get_text(strip=True).split("·")
        if details:
            price_range = details[0].strip()
            cuisine_type = ", ".join([detail.strip() for detail in details[1:]])

    # Description
    description = soup.find("div", {"class": "data-sheet__description"}).get_text(strip=True) if soup.find("div", {"class": "data-sheet__description"}) else ""

    # Facilities and Services
    facilities_services = []
    facilities_div = soup.find("div", {"class": "col col-12 col-lg-6"})
    if facilities_div:
        facilities_services = [li.get_text(strip=True) for li in facilities_div.find_all("li")]

    # Credit Cards
    credit_cards = []
    cards_div = soup.find("div", {"class": "list--card"})
    if cards_div:
        img_elements = cards_div.find_all("img", {"class": "lazy"})
        credit_cards = [img['data-src'].split('/')[-1].split('-')[0].capitalize() for img in img_elements if 'data-src' in img.attrs]

    # Phone Number
    phone_number = ""
    phone_div = soup.find("div", {"class": "d-flex"})
    if phone_div:
        phone_number = phone_div.find("span", {"class": "flex-fill"}).get_text(strip=True) if phone_div.find("span", {"class": "flex-fill"}) else ""

    # Website
    website = ""
    website_div = soup.find("div", {"class": "collapse__block-item link-item"})
    if website_div:
        website_link = website_div.find("a")
        website = website_link['href'] if website_link else ""

    # Return data as a dictionary
    return {
        "index": index,
        "restaurantName": restaurant_name,
        "address": address,
        "city": city,
        "postalCode": postalCode,
        "country": country,
        "priceRange": price_range,
        "cuisineType": cuisine_type,
        "description": description,
        "facilitiesServices": "; ".join(facilities_services),  # Join list items with a semicolon
        "creditCards": "; ".join(credit_cards),  # Join list items with a semicolon
        "phoneNumber": phone_number,
        "website": website
    }



def Parser(input_path, output_path):
    os.makedirs(output_path, exist_ok=True)
    file_index = 1

    for root, dirs, files in os.walk(input_path):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                restaurant_data = parse_restaurant_html(file_path, file_index)
                tsv_file_name = f"restaurant_{file_index}.tsv"
                tsv_file_path = os.path.join(output_path, tsv_file_name)
                with open(tsv_file_path, 'w', newline='', encoding='utf-8') as tsv_file:
                    writer = csv.DictWriter(tsv_file, fieldnames=restaurant_data.keys(), delimiter='\t')
                    writer.writeheader()
                    writer.writerow(restaurant_data)
                file_index += 1

    print("Parsing and TSV file creation completed!")


def merge_tsv_to_csv(input_folder, output_file):
    all_data = pd.DataFrame()

    for file in os.listdir(input_folder):
        if file.endswith(".tsv"):
            file_path = os.path.join(input_folder, file)
            df = pd.read_csv(file_path, sep='\t')
            all_data = pd.concat([all_data, df], ignore_index=True)

    all_data.to_csv(output_file, index=False)
    print("CSV file created!")