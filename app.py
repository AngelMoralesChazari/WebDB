from flask import Flask, render_template, abort, request, redirect, url_for, flash, session, jsonify
from models import (
    obtener_peliculas,
    obtener_pelicula_aleatoria,
    obtener_peliculas_aleatorias,
    obtener_pelicula_por_id,
    registrar_usuario,
    obtener_usuario_por_email,
    buscar_peliculas,
    obtener_recomendadas_por_genero,
    contar_peliculas,
    crear_renta,                # <-- nuevo
    obtener_rentas_por_usuario,  # <-- nuevo
    tiene_renta_activa,
)
from werkzeug.security import generate_password_hash, check_password_hash
from models import eliminar_usuario, obtener_usuario_por_email

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

    # Guardar usuario en sesión (sin mensaje de bienvenida)
    session["usuario_id"] = usuario["id"]
    session["usuario_nombre"] = usuario["nombre"]

    return redirect(url_for("home"))

@app.route("/")
def home():
    pelicula_destacada = obtener_pelicula_aleatoria()
    tendencias = obtener_peliculas_aleatorias(limit=18)
    recomendadas = obtener_peliculas_aleatorias(limit=181)
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

    genero = pelicula.get("genero") or ""
    recomendadas = obtener_recomendadas_por_genero(
        genero=genero,
        movie_id_excluir=movie_id,
        limit=12
    )

    usuario_id = session.get("usuario_id")
    rentada = False
    if usuario_id:
        rentada = tiene_renta_activa(usuario_id, movie_id)

    return render_template(
        "detalle_pelicula.html",
        pelicula=pelicula,
        recomendadas=recomendadas,
        rentada=rentada
    )


@app.route("/peliculas")
def peliculas():
    # Parámetros de búsqueda y filtros
    q = request.args.get("q", "").strip()
    genero = request.args.get("genero", "").strip()
    anio = request.args.get("anio", "").strip()

    # Parámetro de paginación
    page = request.args.get("page", 1, type=int)
    per_page = 24  # Películas por página

    # Obtener películas con paginación
    peliculas = obtener_peliculas(
        busqueda=q if q else None,
        genero=genero if genero else None,
        anio=anio if anio else None,
        limit=per_page,
        offset=(page - 1) * per_page
    )

    # Obtener el total de películas para calcular páginas
    total_peliculas = contar_peliculas(
        busqueda=q if q else None,
        genero=genero if genero else None,
        anio=anio if anio else None
    )

    total_pages = (total_peliculas + per_page - 1) // per_page  # Redondeo hacia arriba

    return render_template(
        "Peliculas.html",
        peliculas=peliculas,
        q=q,
        genero_actual=genero,
        anio_actual=anio,
        page=page,
        total_pages=total_pages
    )

@app.route("/series")
def series():
    return render_template("series.html")

@app.route("/cuenta")
def cuenta():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Debes iniciar sesión para ver tu cuenta.")
        return redirect(url_for("login"))

    # Filtro desde query string: ?filtro=por_vencer, vencidas, devueltas
    filtro = request.args.get("filtro", "").strip() or None

    rentas = obtener_rentas_por_usuario(usuario_id, filtro=filtro)

    return render_template("cuenta.html", rentas=rentas, filtro_actual=filtro)

@app.route("/logout")
def logout():
    session.pop("usuario_id", None)
    session.pop("usuario_nombre", None)
    return redirect(url_for("home"))


# ==== NUEVAS RUTAS DE RENTAS ====

@app.route("/rentas")
def sistema_rentas():
    # Para no romper enlaces viejos, redirigimos a Mi cuenta
    return redirect(url_for("cuenta"))


@app.route("/rentar/<int:movie_id>", methods=["GET", "POST"])
def rentar_pelicula(movie_id):
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Debes iniciar sesión para rentar una película.")
        return redirect(url_for("login"))

    if request.method == "GET":
        # Mostrar formulario simple con días y monto fijos
        return render_template("rentar.html", movie_id=movie_id, dias=3, monto=50.00)

    # POST: procesar "pago simulado" y crear la renta
    dias = 3  # fijo
    monto = 50.00  # fijo

    ok = crear_renta(usuario_id=usuario_id, movie_id=movie_id, dias=dias, monto=monto)

    if not ok:
        flash("Ocurrió un error al crear la renta. Inténtalo más tarde.")
        return redirect(url_for("detalle_pelicula", movie_id=movie_id))

    flash("¡Renta creada correctamente!")
    return redirect(url_for("cuenta"))

# ==== API ====

@app.route("/api/pelicula/<int:movie_id>")
def api_pelicula(movie_id):
    """Devuelve JSON con los datos de la película y recomendadas"""
    pelicula = obtener_pelicula_por_id(movie_id)
    if not pelicula:
        return jsonify({"error": "Película no encontrada"}), 404

    genero = pelicula.get("genero") or ""
    recomendadas = obtener_recomendadas_por_genero(
        genero=genero,
        movie_id_excluir=movie_id,
        limit=12
    )

    return jsonify({
        "pelicula": pelicula,
        "recomendadas": recomendadas
    })

# ==== RUTAS PARA DEVOLVER/CANCELAR RENTA ====
@app.route("/renta/devolver/<int:renta_id>", methods=["POST"])
def devolver_renta(renta_id):
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Debes iniciar sesión para devolver una renta.")
        return redirect(url_for("login"))

    # Validar que la renta pertenece al usuario
    rentas = obtener_rentas_por_usuario(usuario_id)
    if not any(r.get("renta_id") == renta_id for r in rentas):
        flash("No tienes permiso para devolver esa renta.")
        return redirect(url_for("cuenta"))

    from models import actualizar_estado_renta
    ok = actualizar_estado_renta(renta_id, "Devuelta", usuario_id=usuario_id)
    if not ok:
        flash("No se pudo procesar la devolución. Inténtalo más tarde.")
    else:
        flash("Renta marcada como devuelta.")
    return redirect(url_for("cuenta"))


@app.route("/renta/cancelar/<int:renta_id>", methods=["POST"])
def cancelar_renta(renta_id):
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Debes iniciar sesión para cancelar una renta.")
        return redirect(url_for("login"))

    # Validar que la renta pertenece al usuario
    rentas = obtener_rentas_por_usuario(usuario_id)
    if not any(r.get("renta_id") == renta_id for r in rentas):
        flash("No tienes permiso para cancelar esa renta.")
        return redirect(url_for("cuenta"))

    from models import actualizar_estado_renta
    ok = actualizar_estado_renta(renta_id, "Cancelada", usuario_id=usuario_id)
    if not ok:
        flash("No se pudo cancelar la renta. Inténtalo más tarde.")
    else:
        flash("Renta cancelada.")
    return redirect(url_for("cuenta"))

@app.route("/admin/eliminar_usuario/<int:usuario_id>", methods=["POST"])
def admin_eliminar_usuario(usuario_id):
    # Comprobación mínima: solo permitir si el usuario es "admin" (aquí usamos usuario_id == 1 como ejemplo)
    usuario_actual = session.get("usuario_id")
    if not usuario_actual:
        flash("Debes iniciar sesión para realizar esta acción.")
        return redirect(url_for("login"))

    # Opción A (recomendada mínima): solo admin id=1 puede eliminar usuarios
    if usuario_actual != 1:
        flash("No autorizado. Solo el administrador puede eliminar usuarios.")
        return redirect(url_for("cuenta"))

    # Evitar eliminar al propio admin accidentalmente
    if usuario_id == usuario_actual:
        flash("No puedes eliminar tu propia cuenta desde el panel de admin.")
        return redirect(url_for("admin_users"))

    ok = eliminar_usuario(usuario_id)
    if ok:
        flash(f"Usuario {usuario_id} eliminado correctamente.")
    else:
        flash("No se pudo eliminar el usuario. Revisa los logs.")
    return redirect(url_for("admin_users"))

@app.route("/admin/usuarios")
def admin_users():
    usuario_actual = session.get("usuario_id")
    if not usuario_actual:
        flash("Debes iniciar sesión.")
        return redirect(url_for("login"))

    # Permiso mínimo (admin = id 1)
    if usuario_actual != 1:
        flash("No autorizado.")
        return redirect(url_for("cuenta"))

    # Obtener lista de usuarios (implementa una función en models.py o hacer consulta aquí)
    from db import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Usuario_ID, Nombre, Email, FechaRegistro
        FROM dbo.Usuarios
        ORDER BY FechaRegistro DESC;
    """)
    usuarios = []
    rows = cursor.fetchall()
    for row in rows:
        usuarios.append({
            "Usuario_ID": row.Usuario_ID,
            "Nombre": row.Nombre,
            "Email": row.Email,
            "FechaRegistro": row.FechaRegistro
        })
    conn.close()
    return render_template("admin_users.html", usuarios=usuarios)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)