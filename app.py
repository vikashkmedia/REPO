from flask import Flask, render_template, request, send_file
import csv

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # 🔹 Create instant dummy CSV (NO scraping)
        file_path = "products.csv"

        data = [
            {"Title": "Test Product 1", "Price": "₹100"},
            {"Title": "Test Product 2", "Price": "₹200"}
        ]

        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        return send_file(file_path, as_attachment=True)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
