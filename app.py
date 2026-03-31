from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup
import csv

app = Flask(__name__)

def scrape_products(base_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    product_links = []

    try:
        # 🔹 ONLY FIRST PAGE (FAST)
        url = base_url
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        for a in soup.find_all("a", href=True):
            link = a["href"]
            if "/product/" in link and link not in product_links:
                product_links.append(link)

    except Exception as e:
        print("Error:", e)

    all_products = []

    # 🔹 ONLY 5 PRODUCTS (SUPER FAST)
    for link in product_links[:5]:
        try:
            res = requests.get(link, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")

            title = soup.find("h1")
            price = soup.find("span", class_="price")

            all_products.append({
                "Title": title.text.strip() if title else "",
                "Price": price.text.strip() if price else "",
                "URL": link
            })

        except Exception as e:
            print("Product error:", e)

    if not all_products:
        return None

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
            return "❌ Failed to scrape."

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
