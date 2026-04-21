import json
import mysql.connector
from kafka import KafkaConsumer
from datetime import datetime
# Konfigurasi Kafka
KAFKA_CONFIG = {
    'bootstrap_servers': 'localhost:9092',
    'topic': 'parkiran.zim_analytics.parking_transactions',
    'group_id': 'starrocks-consumer'
}
# Konfigurasi StarRocks
STARROCKS_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'zim_analytics',
    'port': 9030
}
def get_starrocks_conn():
    return mysql.connector.connect(**STARROCKS_CONFIG)
def consume_and_load():
    print("=== Kafka Consumer: Parkir Topic -> StarRocks ===")
    print(f"Topic: {KAFKA_CONFIG['topic']}")
    print("Menunggu data dari Kafka...")
    
    consumer = KafkaConsumer(
        KAFKA_CONFIG['topic'],
        bootstrap_servers=KAFKA_CONFIG['bootstrap_servers'],
        group_id=KAFKA_CONFIG['group_id'],
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        enable_auto_commit=True
    )
    
    conn = get_starrocks_conn()
    cursor = conn.cursor()
    
    batch = []
    batch_size = 100
    
    for message in consumer:
        data = message.value
        batch.append((
            data.get('transaction_id'),
            data.get('entry_time'),
            data.get('vehicle_plate'),
            data.get('vehicle_type'),
            data.get('exit_time'),
            data.get('duration_minutes'),
            data.get('payment_method'),
            data.get('amount'),
            data.get('location'),
            data.get('created_at'),
            data.get('updated_at')
        ))
        
        if len(batch) >= batch_size:
            insert_batch(cursor, batch)
            batch = []
    
    # Insert sisa batch
    if batch:
        insert_batch(cursor, batch)
    
    cursor.close()
    conn.close()
def insert_batch(cursor, batch, conn):
    sql = """
    INSERT INTO parking_transactions 
    (transaction_id, entry_time, vehicle_plate, vehicle_type, exit_time, 
     duration_minutes, payment_method, amount, location, created_at, updated_at) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.executemany(sql, batch)
        conn.commit()
        print(f"✅ Inserted {len(batch)} rows to StarRocks")
    except Exception as e:
        print(f"❌ Error: {e}")
if __name__ == "__main__":
    consume_and_load()