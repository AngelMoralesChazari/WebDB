from db import get_connection
from datetime import datetime, timedelta
import hashlib

def obtener_peliculas(busqueda = None, genero = None, anio = None, limit = 20, offset = 0):
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
        query += " AND Title LIKE ?"
        params.append(f"%{busqueda}%")

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
        # SOLO contar por Title, NO por Overview
        query += " AND Title LIKE ?"
        params.append(f"%{busqueda}%")

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

def obtener_generos():
    conn = get_connection()
    if not conn:
        return []
    
    query = """
    SELECT DISTINCT 
        TRIM(value) as genero
    FROM dbo.mymoviedb
    CROSS APPLY STRING_SPLIT(Genre, ',')
    WHERE TRIM(value) <> ''
    ORDER BY TRIM(value);
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        generos = [row.genero.strip() for row in rows if row.genero and row.genero.strip()]
        return generos
    except Exception as e:
        print(f"Error al obtener géneros: {e}")
        try:
            cursor.execute("""
                SELECT TOP 100 Genre 
                FROM dbo.mymoviedb 
                WHERE Genre IS NOT NULL AND Genre <> ''
                ORDER BY Genre
            """)
            rows = cursor.fetchall()
            
            generos_set = set()
            for row in rows:
                if row.Genre:
                    generos = [g.strip() for g in row.Genre.split(',') if g.strip()]
                    generos_set.update(generos)
            
            return sorted(list(generos_set))
        except Exception as e2:
            print(f"Error alternativo al obtener géneros: {e2}")
            return []
    finally:
        conn.close()


def obtener_recomendadas_por_genero(genero, movie_id_excluir = None, limit = 12):
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
    """.format(limit = limit)

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


def buscar_peliculas(texto = None, genero = None, anio = None, limit = 50):
    conn = get_connection()
    if not conn:
        print("=== No se pudo obtener la conexión en buscar_peliculas ===")
        return []

    # Consulta dinámica
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

    # Filtro por texto SOLO en título (NO en overview)
    if texto:
        base_query += " AND Title LIKE ?"
        params.append(f"%{texto}%")

    # Filtro por género 
    if genero:
        base_query += " AND Genre LIKE ?"
        params.append(f"%{genero}%")

    # Filtro por año
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

# === RENTAS ===
def crear_renta(usuario_id, movie_id, dias=3, monto=None):
    from datetime import datetime, timedelta

    if dias < 1 or dias > 5:
        print("Error: El número de días debe estar entre 1 y 5.")
        return False, None

    conn = get_connection()
    if not conn:
        print("=== No se pudo obtener la conexión en crear_renta ===")
        return False, None

    fecha_inicio = datetime.now()
    fecha_devolucion = fecha_inicio + timedelta(days=dias)
    estatus = "Activa"

    try:
        cursor = conn.cursor()
        insert_sql = """
        INSERT INTO dbo.Rentas (Usuario_ID, Movie_ID, FechaInicio, FechaDevolucion, Estatus, Monto)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        cursor.execute(insert_sql, (usuario_id, movie_id, fecha_inicio, fecha_devolucion, estatus, monto))
        conn.commit()

        # Obtener id insertado (SCOPE_IDENTITY)
        cursor.execute("SELECT SCOPE_IDENTITY() AS id;")
        row = cursor.fetchone()
        new_id = row[0] if row and len(row) > 0 else None

        print(f"DEBUG crear_renta: insert ok. nuevo id = {new_id} usuario={usuario_id} movie={movie_id} monto={monto}")
        if new_id is not None:
            return True, int(new_id)
        else:
            return True, None
    except Exception as e:
        print(f"Error al crear renta: {e}")
        try:
            conn.rollback()
        except:
            pass
        return False, None
    finally:
        try:
            conn.close()
        except:
            pass

def actualizar_estado_renta(renta_id, nuevo_estatus, usuario_id=None):
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

        # Ejecutar la actualización 
        cursor.execute("BEGIN TRANSACTION;")
        cursor.execute("""
            UPDATE dbo.Rentas
            SET Estatus = ?
            WHERE Renta_ID = ?;
        """, (nuevo_estatus, renta_id))
        affected = cursor.rowcount

        if affected == 0:
            # No se actualizó ninguna fila 
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


def obtener_rentas_por_usuario(usuario_id, filtro = None):
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

            # Cálculo de estatus
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

            if filtro == "activas" and renta["estatus"] == "Devuelta/Cancelada":
                continue
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

def eliminar_usuario(usuario_id, eliminado_por_usuario_id=None, razon=None):
    """
    Elimina un usuario moviendo sus datos a la tabla de usuarios eliminados primero.
    """
    conn = get_connection()
    if not conn:
        print("=== No se pudo obtener la conexión en eliminar_usuario ===")
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN TRANSACTION;")
        print(f"DEBUG eliminar_usuario: Transacción iniciada para usuario {usuario_id}")

        # 1. Verificar si el usuario existe y obtener sus datos
        cursor.execute("""
            SELECT Usuario_ID, Nombre, Email, FechaRegistro 
            FROM dbo.Usuarios 
            WHERE Usuario_ID = ?
        """, (usuario_id,))
        
        usuario_data = cursor.fetchone()
        if not usuario_data:
            cursor.execute("ROLLBACK;")
            print(f"DEBUG eliminar_usuario: usuario {usuario_id} no existe")
            return False
        
        print(f"DEBUG eliminar_usuario: Usuario encontrado - ID: {usuario_data.Usuario_ID}, Email: {usuario_data.Email}")

        # 2. Guardar en tabla de usuarios eliminados
        print(f"DEBUG eliminar_usuario: Intentando insertar en Usuarios_Eliminados...")
        cursor.execute("""
            INSERT INTO dbo.Usuarios_Eliminados 
            (Usuario_ID_Original, Nombre, Email, FechaRegistro_Original, 
             FechaEliminacion, Razón, EliminadoPor_UsuarioID)
            VALUES (?, ?, ?, ?, GETDATE(), ?, ?)
        """, (
            usuario_data.Usuario_ID,
            usuario_data.Nombre,
            usuario_data.Email,
            usuario_data.FechaRegistro,
            razon or "Eliminado por administrador",
            eliminado_por_usuario_id
        ))
        
        eliminado_id = None
        cursor.execute("SELECT SCOPE_IDENTITY() AS id;")
        row = cursor.fetchone()
        if row:
            eliminado_id = row[0]
        
        print(f"DEBUG eliminar_usuario: Usuario archivado en eliminados (ID: {eliminado_id})")

        # 3. Eliminar tarjetas del usuario
        cursor.execute("DELETE FROM dbo.Tarjetas WHERE Usuario_ID = ?", (usuario_id,))
        tarjetas_eliminadas = cursor.rowcount
        print(f"DEBUG eliminar_usuario: Tarjetas eliminadas: {tarjetas_eliminadas}")

        # 4. Eliminar rentas del usuario
        cursor.execute("DELETE FROM dbo.Rentas WHERE Usuario_ID = ?", (usuario_id,))
        rentas_eliminadas = cursor.rowcount
        print(f"DEBUG eliminar_usuario: Rentas eliminadas: {rentas_eliminadas}")

        # 5. Finalmente eliminar el usuario
        cursor.execute("DELETE FROM dbo.Usuarios WHERE Usuario_ID = ?", (usuario_id,))
        usuarios_eliminados = cursor.rowcount
        print(f"DEBUG eliminar_usuario: Usuarios eliminados de tabla principal: {usuarios_eliminados}")

        # 6. Confirmar transacción
        cursor.execute("COMMIT;")
        conn.commit()
        print(f"DEBUG eliminar_usuario: Transacción COMMIT exitosa para usuario {usuario_id}")
        
        if usuarios_eliminados > 0:
            print(f">>> ÉXITO: Usuario {usuario_id} eliminado correctamente. Datos archivados en eliminados.")
            return True
        else:
            print(f">>> ERROR: No se eliminó ningún usuario. Rollback realizado.")
            cursor.execute("ROLLBACK;")
            return False

    except Exception as e:
        print(f"ERROR CRÍTICO en eliminar_usuario: {e}")
        import traceback
        traceback.print_exc()
        try:
            cursor.execute("ROLLBACK;")
            print("DEBUG eliminar_usuario: Rollback por excepción")
        except:
            pass
        return False
    finally:
        try:
            conn.close()
            print("DEBUG eliminar_usuario: Conexión cerrada")
        except:
            pass

def _tokenizar_numero(numero_tarjeta):
    return hashlib.sha256(numero_tarjeta.encode('utf-8')).hexdigest()

def _mask_last4(numero_tarjeta):
    numero = "".join(filter(str.isdigit, numero_tarjeta))
    return numero[-4:] if len(numero) >= 4 else numero

def guardar_tarjeta(usuario_id, titular, numero_tarjeta, expiry_month, expiry_year, guardar=True):
    conn = get_connection()
    if not conn:
        print("=== No se pudo obtener conexión en guardar_tarjeta ===")
        return False, None

    try:
        token = _tokenizar_numero(numero_tarjeta)
        last4 = _mask_last4(numero_tarjeta)

        query = """
        INSERT INTO dbo.Tarjetas (Usuario_ID, Titular, Last4, Numero_Token, ExpiryMonth, ExpiryYear, Guardar)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        cursor = conn.cursor()
        cursor.execute(query, (
            usuario_id,
            titular,
            last4,
            token,
            int(expiry_month),
            int(expiry_year),
            1 if guardar else 0
        ))
        conn.commit()
        
        # Obtener el id insertado
        cursor.execute("SELECT SCOPE_IDENTITY() AS id;")
        new_id = cursor.fetchone()[0]
        return True, int(new_id)
    except Exception as e:
        print("Error en guardar_tarjeta:", e)
        try:
            conn.rollback()
        except:
            pass
        return False, None
    finally:
        try:
            conn.close()
        except:
            pass

def obtener_tarjetas_por_usuario(usuario_id):
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Tarjeta_ID, Titular, Last4, ExpiryMonth, ExpiryYear, FechaRegistro, Guardar
            FROM dbo.Tarjetas
            WHERE Usuario_ID = ?
            ORDER BY FechaRegistro DESC;
        """, (usuario_id,))
        rows = cursor.fetchall()
        tarjetas = []
        for row in rows:
            tarjetas.append({
                "tarjeta_id": row.Tarjeta_ID,
                "titular": row.Titular,
                "last4": row.Last4,
                "expiry_month": row.ExpiryMonth,
                "expiry_year": row.ExpiryYear,
                "fecha_registro": row.FechaRegistro,
                "guardar": bool(row.Guardar)
            })
        return tarjetas
    except Exception as e:
        print("Error en obtener_tarjetas_por_usuario:", e)
        return []
    finally:
        try:
            conn.close()
        except:
            pass

def obtener_tarjeta_por_id(tarjeta_id):
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Tarjeta_ID, Usuario_ID, Titular, Last4, ExpiryMonth, ExpiryYear, FechaRegistro
            FROM dbo.Tarjetas
            WHERE Tarjeta_ID = ?;
        """, (tarjeta_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "tarjeta_id": row.Tarjeta_ID,
            "usuario_id": row.Usuario_ID,
            "titular": row.Titular,
            "last4": row.Last4,
            "expiry_month": row.ExpiryMonth,
            "expiry_year": row.ExpiryYear,
            "fecha_registro": row.FechaRegistro
        }
    except Exception as e:
        print("Error en obtener_tarjeta_por_id:", e)
        return None
    finally:
        try:
            conn.close()
        except:
            pass

def eliminar_tarjeta(tarjeta_id, usuario_id=None):
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        if usuario_id:
            cursor.execute("DELETE FROM dbo.Tarjetas WHERE Tarjeta_ID = ? AND Usuario_ID = ?;", (tarjeta_id, usuario_id))
        else:
            cursor.execute("DELETE FROM dbo.Tarjetas WHERE Tarjeta_ID = ?;", (tarjeta_id,))
        affected = cursor.rowcount
        conn.commit()
        return affected > 0
    except Exception as e:
        print("Error en eliminar_tarjeta:", e)
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

def tiene_tarjeta(usuario_id):
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dbo.Tarjetas WHERE Usuario_ID = ?;", (usuario_id,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print("Error en tiene_tarjeta:", e)
        return False
    finally:
        try:
            conn.close()
        except:
            pass
