from flask import Flask, render_template, abort
from models import (
    obtener_peliculas,
    obtener_pelicula_aleatoria,
    obtener_peliculas_aleatorias,
    obtener_pelicula_por_id,
)

app = Flask(__name__)


@app.route("/")
def home():
    pelicula_destacada = obtener_pelicula_aleatoria()
    tendencias = obtener_peliculas_aleatorias(limit=14)
    recomendadas = obtener_peliculas_aleatorias(limit=14)
    return render_template(
        "index.html",
        destacada=pelicula_destacada,
        tendencias=tendencias,
        recomendadas=recomendadas,
    )


@app.route("/pelicula/<int:movie_id>")
def detalle_pelicula(movie_id):
    pelicula = obtener_pelicula_por_id(movie_id)
    if not pelicula:
        abort(404)
    return render_template("detalle_pelicula.html", pelicula=pelicula)


@app.route("/peliculas")
def peliculas():
    print(">>> Entrando a la ruta /peliculas")
    lista_peliculas = obtener_peliculas(limit=20)
    print(">>> En vista /peliculas, len(lista_peliculas) =", len(lista_peliculas))
    return render_template("peliculas.html", peliculas=lista_peliculas)


@app.route("/series")
def series():
    return render_template("series.html")


@app.route("/cuenta")
def cuenta():
    return render_template("cuenta.html")


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)