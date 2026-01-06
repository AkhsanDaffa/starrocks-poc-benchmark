import mysql.connector
import time
import random
from faker import Faker
from datetime import datetime

# --- KONFIGURASI KONEKSI MYSQL (SUMBER) ---
db_config = {
    'host': 'localhost',
    'user': 'root',           
    'password': '',           # Kosongkan sesuai request
    'database': 'zim_analytics', # Nama DB Anda
    'port': 3306              # Port standar MySQL dari docker-compose
}

fake = Faker('id_ID')

def get_connection():
    # Menangani error jika database belum siap saat docker baru nyala
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"Error koneksi: {err}")
        return None

def mobil_masuk(cursor):
    entry_time = datetime.now()
    plat = f"{random.choice(['B', 'D', 'F', 'L'])} {random.randint(1000, 9999)} {fake.lexify(text='???').upper()}"
    tipe = random.choice(['Motor', 'Mobil'])
    lokasi = random.choice(['Mall A', 'Mall B', 'Office Park'])
    
    # Perhatikan: tidak ada transaction_id di sini karena AUTO_INCREMENT
    sql = """
    INSERT INTO parking_transactions 
    (entry_time, vehicle_plate, vehicle_type, location) 
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (entry_time, plat, tipe, lokasi))
    print(f"[MASUK] {plat} ({tipe}) di {lokasi}")

def mobil_keluar(cursor):
    # Cari mobil yang exit_time-nya NULL
    cursor.execute("SELECT transaction_id, entry_time, vehicle_type FROM parking_transactions WHERE exit_time IS NULL ORDER BY RAND() LIMIT 1")
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
    print("--- Menghubungkan ke MySQL (Port 3306) ---")
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()
    print("--- Simulasi Berjalan (Ctrl+C untuk stop) ---")
    
    try:
        while True:
            if random.random() < 0.7:
                mobil_masuk(cursor)
            else:
                mobil_keluar(cursor)
            
            conn.commit()
            time.sleep(0.2) # Sedikit lebih cepat biar data cepat banyak
            
    except KeyboardInterrupt:
        print("\nStop.")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    main()


# Version 2

# import mysql.connector
# import random
# from faker import Faker
# from datetime import datetime, timedelta
# import time

# # --- KONFIGURASI DATABASE ---
# db_config = {
#     'host': 'localhost', # Ganti dengan IP Server Anda
#     'user': 'root',
#     'password': '',
#     'database': 'zim_analytics',
#     'port': 3306
# }

# # --- KONFIGURASI TARGET ---
# TARGET_BULK_ROWS = 100000  # Target data awal (100rb)
# BATCH_SIZE = 5000          # Sekali kirim 5000 data (Biar MySQL gak keselek)

# fake = Faker('id_ID')

# def get_connection():
#     return mysql.connector.connect(**db_config)

# def generate_bulk_data(cursor):
#     print(f"\n🚀 MEMULAI MODE BOOSTER: Generate {TARGET_BULK_ROWS} data secepat kilat...")
    
#     sql = """
#     INSERT INTO parking_transactions 
#     (entry_time, vehicle_plate, vehicle_type, exit_time, duration_minutes, payment_method, amount, location, created_at, updated_at) 
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """
    
#     buffer_data = []
#     start_time = time.time()
    
#     for i in range(TARGET_BULK_ROWS):
#         # Simulasi data historis (30 hari terakhir)
#         entry_time = fake.date_time_between(start_date='-30d', end_date='now')
        
#         # 80% data sudah selesai parkir (ada exit_time), 20% masih parkir (NULL)
#         if random.random() < 0.8:
#             duration = random.randint(10, 300) # menit
#             exit_time = entry_time + timedelta(minutes=duration)
#             v_type = random.choice(['Motor', 'Mobil'])
#             tarif = 2000 if v_type == 'Motor' else 5000
#             amount = tarif * (duration // 60 + 1)
#             method = random.choice(['Cash', 'QRIS', 'Debit', 'E-Wallet'])
#         else:
#             # Masih parkir
#             exit_time = None
#             duration = None
#             amount = None
#             method = None
#             v_type = random.choice(['Motor', 'Mobil'])

#         plat = f"{random.choice(['B', 'D', 'F', 'L'])} {random.randint(1000, 9999)} {fake.lexify(text='???').upper()}"
#         lokasi = random.choice(['Mall A', 'Mall B', 'Office Park', 'Pasar Modern'])
        
#         # Masukkan ke buffer
#         buffer_data.append((entry_time, plat, v_type, exit_time, duration, method, amount, lokasi, entry_time, entry_time))
        
#         # Jika buffer penuh, tembak ke database
#         if len(buffer_data) >= BATCH_SIZE:
#             cursor.executemany(sql, buffer_data)
#             print(f"   -> Terkirim {i+1} data...")
#             buffer_data = [] # Kosongkan buffer

#     # Kirim sisa data di buffer
#     if buffer_data:
#         cursor.executemany(sql, buffer_data)
    
#     elapsed = time.time() - start_time
#     print(f"✅ SELESAI! {TARGET_BULK_ROWS} data masuk dalam {elapsed:.2f} detik.")
#     print(f"⚡ Kecepatan rata-rata: {TARGET_BULK_ROWS / elapsed:.0f} rows/detik")

# def mode_realtime(conn, cursor):
#     print("\n🔄 Masuk ke MODE REAL-TIME (Simulasi Transaksi Berjalan)...")
#     print("   Tekan Ctrl+C untuk STOP.")
    
#     try:
#         while True:
#             # Logika Insert Satu per Satu (seperti script lama)
#             entry_time = datetime.now()
#             plat = f"{random.choice(['B', 'D', 'F', 'L'])} {random.randint(1000, 9999)} {fake.lexify(text='???').upper()}"
#             tipe = random.choice(['Motor', 'Mobil'])
#             lokasi = random.choice(['Mall A', 'Mall B', 'Office Park'])
            
#             cursor.execute("""
#                 INSERT INTO parking_transactions (entry_time, vehicle_plate, vehicle_type, location, created_at) 
#                 VALUES (%s, %s, %s, %s, NOW())
#             """, (entry_time, plat, tipe, lokasi))
            
#             conn.commit()
#             time.sleep(0.05) # Cepat tapi wajar (20 transaksi/detik)
            
#     except KeyboardInterrupt:
#         print("\n🛑 Simulasi dihentikan.")

# def main():
#     conn = get_connection()
#     if conn:
#         cursor = conn.cursor()
        
#         # 1. Jalankan Bulk Load dulu
#         generate_bulk_data(cursor)
#         conn.commit() # Commit besar
        
#         # 2. Lanjut simulasi real-time
#         mode_realtime(conn, cursor)
        
#         cursor.close()
#         conn.close()

# if __name__ == "__main__":
#     main()