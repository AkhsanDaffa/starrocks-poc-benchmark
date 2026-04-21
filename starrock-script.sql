SHOW BACKENDS;

-- ALTER SYSTEM ADD BACKEND "starrocks-be:9050";

ALTER SYSTEM ADD BACKEND "172.25.0.4:9050";


CREATE DATABASE IF NOT EXISTS zim_analytics;

-- DROP TABLE IF EXISTS parking_transactions;

USE zim_analytics;

CREATE TABLE parking_transactions (
    transaction_id INT, -- Ini jadi Primary Key
    entry_time DATETIME,
    vehicle_plate VARCHAR(20),
    vehicle_type VARCHAR(10),
    exit_time DATETIME,
    duration_minutes INT,
    payment_method VARCHAR(20),
    amount DECIMAL(10, 2),
    location VARCHAR(50),
    created_at DATETIME,
    updated_at DATETIME
) ENGINE=OLAP
PRIMARY KEY(transaction_id) -- Wajib untuk CDC
DISTRIBUTED BY HASH(transaction_id) BUCKETS 10
PROPERTIES (
    "replication_num" = "1" -- Karena cuma 1 node (single backend)
);
