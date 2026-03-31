from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup
import csv
import time

app = Flask(__name__)

def scrape_products(base_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    product_links = []

    try:
        # 🔹 STEP 1: Collect product links (LIMITED to avoid timeout)
        for page in range(1, 3):  # only 2 pages
            url = f"{base_url}/page/{page}/"
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            for a in soup.find_all("a", href=True):
                link = a["href"]
                if "/product/" in link and link not in product_links:
                    product_links.append(link)

    except Exception as e:
        print("Error collecting links:", e)

    all_products = []

    # 🔹 STEP 2: Scrape each product (LIMITED)
    for link in product_links[:10]:  # max 10 products
        try:
            res = requests.get(link, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            title = soup.find("h1")
            price = soup.find("span", class_="price")
            description = soup.find("div", class_="woocommerce-product-details__short-description")

            # 🔹 images
            images = []
            for img in soup.find_all("img"):
                src = img.get("src")
                if src and "product" in src:
                    images.append(src)

            all_products.append({
                "Title": title.text.strip() if title else "",
                "Price": price.text.strip() if price else "",
                "Description": description.text.strip() if description else "",
                "URL": link,
                "Images": ", ".join(images)
            })

            time.sleep(0.5)

        except Exception as e:
            print("Error scraping product:", e)

    # 🔹 STEP 3: Safety check
    if not all_products:
        return None

    # 🔹 STEP 4: Save CSV
    file_path = "products.csv"

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=all_products[0].keys())
        writer.writeheader()
        writer.writerows(all_products)

    return file_path


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        file = scrape_products(url)

        if file:
            return send_file(file, as_attachment=True)
        else:
            return "❌ Error: Could not scrape data. Check URL."

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
