import pymysql

try:
    conn = pymysql.connect(
        host="192.168.40.160",
        user="deploy_user",
        password="deploy",
        database="db_demografi",
        port=3306  # Default port MySQL
    )
    print("Koneksi Berhasil!")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
