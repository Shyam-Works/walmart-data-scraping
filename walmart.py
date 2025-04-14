from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import json
import urllib.parse
walmart_url = "https://www.walmart.com/ip/CRUA-34-144Hz-Ultrawide-Curved-Gaming-Monitor-WQHD-3440-1440P-21-9-1500R-Computer-Monitor-1ms-GTG-Adaptive-Sync-99-SRGB-DP-HDMI-Port-Black/2345013784?classType=VARIANT&adsRedirect=true"


HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9,en-CA;q=0.8,en-IN;q=0.7",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36 Edg/135.0.0.0"
}

def get_product_links(query, page_number=1):
    search_url = f"https://www.walmart.com/search/?query={query}&page={page_number}"
    response = requests.get(search_url, headers=HEADERS)

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all("a", href=True)

    product_links = []
    for link in links:
        href = link['href']

        # Walmart tracking links with embedded real URL
        if "/sp/track" in href and "rd=" in href:
            parsed_url = urllib.parse.urlparse(href)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            if "rd" in query_params:
                real_url = urllib.parse.unquote(query_params["rd"][0])
                product_links.append(real_url)
        elif '/ip/' in href:
            # Direct product link
            if href.startswith('https'):
                product_links.append(href)
            else:
                product_links.append("https://www.walmart.com" + href)

    return product_links

def extract_product_info(product_url):
    response = requests.get(product_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    script_tag = soup.find("script", id="__NEXT_DATA__")
    data = json.loads(script_tag.string)

    product_info = {
        "product_name": data['props']['pageProps']['initialData']['data']['product']['name'],
        "brand": data['props']['pageProps']['initialData']['data']['product']['brand'],
        "price": data['props']['pageProps']['initialData']['data']['product']['priceInfo']['currentPrice']['price'],
        "availability": data['props']['pageProps']['initialData']['data']['product']['availabilityStatus'],
        "image_url": data['props']['pageProps']['initialData']['data']['product']['imageInfo']['thumbnailUrl'],
        "short_description": data['props']['pageProps']['initialData']['data']['product']["shortDescription"],
        "avg_review": data['props']['pageProps']['initialData']['data']["reviews"]["averageOverallRating"],
        "total_review": data['props']['pageProps']['initialData']["data"]["reviews"]["totalReviewCount"]
    }
    return product_info


def main():
    OUTPUT_FILE = "product_info2.jsonl"
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

        page_number = 1
        while True:
            links = get_product_links("monitor", page_number)
            if not links or page_number > 10:
                break
            for link in links:
                print(link)
                try:
                    
                    product_info2 = extract_product_info(link)
                    if product_info2:
                        file.write(json.dumps(product_info2) + "\n")
                except Exception as e:
                    print(f"Error extracting data from {link}: {e}")
            page_number += 1
            print(f"search page {page_number}")
    
if __name__ == "__main__":
    main()































# response = requests.get(walmart_url, headers=HEADERS)

# soup = bs(response.text, 'html.parser')

# script_tag = soup.find("script", id="__NEXT_DATA__")
# data = json.loads(script_tag.string)

# product_info = {
#     "product_name": data['props']['pageProps']['initialData']['data']['product']['name'],
#     "brand": data['props']['pageProps']['initialData']['data']['product']['brand'],
#     "price": data['props']['pageProps']['initialData']['data']['product']['priceInfo']['currentPrice']['price'],
#     "availability": data['props']['pageProps']['initialData']['data']['product']['availabilityStatus'],
#     "image_url": data['props']['pageProps']['initialData']['data']['product']['imageInfo']['thumbnailUrl'],
#     "short_description": data['props']['pageProps']['initialData']['data']['product']["shortDescription"],
#     "avg_review": data['props']['pageProps']['initialData']['data']["reviews"]["averageOverallRating"],
#     "total_review": data['props']['pageProps']['initialData']["data"]["reviews"]["totalReviewCount"]
# }
# # avg_review = data['props']['pageProps']['initialData']['data']['reviews']['averageOverallRating']
# # price = data['props']['pageProps']['initialData']['data']['product']['priceInfo']['currentPrice']['price']
# # total_review = data['props']['pageProps']['initialData']['data']['reviews']['totalReviewCount']
# # product_name = data['props']['pageProps']['initialData']['data']['product']['name']
# # brand = data['props']['pageProps']['initialData']['data']['product']['brand']
# # availability = data['props']['pageProps']['initialData']['data']['product']['availabilityStatus']
# # image_url = data['props']['pageProps']['initialData']['data']['product']['imageInfo']['thumbnailUrl']
# # short_description = data['props']['pageProps']['initialData']['data']['product']['shortDescription']
