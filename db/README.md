# Database Dev Environment — NusaFire (B-P4-001)

Konfigurasi Cassandra single-node untuk pengembangan lokal dan integrasi awal layanan backend.

## 1. Versi & Asumsi Stack

- **Image Cassandra:** `cassandra:5.0.9`
  - Status: `ASSUMPTION` (menunggu konfirmasi resmi pada `ADR-001` di tugas `C-P3-001` yang belum selesai saat `B-P4-001` dikerjakan).
  - Dasar pemilihan: tag `5.0.x` tercantum pada [dokumen 07](../docs/00-discovery/07-three-node-laptop-spec.md) (`VERIFIED`), dan image lokal `cassandra:latest` terverifikasi menjalankan `5.0.9` (`VERIFIED`).
- **Heap JVM:** `MAX_HEAP_SIZE=1G` (`mem_limit: 2g`, `cpus: "2.0"`)
  - Mekanisme terverifikasi (`VERIFIED`) dengan membaca `/etc/cassandra/cassandra-env.sh` di dalam image `5.0.9`: Cassandra 5.0 memakai G1GC secara default, sehingga hanya `MAX_HEAP_SIZE` yang diset dan `HEAP_NEWSIZE` dibiarkan tidak diset (jika diset pada G1GC, `cassandra-env.sh` mencetak peringatan dan mengabaikannya).
- **Keyspace dev:** `nusafire_dev` (`SimpleStrategy`, `replication_factor: 1`) dibuat secara idempoten melalui `db/docker/init-dev-keyspace.cql`. **Belum ada skema tabel produksi** pada tahap ini (skema final menunggu `B-P3-002` setelah G3).

## 2. Struktur File

- `db/docker/docker-compose.cassandra.yml` — Fragmen Docker Compose single-node (image terkunci, heap 1 GB, healthcheck `cqlsh`, volume persisten `cassandra_data`).
- `db/docker/init-dev-keyspace.cql` — Inisialisasi keyspace dev (`nusafire_dev`) secara idempoten.
- `db/scripts/wait-for-cassandra.sh` — Skrip readiness; melakukan polling `cqlsh -e 'describe keyspaces'` dan keluar dengan kode `0` jika siap sebelum timeout (default `180` detik).
- `db/scripts/init-dev-keyspace.sh` — Menjalankan `wait-for-cassandra.sh` lalu menerapkan `init-dev-keyspace.cql`.

## 3. Cara Menjalankan & Verifikasi

Dari root repository (atau worktree aktif):

```bash
# 1. Jalankan container Cassandra single-node
docker compose -f db/docker/docker-compose.cassandra.yml up -d

# 2. Tunggu hingga Cassandra siap (exit 0)
./db/scripts/wait-for-cassandra.sh

# 3. (Opsional) Inisialisasi keyspace dev nusafire_dev
./db/scripts/init-dev-keyspace.sh

# 4. Verifikasi langsung dengan cqlsh
docker exec nusafire-cassandra-dev cqlsh -e "describe keyspaces"

# 5. Hentikan container (tambah -v jika ingin menghapus volume data)
docker compose -f db/docker/docker-compose.cassandra.yml down
```

Variabel lingkungan opsional untuk skrip:
- `CASSANDRA_CONTAINER` (default: `nusafire-cassandra-dev`)
- `TIMEOUT_SECONDS` (default: `180`)
- `POLL_INTERVAL` (default: `5`)

## 4. Serah-Terima ke Role C (`C-P4-004`)

- Role C dapat menyertakan fragmen `db/docker/docker-compose.cassandra.yml` ke `docker-compose.yml` utama (mis. melalui `include:` atau `-f`).
- Gunakan `service_healthy` pada `depends_on` untuk service backend, atau panggil `db/scripts/wait-for-cassandra.sh` di skrip startup/CI.
