from db import get_connection

print("Probando conexión a SQL Server...")

conn = get_connection()
print("Resultado de get_connection():", conn)

if conn:
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 * FROM dbo.mymoviedb;")
        row = cursor.fetchone()
        print("Consulta OK, primera fila:", row)
    except Exception as e:
        print("Error ejecutando consulta de prueba:", e)
    finally:
        conn.close()
        print("Conexión cerrada.")
else:
    print("No se pudo obtener conexión.")