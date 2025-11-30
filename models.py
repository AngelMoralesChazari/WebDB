from db import get_connection

def obtener_peliculas(limit = 20):
    print("obtener_peliculas() llamado, limit =", limit)

    conn = get_connection()
    if not conn:
        print(" === No se pudo obtener la conexión === ")
        return []

    print("Conexión obtenida")

    query = """
        SELECT TOP (?) 
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
        ORDER BY Popularity DESC;
    """

    peliculas = []

    try:
        cursor = conn.cursor()
        cursor.execute(query, (limit,))
        print("=== Consulta ejecutada")
        rows = cursor.fetchall()
        print("=== Filas recibidas:", len(rows))

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

        print("=== Películas añadidas como un diccionario:", len(peliculas))

    except Exception as e:
        print(f"Error al obtener películas: {e}")
    finally:
        conn.close()
        print("!= Conexión cerrada")

    return peliculas

#Tendencias
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

#Recomendadas
def obtener_peliculas_aleatorias(limit = 10):
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