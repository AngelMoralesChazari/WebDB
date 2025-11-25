from db import get_connection

#Banner
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