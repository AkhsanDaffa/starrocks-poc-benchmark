import mysql.connector
import time
from datetime import datetime

# --- KONFIGURASI ---
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '', 
    'database': 'zim_analytics',
    'port': 3306
}

# StarRocks pakai protokol MySQL, jadi drivernya sama
STARROCKS_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '', # Default StarRocks biasanya kosong atau root
    'database': 'zim_analytics',
    'port': 9030 # Port SQL StarRocks (PENTING!)
}

def get_mysql_conn():
    return mysql.connector.connect(**MYSQL_CONFIG)

def get_starrocks_conn():
    return mysql.connector.connect(**STARROCKS_CONFIG)

def etl_process():
    print(f"\n--- [ {datetime.now()} ] MEMULAI PROSES SYNC ---")
    
    # 1. Buka Koneksi
    try:
        source_conn = get_mysql_conn()
        dest_conn = get_starrocks_conn()
        source_cursor = source_conn.cursor()
        dest_cursor = dest_conn.cursor()
    except Exception as e:
        print(f"Gagal koneksi: {e}")
        return

    # 2. Ambil data dari MySQL (Misal: ambil semua data 1 jam terakhir / semua data)
    # Untuk PoC ini, kita ambil semua data agar terlihat update-nya (Overwrite logic)
    print("-> Mengambil data dari MySQL...")
    source_cursor.execute("SELECT transaction_id, entry_time, vehicle_plate, vehicle_type, exit_time, duration_minutes, payment_method, amount, location, created_at, updated_at FROM parking_transactions")
    data = source_cursor.fetchall()
    
    if not data:
        print("-> Tidak ada data di MySQL.")
        return

    print(f"-> Ditemukan {len(data)} baris data.")

    # 3. Masukkan ke StarRocks
    # StarRocks Primary Key Model akan otomatis UPDATE jika ID sudah ada
    print("-> Mengirim ke StarRocks...")
    
    sql_insert = """
    INSERT INTO parking_transactions 
    (transaction_id, entry_time, vehicle_plate, vehicle_type, exit_time, duration_minutes, payment_method, amount, location, created_at, updated_at) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    # Batch insert agar cepat
    try:
        dest_cursor.executemany(sql_insert, data)
        dest_conn.commit()
        print(f"-> SUKSES! {len(data)} data tersinkronisasi ke StarRocks.")
    except Exception as e:
        print(f"-> Gagal Insert StarRocks: {e}")

    # 4. Tutup
    source_cursor.close()
    dest_cursor.close()
    source_conn.close()
    dest_conn.close()

def main():
    print("=== SYSTEM ETL (MySQL -> StarRocks) ===")
    print("Running every 10 seconds...")
    
    while True:
        etl_process()
        # Jeda 10 detik (Simulasi batch processing)
        # Di production, ini bisa diganti 3600 (1 jam)
        time.sleep(20) 

if __name__ == "__main__":
    main()