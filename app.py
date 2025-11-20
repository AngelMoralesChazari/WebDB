from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    # Renderiza templates/index.html
    return render_template("index.html")

@app.route("/peliculas")
def peliculas():
    return render_template("peliculas.html")

@app.route("/series")
def series():
    return render_template("series.html")

@app.route("/cuenta")
def cuenta():
    return render_template("cuenta.html")

from db import get_connection

conn = get_connection()
if conn:
    print("✅ Conexión exitosa a SQL Server")
    conn.close()
else:
    print("❌ No se pudo conectar")

if __name__ == "__main__":
    # debug=True es opcional, ayuda a recargar solo
    app.run(debug=True)