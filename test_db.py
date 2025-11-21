import pyodbc

print("Iniciando prueba de conexión...")

try:
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=ANGEL;'
        'DATABASE=Movies;'
        'Trusted_Connection=yes;'
        'Connection Timeout=5;'
    )
    print("✅ Conexión exitosa")
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 3 Movie_ID, Title FROM dbo.mymoviedb;")
    rows = cursor.fetchall()
    for r in rows:
        print(r.Movie_ID, "-", r.Title)
    conn.close()
    print("✅ Consulta terminada y conexión cerrada")
except Exception as e:
    print("❌ Error en la conexión o consulta:")
    print(e)