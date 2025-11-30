from flask import Flask, render_template, abort, request, redirect, url_for, flash, session
from models import (
    obtener_peliculas,
    obtener_pelicula_aleatoria,
    obtener_peliculas_aleatorias,
    obtener_pelicula_por_id,
    registrar_usuario,
    obtener_usuario_por_email,
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "test"


@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/registro", methods=["POST"])
def registro():
    nombre = request.form.get("nombre")
    email = request.form.get("email")
    password = request.form.get("password")

    if not nombre or not email or not password:
        flash("Todos los campos son obligatorios.")
        return redirect(url_for("login"))

    usuario_existente = obtener_usuario_por_email(email)
    if usuario_existente:
        flash("Ese correo ya está registrado.")
        return redirect(url_for("login"))

    password_hash = generate_password_hash(password)

    exito = registrar_usuario(nombre, email, password_hash)
    if not exito:
        flash("Ocurrió un error al registrar el usuario.")
        return redirect(url_for("login"))

    flash("Registro exitoso, ahora puedes iniciar sesión.")
    return redirect(url_for("login"))


@app.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        flash("Debes ingresar correo y contraseña.")
        return redirect(url_for("login"))

    usuario = obtener_usuario_por_email(email)
    if not usuario:
        flash("Correo o contraseña incorrectos.")
        return redirect(url_for("login"))

    if not check_password_hash(usuario["password_hash"], password):
        flash("Correo o contraseña incorrectos.")
        return redirect(url_for("login"))

    session["usuario_id"] = usuario["id"]
    session["usuario_nombre"] = usuario["nombre"]

    flash(f"Bienvenido, {usuario['nombre']} (aún sin sesión persistente).")
    return redirect(url_for("home"))


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

@app.route("/logout")
def logout():
    session.pop("usuario_id", None)
    session.pop("usuario_nombre", None)
    flash("Has cerrado sesión correctamente.")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)