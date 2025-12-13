from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    idols = [
        {"name": "BTS", "group": "방탄소년단"},
        {"name": "BLACKPINK", "group": "블랙핑크"},
        {"name": "EXO", "group": "엑소"},
        {"name": "IVE", "group": "아이브"},
        {"name": "NewJeans", "group": "뉴진스"},
    ]
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
