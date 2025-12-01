from flask import (
    Flask,
    render_template,
    abort,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Importa las funciones necesarias desde models.py (asegúrate de haberlas añadido a models.py)
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
    crear_renta,
    obtener_rentas_por_usuario,
    tiene_renta_activa,
    eliminar_usuario,
    # Funciones de tarjetas (asegúrate de tenerlas en models.py)
    guardar_tarjeta,
    obtener_tarjetas_por_usuario,
    obtener_tarjeta_por_id,
    eliminar_tarjeta as eliminar_tarjeta_model,
    tiene_tarjeta,
)

# Si models.py no contiene alguna función, el import fallará: añade las funciones en models.py antes.

app = Flask(__name__)
app.secret_key = "test"  # Cambia en producción


# ---------------------
# Login (GET) - filtrar flashes no relacionados con login
# ---------------------
@app.route("/login", methods=["GET"])
def login():
    # Filtrar mensajes flash para mostrar solo los relacionados con login en esta vista.
    # Flask guarda flashes en session['_flashes'] como lista de (category, message).
    flashes = session.get("_flashes", [])
    mensajes_a_mantener = []
    for category, message in flashes:
        msg_lower = (message or "").lower()
        # Palabras clave relacionadas con login/registro que queremos mantener
        if any(
            kw in msg_lower
            for kw in [
                "correo",
                "contraseña",
                "obligatorio",
                "registr",
                "sesión",
                "error",
                "credencial",
            ]
        ):
            mensajes_a_mantener.append((category, message))
    # Sobrescribir los flashes con los filtrados
    session["_flashes"] = mensajes_a_mantener
    return render_template("login.html")


# ---------------------
# Registro
# ---------------------
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


# ---------------------
# Login (POST) - flujo normal usando BD y redirección a admin si id == 1
# ---------------------
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

    # Guardar usuario en sesión
    # Aseguramos que sea entero al guardar
    try:
        usuario_id = int(usuario["id"])
    except Exception:
        usuario_id = usuario["id"]
    session["usuario_id"] = usuario_id
    session["usuario_nombre"] = usuario["nombre"]

    # Si es admin (id == 1), redirigir al panel admin
    try:
        if int(usuario_id) == 1:
            flash("Has iniciado sesión como administrador.")
            return redirect(url_for("admin_users"))
    except Exception:
        pass

    return redirect(url_for("home"))


# ---------------------
# Logout
# ---------------------
@app.route("/logout")
def logout():
    session.pop("usuario_id", None)
    session.pop("usuario_nombre", None)
    return redirect(url_for("home"))


# ---------------------
# Home / Index
# ---------------------
@app.route("/")
def home():
    pelicula_destacada = obtener_pelicula_aleatoria()
    tendencias = obtener_peliculas_aleatorias(limit=18)
    recomendadas = obtener_peliculas_aleatorias(limit=18)
    return render_template(
        "index.html",
        destacada=pelicula_destacada,
        tendencias=tendencias,
        recomendadas=recomendadas,
    )


# ---------------------
# Películas (listado con paginación y filtros)
# ---------------------
@app.route("/peliculas")
def peliculas():
    q = request.args.get("q", "").strip()
    genero = request.args.get("genero", "").strip()
    anio = request.args.get("anio", "").strip()

    page = request.args.get("page", 1, type=int)
    per_page = 24

    peliculas_list = obtener_peliculas(
        busqueda=q if q else None,
        genero=genero if genero else None,
        anio=anio if anio else None,
        limit=per_page,
        offset=(page - 1) * per_page,
    )

    total_peliculas = contar_peliculas(
        busqueda=q if q else None, genero=genero if genero else None, anio=anio if anio else None
    )

    total_pages = (total_peliculas + per_page - 1) // per_page

    return render_template(
        "Peliculas.html",
        peliculas=peliculas_list,
        q=q,
        genero_actual=genero,
        anio_actual=anio,
        page=page,
        total_pages=total_pages,
    )


# ---------------------
# Series (placeholder)
# ---------------------
@app.route("/series")
def series():
    return render_template("series.html")


# ---------------------
# Detalle de película
# ---------------------
@app.route("/pelicula/<int:movie_id>")
def detalle_pelicula(movie_id):
    pelicula = obtener_pelicula_por_id(movie_id)
    if not pelicula:
        abort(404)

    genero = pelicula.get("genero") or ""
    recomendadas = obtener_recomendadas_por_genero(genero=genero, movie_id_excluir=movie_id, limit=12)

    usuario_id = session.get("usuario_id")
    rentada = False
    if usuario_id:
        rentada = tiene_renta_activa(usuario_id, movie_id)

    return render_template("detalle_pelicula.html", pelicula=pelicula, recomendadas=recomendadas, rentada=rentada)


# ---------------------
# Cuenta (mis rentas)
# ---------------------
@app.route("/cuenta")
def cuenta():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Debes iniciar sesión para ver tu cuenta.")
        return redirect(url_for("login"))

    filtro = request.args.get("filtro", "").strip() or None
    rentas = obtener_rentas_por_usuario(usuario_id, filtro=filtro)
    tarjetas = obtener_tarjetas_por_usuario(usuario_id)
    return render_template("cuenta.html", rentas=rentas, filtro_actual=filtro, tarjetas=tarjetas)


# ---------------------
# Rutas de rentas: rentar / devolver / cancelar
# ---------------------
@app.route("/rentas")
def sistema_rentas():
    return redirect(url_for("cuenta"))


@app.route("/rentar/<int:movie_id>", methods=["GET", "POST"])
def rentar_pelicula(movie_id):
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Debes iniciar sesión para rentar una película.")
        return redirect(url_for("login"))

    if request.method == "GET":
        # AGREGAR: Obtener información de la película
        pelicula = obtener_pelicula_por_id(movie_id)
        if not pelicula:
            flash("Película no encontrada.")
            return redirect(url_for("peliculas"))

        tarjetas = obtener_tarjetas_por_usuario(usuario_id)
        if not tarjetas or len(tarjetas) == 0:
            flash("Necesitas registrar una tarjeta antes de rentar.")
            return redirect(url_for("tarjeta_agregar", next=url_for("rentar_pelicula", movie_id=movie_id)))

        # MODIFICAR: Pasar poster_url al template
        return render_template("rentar.html", movie_id=movie_id, tarjetas=tarjetas, dias=3, monto=50.00,
                               poster_url=pelicula.get('poster'))

    # POST
    tarjeta_id = request.form.get("tarjeta_id")
    if not tarjeta_id:
        flash("Selecciona una tarjeta para pagar.")
        return redirect(url_for("rentar_pelicula", movie_id=movie_id))

    try:
        tarjeta_id_int = int(tarjeta_id)
    except Exception:
        flash("Tarjeta inválida.")
        return redirect(url_for("rentar_pelicula", movie_id=movie_id))

    tarjeta = obtener_tarjeta_por_id(tarjeta_id_int)
    if not tarjeta or tarjeta.get("usuario_id") != usuario_id:
        flash("Tarjeta inválida.")
        return redirect(url_for("rentar_pelicula", movie_id=movie_id))

    now = datetime.now()
    if tarjeta.get("expiry_year") < now.year or (tarjeta.get("expiry_year") == now.year and tarjeta.get("expiry_month") < now.month):
        flash("La tarjeta seleccionada está vencida.")
        return redirect(url_for("rentar_pelicula", movie_id=movie_id))

    dias = 3
    monto = 50.00

    ok, renta_id = crear_renta(usuario_id=usuario_id, movie_id=movie_id, dias=dias, monto=monto)
    if not ok:
        flash("Ocurrió un error al crear la renta. Inténtalo más tarde.")
        return redirect(url_for("detalle_pelicula", movie_id=movie_id))

    flash("¡Renta creada correctamente!")
    return redirect(url_for("cuenta"))


@app.route("/renta/devolver/<int:renta_id>", methods=["POST"])
def devolver_renta(renta_id):
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Debes iniciar sesión para devolver una renta.")
        return redirect(url_for("login"))

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


# ---------------------
# Tarjetas: agregar / eliminar
# ---------------------
@app.route("/tarjeta/agregar", methods=["GET", "POST"])
def tarjeta_agregar():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Debes iniciar sesión para agregar una tarjeta.")
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("tarjeta_agregar.html", next=request.args.get("next"))

    # POST: procesar datos de la tarjeta (simulación)
    titular = request.form.get("titular", "").strip()
    numero = request.form.get("numero", "").replace(" ", "")
    expiry = request.form.get("expiry", "").strip()  # formato MM/YY
    cvv = request.form.get("cvv", "").strip()
    guardar = True if request.form.get("guardar") == "on" else False

    if not titular or not numero or not expiry or not cvv:
        flash("Todos los campos de la tarjeta son obligatorios.")
        return redirect(url_for("tarjeta_agregar", next=request.args.get("next")))

    # Parse expiry
    try:
        if "/" in expiry:
            parts = expiry.split("/")
            month = int(parts[0])
            year = int(parts[1])
            if year < 100:
                year += 2000
        else:
            flash("Formato de expiración inválido. Usa MM/YY.")
            return redirect(url_for("tarjeta_agregar", next=request.args.get("next")))
    except Exception:
        flash("Formato de expiración inválido. Usa MM/YY.")
        return redirect(url_for("tarjeta_agregar", next=request.args.get("next")))

    # No almacenamos CVV por seguridad (simulación)
    ok, new_id = guardar_tarjeta(usuario_id, titular, numero, month, year, guardar=guardar)
    if not ok:
        flash("No se pudo guardar la tarjeta. Inténtalo más tarde.")
        return redirect(url_for("tarjeta_agregar", next=request.args.get("next")))

    flash("Tarjeta registrada correctamente.")
    next_url = request.args.get("next")
    if next_url:
        return redirect(next_url)
    return redirect(url_for("cuenta"))


@app.route("/tarjeta/eliminar/<int:tarjeta_id>", methods=["POST"])
def tarjeta_eliminar(tarjeta_id):
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Debes iniciar sesión.")
        return redirect(url_for("login"))

    ok = eliminar_tarjeta_model(tarjeta_id, usuario_id=usuario_id)
    if ok:
        flash("Tarjeta eliminada.")
    else:
        flash("No fue posible eliminar la tarjeta.")
    return redirect(url_for("cuenta"))


# ---------------------
# API: pelicula
# ---------------------
@app.route("/api/pelicula/<int:movie_id>")
def api_pelicula(movie_id):
    pelicula = obtener_pelicula_por_id(movie_id)
    if not pelicula:
        return jsonify({"error": "Película no encontrada"}), 404

    genero = pelicula.get("genero") or ""
    recomendadas = obtener_recomendadas_por_genero(genero=genero, movie_id_excluir=movie_id, limit=12)

    return jsonify({"pelicula": pelicula, "recomendadas": recomendadas})


# ---------------------
# Admin: listar usuarios y eliminar usuario
# ---------------------
@app.route("/admin/usuarios")
def admin_users():
    usuario_actual = session.get("usuario_id")
    if not usuario_actual:
        flash("Debes iniciar sesión.")
        return redirect(url_for("login"))

    if int(usuario_actual) != 1:
        flash("No autorizado.")
        return redirect(url_for("cuenta"))

    # Obtener lista de usuarios
    # Aquí usamos directamente la consulta como ejemplo
    from db import get_connection

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT Usuario_ID, Nombre, Email, FechaRegistro
        FROM dbo.Usuarios
        ORDER BY FechaRegistro DESC;
        """
    )
    usuarios = []
    rows = cursor.fetchall()
    for row in rows:
        usuarios.append(
            {
                "Usuario_ID": row.Usuario_ID,
                "Nombre": row.Nombre,
                "Email": row.Email,
                "FechaRegistro": row.FechaRegistro,
            }
        )
    conn.close()
    return render_template("admin_users.html", usuarios=usuarios)


@app.route("/admin/eliminar_usuario/<int:usuario_id>", methods=["POST"])
def admin_eliminar_usuario(usuario_id):
    usuario_actual = session.get("usuario_id")
    if not usuario_actual:
        flash("Debes iniciar sesión para realizar esta acción.")
        return redirect(url_for("login"))

    if int(usuario_actual) != 1:
        flash("No autorizado. Solo el administrador puede eliminar usuarios.")
        return redirect(url_for("cuenta"))

    if usuario_id == usuario_actual:
        flash("No puedes eliminar tu propia cuenta desde el panel de admin.")
        return redirect(url_for("admin_users"))

    ok = eliminar_usuario(usuario_id)
    if ok:
        flash(f"Usuario {usuario_id} eliminado correctamente.")
    else:
        flash("No se pudo eliminar el usuario. Revisa los logs.")
    return redirect(url_for("admin_users"))


# ---------------------
# Ejecutar app
# ---------------------
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)