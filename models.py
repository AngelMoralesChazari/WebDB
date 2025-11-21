from db import get_connection


def obtener_peliculas(limit=20):
    """
    Obtiene una lista de películas desde la tabla dbo.mymoviedb.
    Retorna una lista de diccionarios.
    """
    print(">>> obtener_peliculas() llamado, limit =", limit)

    conn = get_connection()
    if not conn:
        print(">>> No se pudo obtener la conexión")
        return []

    print(">>> Conexión obtenida, ejecutando consulta...")

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
        print(">>> Consulta ejecutada, haciendo fetch...")
        rows = cursor.fetchall()
        print(">>> Filas recibidas:", len(rows))

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

        print(">>> Películas convertidas a diccionario:", len(peliculas))

    except Exception as e:
        print(f"Error al obtener películas: {e}")
    finally:
        conn.close()
        print(">>> Conexión cerrada")

    return peliculas