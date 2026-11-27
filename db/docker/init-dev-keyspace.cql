-- Keyspace dev untuk pengembangan lokal (B-P4-001).
-- Tanpa skema produksi; skema CQL final baru ditetapkan setelah G3 (B-P3-002).
CREATE KEYSPACE IF NOT EXISTS nusafire_dev
  WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
  };
