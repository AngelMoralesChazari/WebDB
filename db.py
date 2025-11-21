import pyodbc


def get_connection():
    """
    Crea y retorna una conexión a SQL Server.
    Ajusta los parámetros según tu configuración.
    """
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