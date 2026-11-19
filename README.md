# NusaFire — Indonesian Hotspot Intelligence

Aplikasi pemantauan deteksi hotspot satelit (NASA FIRMS) dan analitik event terdistribusi berbasis Apache Cassandra. Proyek universitas, 4 anggota, 21 hari.

> Hotspot adalah deteksi anomali termal oleh satelit, **bukan** konfirmasi kebakaran hutan/lahan.

## Status

Fase 0 selesai (G0 disetujui 2026-11-19). Berikutnya: Fase 1 — Dataset Feasibility. Belum ada kode aplikasi.

## Dokumentasi

- **[Status & konteks proyek](docs/STATUS.md)**: mulai dari sini
- [Fase 0 — Project Discovery](docs/00-discovery/README.md)

## Setup lokal

Salin `.env.example` menjadi `.env`, lalu isi `FIRMS_MAP_KEY`. File `.env` tidak pernah di-commit.
