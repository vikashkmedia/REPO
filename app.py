from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup
import csv

app = Flask(__name__)

def scrape_products(base_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    product_links = []

    # 🔹 Collect product links (4 pages)
    for page in range(1, 5):
        url = f"{base_url}/page/{page}/"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        for a in soup.find_all("a", href=True):
            link = a["href"]
            if "/product/" in link:
                if link not in product_links:
                    product_links.append(link)

    all_products = []

    # 🔹 Scrape each product
    for link in product_links:
        res = requests.get(link, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        try:
            title = soup.find("h1").text.strip()
        except:
            title = ""

        try:
            price = soup.find("span", class_="price").text.strip()
        except:
            price = ""

        try:
            description = soup.find("div", class_="woocommerce-product-details__short-description").text.strip()
        except:
            description = ""

        images = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if src and "product" in src:
                images.append(src)

        all_products.append({
            "Title": title,
            "Price": price,
            "Description": description,
            "URL": link,
            "Images": ", ".join(images)
        })

    # 🔹 Save CSV (no pandas)
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
        return send_file(file, as_attachment=True)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
