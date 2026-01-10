import psycopg2
import time
import random
from faker import Faker
from datetime import datetime

# --- KONFIGURASI KONEKSI POSTGRESQL ---
db_config = {
    'host': '192.168.200.212',
    'user': 'postgres',           # User default container
    'password': 'postgres',       # Password dari docker-compose
    'database': 'zim_pg_analytics', # Nama DB baru
    'port': 5500                  # Port standar Postgres
}

fake = Faker('id_ID')

def get_connection():
    try:
        return psycopg2.connect(**db_config)
    except psycopg2.Error as err:
        print(f"Error koneksi: {err}")
        return None

def mobil_masuk(cursor):
    entry_time = datetime.now()
    plat = f"{random.choice(['B', 'D', 'F', 'L'])} {random.randint(1000, 9999)} {fake.lexify(text='???').upper()}"
    tipe = random.choice(['Motor', 'Mobil'])
    lokasi = random.choice(['Mall A', 'Mall B', 'Office Park'])
    
    # Syntax INSERT sama, Postgres juga pakai %s untuk placeholder di library ini
    sql = """
    INSERT INTO parking_transactions 
    (entry_time, vehicle_plate, vehicle_type, location) 
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (entry_time, plat, tipe, lokasi))
    print(f"[MASUK] {plat} ({tipe}) di {lokasi}")

def mobil_keluar(cursor):
    # PERBEDAAN: MySQL pakai RAND(), Postgres pakai RANDOM()
    cursor.execute("SELECT transaction_id, entry_time, vehicle_type FROM parking_transactions WHERE exit_time IS NULL ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()
    
    if result:
        trx_id, entry_time, v_type = result
        exit_time = datetime.now()
        
        # Hitung durasi
        delta = exit_time - entry_time
        duration = int(delta.total_seconds() // 60)
        if duration == 0: duration = 1 
        
        tarif = 2000 if v_type == 'Motor' else 5000
        amount = tarif * (duration // 60 + 1)
        method = random.choice(['Cash', 'QRIS', 'Debit'])
        
        # Update data
        sql = """
        UPDATE parking_transactions 
        SET exit_time = %s, duration_minutes = %s, payment_method = %s, amount = %s
        WHERE transaction_id = %s
        """
        cursor.execute(sql, (exit_time, duration, method, amount, trx_id))
        print(f"[KELUAR] ID: {trx_id} | Bayar: {amount}")

def main():
    print("--- Menghubungkan ke PostgreSQL (Port 5432) ---")
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()
    print("--- Simulasi Berjalan (Ctrl+C untuk stop) ---")
    
    try:
        while True:
            # 70% Mobil Masuk, 30% Mobil Keluar
            if random.random() < 0.7:
                mobil_masuk(cursor)
            else:
                mobil_keluar(cursor)
            
            conn.commit() # Wajib commit di Postgres
            time.sleep(0.5) # Delay sedikit agar mudah dipantau
            
    except KeyboardInterrupt:
        print("\nStop.")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    main()