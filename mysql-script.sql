DROP TABLE IF EXISTS parking_transactions;

USE zim_analytics;

CREATE TABLE parking_transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    entry_time DATETIME,
    vehicle_plate VARCHAR(20),
    vehicle_type VARCHAR(10),
    exit_time DATETIME NULL,
    duration_minutes INT NULL,
    payment_method VARCHAR(20) NULL,
    amount DECIMAL(10, 2) NULL,
    location VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- DESC parking_transactions;
-- 
TRUNCATE TABLE parking_transactions;

SELECT COUNT(*) FROM parking_transactions;