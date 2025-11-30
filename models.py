from db import get_connection
from datetime import datetime, timedelta

def obtener_peliculas(busqueda=None, genero=None, anio=None, limit=20, offset=0):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        Movie_ID,
        Title,
        Genre,
        Release_Date,
        Poster_Url,
        Vote_Average,
        Vote_Count,
        Overview
    FROM dbo.mymoviedb 
    WHERE 1=1
    """
    params = []

    if busqueda:
        query += " AND (Title LIKE ? OR Overview LIKE ?)"
        params.extend([f"%{busqueda}%", f"%{busqueda}%"])

    if genero:
        query += " AND Genre LIKE ?"
        params.append(f"%{genero}%")

    if anio:
        query += " AND YEAR(Release_Date) = ?"
        params.append(anio)

    query += " ORDER BY Popularity DESC"
    query += " OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
    params.extend([offset, limit])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    peliculas = []
    for row in rows:
        peliculas.append({
            "id": row.Movie_ID,
            "titulo": row.Title,
            "genero": row.Genre,
            "fecha": row.Release_Date,
            "poster": row.Poster_Url,
            "promedio": row.Vote_Average,
            "votos": row.Vote_Count,
            "overview": row.Overview
        })

    return peliculas


def contar_peliculas(busqueda=None, genero=None, anio=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT COUNT(*) FROM dbo.mymoviedb WHERE 1=1"
    params = []

    if busqueda:
        query += " AND (Title LIKE ? OR Overview LIKE ?)"
        params.extend([f"%{busqueda}%", f"%{busqueda}%"])

    if genero:
        query += " AND Genre LIKE ?"
        params.append(f"%{genero}%")

    if anio:
        query += " AND YEAR(Release_Date) = ?"
        params.append(anio)

    cursor.execute(query, params)
    total = cursor.fetchone()[0]
    conn.close()

    return total


# Tendencias
def obtener_pelicula_aleatoria():
    conn = get_connection()
    if not conn:
        return None

    query = """
    SELECT TOP 1
        Movie_ID,
        Release_Date,
        Title,
        Overview,
        Popularity,
        Vote_Count,
        Vote_Average,
        Original_Language,
        Genre,
        Poster_Url
    FROM dbo.mymoviedb
    ORDER BY NEWID();
    """

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()

        if row:
            pelicula = {
                "id": row.Movie_ID,
                "fecha": row.Release_Date,
                "titulo": row.Title,
                "overview": row.Overview,
                "popularidad": row.Popularity,
                "votos": row.Vote_Count,
                "promedio": row.Vote_Average,
                "idioma": row.Original_Language,
                "genero": row.Genre,
                "poster": row.Poster_Url,
            }
            return pelicula
        else:
            return None

    except Exception as e:
        print(f"Error al obtener película aleatoria: {e}")
        return None
    finally:
        conn.close()


# Recomendadas
def obtener_peliculas_aleatorias(limit=10):
    conn = get_connection()
    if not conn:
        return []

    query = f"""
    SELECT TOP ({limit})
        Movie_ID,
        Release_Date,
        Title,
        Overview,
        Popularity,
        Vote_Count,
        Vote_Average,
        Original_Language,
        Genre,
        Poster_Url
    FROM dbo.mymoviedb
    ORDER BY NEWID();
    """

    peliculas = []
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            peliculas.append({
                "id": row.Movie_ID,
                "fecha": row.Release_Date,
                "titulo": row.Title,
                "overview": row.Overview,
                "popularidad": row.Popularity,
                "votos": row.Vote_Count,
                "promedio": row.Vote_Average,
                "idioma": row.Original_Language,
                "genero": row.Genre,
                "poster": row.Poster_Url,
            })
    except Exception as e:
        print(f"Error al obtener películas aleatorias: {e}")
    finally:
        conn.close()

    return peliculas


def obtener_pelicula_por_id(movie_id):
    conn = get_connection()
    if not conn:
        return None

    query = """
    SELECT
        Movie_ID,
        Release_Date,
        Title,
        Overview,
        Popularity,
        Vote_Count,
        Vote_Average,
        Original_Language,
        Genre,
        Poster_Url
    FROM dbo.mymoviedb
    WHERE Movie_ID = ?;
    """

    try:
        cursor = conn.cursor()
        cursor.execute(query, (movie_id,))
        row = cursor.fetchone()

        if not row:
            return None

        pelicula = {
            "id": row.Movie_ID,
            "fecha": row.Release_Date,
            "titulo": row.Title,
            "overview": row.Overview,
            "popularidad": row.Popularity,
            "votos": row.Vote_Count,
            "promedio": row.Vote_Average,
            "idioma": row.Original_Language,
            "genero": row.Genre,
            "poster": row.Poster_Url,
        }
        return pelicula

    except Exception as e:
        print(f"Error al obtener película por id: {e}")
        return None
    finally:
        conn.close()


def obtener_recomendadas_por_genero(genero, movie_id_excluir=None, limit=12):
    """
    Devuelve películas del mismo género (o que contengan ese género en el campo Genre),
    ordenadas por popularidad, excluyendo opcionalmente una película concreta.
    """
    conn = get_connection()
    if not conn:
        return []

    query = """
    SELECT TOP ({limit})
        Movie_ID,
        Release_Date,
        Title,
        Overview,
        Popularity,
        Vote_Count,
        Vote_Average,
        Original_Language,
        Genre,
        Poster_Url
    FROM dbo.mymoviedb
    WHERE Genre LIKE ?
    """.format(limit=limit)

    params = [f"%{genero}%"]

    if movie_id_excluir:
        query += " AND Movie_ID <> ?"
        params.append(movie_id_excluir)

    query += " ORDER BY Popularity DESC;"

    peliculas = []
    try:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        for row in rows:
            peliculas.append({
                "id": row.Movie_ID,
                "fecha": row.Release_Date,
                "titulo": row.Title,
                "overview": row.Overview,
                "popularidad": row.Popularity,
                "votos": row.Vote_Count,
                "promedio": row.Vote_Average,
                "idioma": row.Original_Language,
                "genero": row.Genre,
                "poster": row.Poster_Url,
            })
    except Exception as e:
        print(f"Error al obtener recomendadas por género: {e}")
    finally:
        conn.close()

    return peliculas


# Usuarios
def registrar_usuario(nombre, email, password_hash):
    conn = get_connection()
    if not conn:
        print("=== No se pudo obtener la conexión en registrar_usuario ===")
        return False

    query = """
    INSERT INTO dbo.Usuarios (Nombre, Email, Contraseña)
    VALUES (?, ?, ?);
    """

    try:
        cursor = conn.cursor()
        cursor.execute(query, (nombre, email, password_hash))
        conn.commit()
        print(f">>> Usuario registrado: {email}")
        return True
    except Exception as e:
        print(f"Error al registrar usuario: {e}")
        return False
    finally:
        conn.close()
        print("!= Conexión cerrada en registrar_usuario")


def obtener_usuario_por_email(email):
    conn = get_connection()
    if not conn:
        print("=== No se pudo obtener la conexión en obtener_usuario_por_email ===")
        return None

    query = """
    SELECT Usuario_ID, Nombre, Email, Contraseña, FechaRegistro
    FROM dbo.Usuarios
    WHERE Email = ?;
    """

    try:
        cursor = conn.cursor()
        cursor.execute(query, (email,))
        row = cursor.fetchone()
        if not row:
            return None

        usuario = {
            "id": row.Usuario_ID,
            "nombre": row.Nombre,
            "email": row.Email,
            "password_hash": row.Contraseña,
            "fecha_registro": row.FechaRegistro,
        }
        return usuario
    except Exception as e:
        print(f"Error al obtener usuario por email: {e}")
        return None
    finally:
        conn.close()
        print("!= Conexión cerrada en obtener_usuario_por_email")


def buscar_peliculas(texto=None, genero=None, anio=None, limit=50):
    conn = get_connection()
    if not conn:
        print("=== No se pudo obtener la conexión en buscar_peliculas ===")
        return []

    # Construimos la consulta dinámica
    base_query = """
    SELECT TOP ({limit})
        Movie_ID,
        Release_Date,
        Title,
        Overview,
        Popularity,
        Vote_Count,
        Vote_Average,
        Original_Language,
        Genre,
        Poster_Url
    FROM dbo.mymoviedb
    WHERE 1=1
    """.format(limit=limit)

    params = []

    # Filtro por texto en título u overview
    if texto:
        base_query += " AND (Title LIKE ? OR Overview LIKE ?)"
        like_text = f"%{texto}%"
        params.append(like_text)
        params.append(like_text)

    # Filtro por género (contenga el género)
    if genero:
        base_query += " AND Genre LIKE ?"
        params.append(f"%{genero}%")

    # Filtro por año: comparamos con el año de Release_Date
    if anio:
        base_query += " AND YEAR(Release_Date) = ?"
        params.append(anio)

    # Ordenamos por popularidad
    base_query += " ORDER BY Popularity DESC;"

    peliculas = []
    try:
        cursor = conn.cursor()
        cursor.execute(base_query, tuple(params))
        rows = cursor.fetchall()

        for row in rows:
            peliculas.append({
                "id": row.Movie_ID,
                "fecha": row.Release_Date,
                "titulo": row.Title,
                "overview": row.Overview,
                "popularidad": row.Popularity,
                "votos": row.Vote_Count,
                "promedio": row.Vote_Average,
                "idioma": row.Original_Language,
                "genero": row.Genre,
                "poster": row.Poster_Url,
            })
    except Exception as e:
        print(f"Error en buscar_peliculas: {e}")
    finally:
        conn.close()

    return peliculas

# ==== RENTAS ====

def crear_renta(usuario_id, movie_id, dias=3, monto=None):
    """
    Crea un registro de renta para un usuario y una película.
    - Por defecto dura 3 días.
    - Máximo 5 días.
    """
    if dias < 1 or dias > 5:
        print("Error: El número de días debe estar entre 1 y 5.")
        return False

    conn = get_connection()
    if not conn:
        print("=== No se pudo obtener la conexión en crear_renta ===")
        return False

    from datetime import datetime, timedelta
    fecha_inicio = datetime.now()
    fecha_devolucion = fecha_inicio + timedelta(days=dias)
    estatus = "Activa"

    query = """
    BEGIN TRANSACTION;
    INSERT INTO dbo.Rentas (Usuario_ID, Movie_ID, FechaInicio, FechaDevolucion, Estatus, Monto)
    VALUES (?, ?, ?, ?, ?, ?);
    COMMIT;
    """

    try:
        cursor = conn.cursor()
        cursor.execute(query, (
            usuario_id,
            movie_id,
            fecha_inicio,
            fecha_devolucion,
            estatus,
            monto
        ))
        conn.commit()
        print(f">>> Renta creada: Usuario {usuario_id}, Película {movie_id}, Días {dias}")
        return True
    except Exception as e:
        print(f"Error al crear renta: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def actualizar_estado_renta(renta_id, nuevo_estatus, usuario_id=None):
    """
    Actualiza el estado de una renta.
    - renta_id: id de la renta a actualizar
    - nuevo_estatus: string ("Devuelta", "Cancelada", etc.)
    - usuario_id: opcional. Si se provee, se verifica que la renta pertenezca al usuario.
    Retorna True si la actualización tuvo efecto, False si no (o en caso de error).
    """
    conn = get_connection()
    if not conn:
        print("=== No se pudo obtener la conexión en actualizar_estado_renta ===")
        return False

    try:
        cursor = conn.cursor()

        # Si se pasó usuario_id, verificar pertenencia
        if usuario_id is not None:
            cursor.execute("""
                SELECT Usuario_ID FROM dbo.Rentas WHERE Renta_ID = ?
            """, (renta_id,))
            row = cursor.fetchone()
            if not row:
                print(f"actualizar_estado_renta: renta {renta_id} no encontrada")
                return False
            if row[0] != usuario_id:
                print(f"actualizar_estado_renta: renta {renta_id} no pertenece al usuario {usuario_id}")
                return False

        # Ejecutar la actualización dentro de una transacción
        cursor.execute("BEGIN TRANSACTION;")
        cursor.execute("""
            UPDATE dbo.Rentas
            SET Estatus = ?
            WHERE Renta_ID = ?;
        """, (nuevo_estatus, renta_id))
        affected = cursor.rowcount

        if affected == 0:
            # No se actualizó ninguna fila (posible id inexistente)
            cursor.execute("ROLLBACK;")
            print(f"actualizar_estado_renta: no se afectó ninguna fila para renta_id={renta_id}")
            return False

        cursor.execute("COMMIT;")
        conn.commit()
        print(f">>> Renta {renta_id} actualizada a '{nuevo_estatus}' (filas afectadas: {affected})")
        return True

    except Exception as e:
        print(f"Error al actualizar estado de renta: {e}")
        try:
            conn.rollback()
        except:
            pass
        return False
    finally:
        try:
            conn.close()
        except:
            pass


def obtener_rentas_por_usuario(usuario_id, filtro=None):
    """
    Devuelve las rentas de un usuario.
    filtro puede ser: None, 'por_vencer', 'vencidas', 'devueltas'
    """
    conn = get_connection()
    if not conn:
        print("=== No se pudo obtener la conexión en obtener_rentas_por_usuario ===")
        return []

    query = """
    SELECT
        r.Renta_ID,
        r.FechaInicio,
        r.FechaDevolucion,
        r.Estatus,
        r.Monto,
        m.Movie_ID,
        m.Title,
        m.Poster_Url
    FROM dbo.Rentas r
    INNER JOIN dbo.mymoviedb m ON r.Movie_ID = m.Movie_ID
    WHERE r.Usuario_ID = ?
    ORDER BY r.FechaInicio DESC;
    """

    rentas = []
    try:
        cursor = conn.cursor()
        cursor.execute(query, (usuario_id,))
        rows = cursor.fetchall()

        from datetime import datetime
        ahora = datetime.now()

        for row in rows:
            fecha_devolucion = row.FechaDevolucion
            estatus_bd = (row.Estatus or "").strip()

            # Cálculo de estatus "amigable"
            if estatus_bd.lower() in ("completada", "devuelto", "devuelta", "cancelado", "cancelada"):
                estatus_mostrado = "Devuelta/Cancelada"
            else:
                if fecha_devolucion and ahora > fecha_devolucion:
                    estatus_mostrado = "Vencida"
                else:
                    estatus_mostrado = "Por vencer"

            renta = {
                "renta_id": row.Renta_ID,
                "fecha_inicio": row.FechaInicio,
                "fecha_devolucion": fecha_devolucion,
                "estatus": estatus_mostrado,
                "estatus_bd": estatus_bd,
                "monto": row.Monto,
                "movie_id": row.Movie_ID,
                "titulo": row.Title,
                "poster": row.Poster_Url,
            }

            # Aplicar filtro en memoria
            if filtro == "por_vencer" and renta["estatus"] != "Por vencer":
                continue
            if filtro == "vencidas" and renta["estatus"] != "Vencida":
                continue
            if filtro == "devueltas" and renta["estatus"] != "Devuelta/Cancelada":
                continue

            rentas.append(renta)

    except Exception as e:
        print(f"Error al obtener rentas por usuario: {e}")
    finally:
        conn.close()

    return rentas

def tiene_renta_activa(usuario_id, movie_id):
    """
    Devuelve True si el usuario tiene una renta activa de esa película.
    Para simplificar, consideramos activa si Estatus <> 'Completada' y <> 'Cancelada'.
    """
    conn = get_connection()
    if not conn:
        print("=== No se pudo obtener la conexión en tiene_renta_activa ===")
        return False

    query = """
    SELECT COUNT(*)
    FROM dbo.Rentas
    WHERE Usuario_ID = ?
      AND Movie_ID = ?
      AND Estatus NOT IN ('Completada', 'Cancelada');
    """

    try:
        cursor = conn.cursor()
        cursor.execute(query, (usuario_id, movie_id))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Error en tiene_renta_activa: {e}")
        return False
    finally:
        conn.close()

def eliminar_usuario(usuario_id):
    """
    Elimina un usuario y sus rentas asociadas dentro de una transacción.
    Retorna True si se eliminó correctamente, False si hubo error o no existe.
    """
    conn = get_connection()
    if not conn:
        print("=== No se pudo obtener la conexión en eliminar_usuario ===")
        return False

    try:
        cursor = conn.cursor()
        # Iniciar transacción explícita (pyodbc maneja transacción con commit/rollback)
        cursor.execute("BEGIN TRANSACTION;")

        # (Opcional) Comprobar existencia
        cursor.execute("SELECT COUNT(*) FROM dbo.Usuarios WHERE Usuario_ID = ?", (usuario_id,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("ROLLBACK;")
            print(f"eliminar_usuario: usuario {usuario_id} no existe")
            return False

        # 1) Eliminar rentas asociadas (si prefieres conservar histórico cambia a soft-delete o reasignación)
        cursor.execute("DELETE FROM dbo.Rentas WHERE Usuario_ID = ?", (usuario_id,))

        # 2) Eliminar registros dependientes adicionales si los hubiera (ej: favoritos, reviews)
        # cursor.execute("DELETE FROM dbo.Favoritos WHERE Usuario_ID = ?", (usuario_id,))

        # 3) Eliminar el usuario
        cursor.execute("DELETE FROM dbo.Usuarios WHERE Usuario_ID = ?", (usuario_id,))

        conn.commit()
        print(f">>> Usuario {usuario_id} y sus rentas eliminadas correctamente.")
        return True

    except Exception as e:
        print(f"Error en eliminar_usuario: {e}")
        try:
            conn.rollback()
        except:
            pass
        return False
    finally:
        try:
            conn.close()
        except:
            pass