from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    # Renderiza templates/index.html
    return render_template("index.html")


if __name__ == "__main__":
    # debug=True es opcional, ayuda a recargar solo
    app.run(debug=True)