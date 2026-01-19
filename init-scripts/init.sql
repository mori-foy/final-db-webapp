CREATE TABLE IF NOT EXISTS color_entries (
  id SERIAL PRIMARY KEY,
  entry_date DATE NOT NULL,
  color_code VARCHAR(7) NOT NULL,
  memo TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO color_entries (entry_date, color_code, memo) VALUES
(CURRENT_DATE, '#3A7BD5', 'サンプル：落ち着いた日');
