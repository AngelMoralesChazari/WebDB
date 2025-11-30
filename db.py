import pyodbc

def get_connection():
    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=ANGEL;'
            'DATABASE=Movies;'
            'Trusted_Connection=yes;'
        )
        return conn
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

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