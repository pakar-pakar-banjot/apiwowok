# 01 — Source Inventory (P1-01)

> Fase 1 · Diperiksa 2026-11-19 · Label sesuai [legenda](../00-discovery/README.md#label-status-informasi)

## 1. Sumber data hotspot: NASA FIRMS (keputusan OQ-28)

| Source ID (Area API) | Satelit | Jenis | Ketersediaan (`data_availability`, 2026-11-19) | Dipakai untuk | Status |
|---|---|---|---|---|---|
| `VIIRS_NOAA20_SP` | NOAA-20 (`N20`) | Standard Processing (arsip, kualitas sains) | 2018-04-01 … 2026-07-31 | Backfill utama | `VERIFIED` |
| `VIIRS_NOAA20_NRT` | NOAA-20 | Near Real-Time | 2026-08-01 … 2026-11-18 | Backfill sesudah SP + polling | `VERIFIED` |
| `VIIRS_NOAA21_SP` | NOAA-21 (`N21`) | Standard Processing | 2023-03-01 … 2026-07-31 | Backfill kedua | `VERIFIED` |
| `VIIRS_NOAA21_NRT` | NOAA-21 | Near Real-Time | 2024-01-17 … 2026-11-19 | Polling; tumpang tindih dengan SP 2024-01-17 … 2026-07-31. Fase 1 mengunduh NRT mulai 2025-08-01 untuk perbandingan 12 bulan ([04](04-nrt-vs-sp-and-latency.md)) | `VERIFIED` |
| `VIIRS_SNPP_*`, `MODIS_*` | S-NPP, Terra/Aqua | — | S-NPP berhenti 2026-11-02 | **Tidak dipakai** (OQ-04) | `VERIFIED` |

### 1.1 Mekanisme akses

| Aspek | Nilai | Status / bukti |
|---|---|---|
| Endpoint | `GET https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{SOURCE}/{W,S,E,N}/{DAY_RANGE}[/{DATE}]` | `VERIFIED` (halaman API + uji) |
| Semantik `DATE` | **Tanggal awal**: data `DATE … DATE + DAY_RANGE − 1`. Tanpa `DATE`: hari ini mundur `DAY_RANGE − 1` hari. | `VERIFIED` (halaman `/api/area/`) + diamati: tidak ada baris di luar jendela yang diminta (lihat [03](03-profiling-report.md)) |
| `DAY_RANGE` | 1–5 | `VERIFIED` |
| Kuota | 5000 transaksi / 10 menit. "Larger transactions may count as multiple requests (ex. requesting 7 days)". | `VERIFIED` (halaman API) |
| **Biaya transaksi terukur** | Bounding box Indonesia: 1 hari = **2 transaksi**, 5 hari = **10 transaksi** (`mapkey_status` sebelum/sesudah). Jadi 1 tahun backfill = 73 request ≈ **730 transaksi** per sumber. | `VERIFIED` (diukur 2026-11-19). Apakah biaya juga bergantung pada luas area masih `UNKNOWN`. |
| Cek kuota | `GET /mapserver/mapkey_status/?MAP_KEY=…` → `transaction_limit`, `current_transactions`, `transaction_interval` | `VERIFIED` |
| Hari data hilang | Halaman `/api/missing_data/`. Datanya dimuat lewat `?action=fetch_data` (JSON berisi tabel HTML). Endpoint ini internal dan tidak terdokumentasi, sehingga kestabilannya `UNKNOWN`. | `VERIFIED` (diambil 2026-11-19) |
| Format | CSV, header di baris pertama, koma sebagai pemisah, tanpa kutip | `VERIFIED` |
| Latensi NRT | "Global data are available within 3 hours of satellite observation" | `VERIFIED` (halaman FIRMS). Pengamatan Indonesia: [04](04-nrt-vs-sp-and-latency.md) |
| Penggantian NRT | "Near Real-Time (NRT) data are replaced with standard science quality data as they become available (with approximately a 5 month lag)" | `VERIFIED` (halaman Download) |

### 1.2 Lisensi, atribusi, disclaimer

- Kebijakan NASA: "NASA supports full and open sharing of data". Data FIRMS bebas dipakai, termasuk di aplikasi publik. `VERIFIED` (halaman FIRMS, dengan tautan ke kebijakan data NASA)
- **Atribusi** (untuk footer aplikasi dan README): halaman FIRMS bagian *Acknowledgments* memuat kalimat yang diawali "We acknowledge the use of data and/or imagery from NASA's Fire Information for Resource Management System (FIRMS)" dan menyebut "part of NASA's Land, Atmosphere Near real-time Capability for Earth observations (LANCE) … and NASA's Earth Science Data and Information System (ESDIS)".
  - Potongan-potongan itu `VERIFIED`. Kalimat lengkapnya disalin langsung dari halaman saat UI dibuat (Fase 5), bukan dari dokumen ini.
- Disclaimer: data disediakan "as is", dan pengguna menanggung seluruh tanggung jawab atas penggunaannya. `VERIFIED`
- Disclaimer ilmiah proyek (hotspot ≠ kebakaran terkonfirmasi) tetap berlaku dari charter. Halaman FIRMS yang dibaca tidak memuat kalimat itu secara eksplisit. Namun karena atribut confidence dan `type` (sumber statis/vulkan/offshore) ada, deteksi memang bukan konfirmasi kebakaran.

## 2. Sumber batas wilayah

Diringkas dari [05-boundary-sources.md](05-boundary-sources.md):

| Sumber | Provinsi | Lisensi | Rekomendasi |
|---|---|---|---|
| BIG `BATAS_KABKOTA_AR`, edisi Juni 2026 | 38 | `UNKNOWN` (perlu konfirmasi) | **Utama** |
| HDX COD-AB (BPS/OCHA) | 34 | CC BY-IGO | Cadangan |
| geoBoundaries gbOpen | 34 | ODbL 1.0 | Tidak dipakai |
| GADM | `UNKNOWN` | Non-komersial, tanpa redistribusi | Tidak dipakai |

## 3. Data lokal hasil Fase 1 (tidak di-commit)

| Path | Isi |
|---|---|
| `data/firms/raw/{SOURCE}/{YYYY-MM-DD}_{N}d.csv` | Respons mentah Area API, satu file per request (bbox `94,-11.5,141.5,6.5`) |
| `data/firms/manifest.csv` | Per file: source, tanggal awal, jumlah hari, HTTP, jumlah baris, byte, **SHA-256**, waktu ambil (UTC) |
| `data/firms/missing_data.json` | Snapshot tabel hari data hilang FIRMS |
| `data/firms/latency/` | Log poller latensi NRT (P1-10) |
| `data/firms/profile/` | Keluaran profiling (JSON/CSV) |
| `data/boundaries/big_kabkota_2026_06_off0.001/` | 22 bagian GeoJSON batas kab/kota BIG |

Skrip sekali pakai ada di `scratch/phase1/` dan membaca `FIRMS_MAP_KEY` dari `.env` tanpa mencetaknya. Statusnya sebagai alat bantu Fase 1, bukan kode aplikasi. Apakah skrip ini perlu di-commit diputuskan di G1.
