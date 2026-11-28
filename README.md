# NusaFire — Indonesian Hotspot Intelligence

Aplikasi pemantauan deteksi hotspot satelit (NASA FIRMS) dan analitik event terdistribusi berbasis Apache Cassandra. Proyek universitas, 4 anggota, 21 hari.

> Hotspot adalah deteksi anomali termal oleh satelit, **bukan** konfirmasi kebakaran hutan/lahan.

## Status

Status terkini selalu ada di [docs/STATUS.md](docs/STATUS.md). Belum ada kode aplikasi.

## Dokumentasi

- **[Status & konteks proyek](docs/STATUS.md)**: mulai dari sini
- [Fase 0 — Project Discovery](docs/00-discovery/README.md)

## Struktur repo

Kepemilikan lengkap: [07-file-ownership-matrix](docs/10-execution-plan/07-file-ownership-matrix.md); penegakannya di [`.github/CODEOWNERS`](.github/CODEOWNERS).

| Direktori | Isi | Maintainer |
|---|---|---|
| [`pipeline/`](pipeline/) | Pipeline ingestion (backfill + incremental) | A (R1) |
| [`db/`](db/) | Migrasi, writer, agregat Cassandra | B (R2) |
| [`experiments/`](experiments/) | Eksperimen Cassandra + laporan | B (R2) |
| [`api/`](api/) | Backend FastAPI | C (R3) |
| [`deploy/`](deploy/) | Skrip env, smoke E2E, konfigurasi cloud | C (R3) |
| [`web/`](web/) | Frontend React + Leaflet | D (R4) |
| [`docs/`](docs/) | Dokumentasi dan spesifikasi | per subfolder |

Template PR: [`.github/pull_request_template.md`](.github/pull_request_template.md).

## Setup lokal

Salin `.env.example` menjadi `.env`, lalu isi `FIRMS_MAP_KEY`. File `.env` tidak pernah di-commit.
