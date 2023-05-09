from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index_rt():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context="adhoc")