CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT,
    action TEXT,
    record_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
