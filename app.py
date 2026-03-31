from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)

def scrape_products(base_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    product_links = []

    for page in range(1, 5):
        url = f"{base_url}/page/{page}/"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        for a in soup.find_all("a", href=True):
            link = a["href"]
            if "/product/" in link:
                product_links.append(link)

    all_products = []

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

        all_products.append({
            "Title": title,
            "Price": price,
            "URL": link
        })

    df = pd.DataFrame(all_products)
    file_path = "products.csv"
    df.to_csv(file_path, index=False)

    return file_path


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        file = scrape_products(url)
        return send_file(file, as_attachment=True)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
