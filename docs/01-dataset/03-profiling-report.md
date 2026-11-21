# 03 — Laporan Profiling Dataset (A-P1-004)

> Fase 1 · Draf agen 2026-11-19 · Pemilik: R1 (Lanang) · Reviewer: R2 (Abi Funn)
> Semua angka **diukur** dari raw zone Fase 1. Sumber angka (lokal, tidak di-commit): `data/firms/profile/profile.json`, `extra_checks.json`, `daily_counts.csv`, `prov_day.csv`, `prov_month.csv`, `coord_assign.csv`.
> Reproduksi: `python -I scratch/phase1/pip_assign.py`, lalu `profile_firms.py`, lalu `extra_checks.py` (tanpa panggilan API).

## 1. Cakupan unduhan

| Sumber | File | Baris (bbox) | Byte CSV | Rentang `acq_date` (UTC) | Hari |
|---|---|---|---|---|---|
| `VIIRS_NOAA20_SP` | 262 | 626.944 | 50.421.754 | 2023-01-01 … 2026-07-31 | 1.308 |
| `VIIRS_NOAA21_SP` | 250 | 617.599 | 49.695.885 | 2023-03-01 … 2026-07-31 | 1.249 |
| `VIIRS_NOAA20_NRT` | 22 | 664.101 | 55.529.078 | 2026-08-01 … 2026-11-18 | 110 |
| `VIIRS_NOAA21_NRT` | 95 | 797.261 | 66.692.258 | 2025-08-01 … 2026-11-18 | 475 |
| **Total** | **629** | **2.705.905** | **222.338.975** | | |

- Ukuran ±80–84 byte per baris CSV. Semua request HTTP 200, dan semua SHA-256 cocok dengan manifest (diverifikasi ulang 2026-11-19).
- Jendela waktu sesuai permintaan: 0 baris di luar tanggal yang diminta di keempat sumber.
- NOAA-21 NRT sengaja diunduh mulai 2025-08-01 supaya ada 12 bulan tumpang tindih dengan SP ([04](04-nrt-vs-sp-and-latency.md)).

## 2. Kelengkapan

| Ukuran | Hasil |
|---|---|
| Nilai kosong | 0 di semua kolom, semua sumber |
| Nilai non-numerik di kolom numerik | 0 |
| `acq_time` invalid (jam > 23 atau menit > 59) | 0 |
| Confidence di luar `l`/`n`/`h` | 0 |
| `version` tidak sesuai sumber | 0 |

### Hari tanpa data vs tabel resmi `missing_data` FIRMS

| Sumber | Hari yang dicantumkan FIRMS sebagai hilang (di rentang unduhan) | Hari dengan 0 baris di bbox | Selisih |
|---|---|---|---|
| NOAA-20 SP | 2023-07-19, 07-20, 07-21, 07-22, 2023-09-30, 2024-02-04 (6) | 6, persis sama | 2024-02-05: 2 baris di bbox, 0 di Indonesia (`UNKNOWN`: lintasan parsial atau memang tidak ada deteksi) |
| NOAA-21 SP | 2024-02-27 … 2024-03-06 (9) | 2024-02-27, 02-28 (2) | 7 hari tercantum tetapi berisi 62–138 baris → **data parsial**, bukan kosong |
| NOAA-20 NRT, NOAA-21 NRT | — | 0 | — |

Kesimpulannya, hari kosong selalu tercantum di tabel `missing_data`. Sebaliknya, tidak semua hari yang tercantum kosong: sebagian hanya parsial. Aturannya ada di DQ-12 ([06](06-data-quality-rules.md)).

## 3. Rentang nilai (bbox, semua baris)

| Kolom | NOAA-20 SP p1 / p50 / p99 (min–maks) | NOAA-20 NRT p1 / p50 / p99 (min–maks) |
|---|---|---|
| `bright_ti4` (K) | 298,13 / 334,04 / 367,0 (207,93–367,0) | 298,48 / 333,01 / 367,0 (207,93–367,0) |
| `bright_ti5` (K) | 269,42 / 294,9 / 311,06 (232,1–376,43) | 270,34 / 294,88 / 312,33 (229,55–375,3) |
| `scan` | 0,32 / 0,43 / 0,73 (0,32–0,80) | 0,32 / 0,43 / 0,73 (0,32–0,80) |
| `track` | 0,36 / 0,43 / 0,76 (0,36–0,78) | 0,36 / 0,42 / 0,76 (0,36–0,78) |
| `frp` (MW) | 0,47 / 4,51 / 51,70 (0,09–954,79) | 0,54 / 4,13 / 58,06 (0,0–1.081,07) |

NOAA-21 berada di rentang yang sama (lihat `profile.json`).

| Pemeriksaan nilai | N20 SP | N21 SP | N20 NRT | N21 NRT |
|---|---|---|---|---|
| `bright_ti4` = 367,0 (saturasi, S3) | 16.647 | 19.762 | 36.359 | 34.042 |
| `bright_ti4` < 280 K | 209 | 185 | 227 | 296 |
| `bright_ti4` < `bright_ti5` | 726 | 889 | 778 | 1.146 |
| `frp` = 0 | 0 | 9 | 3 | 17 |
| `frp` > 500 MW | 14 | 17 | 16 | 33 |

Batas bawah `bright_ti4` ±208 K cocok dengan rentang data layer di S3 ("» 208 : 367"). Nilai < 280 K dan `ti4` < `ti5` tidak didefinisikan sebagai error di sumber resmi, jadi baris-baris itu hanya dilaporkan, **tidak** ditolak.

## 4. Kategori (di dalam Indonesia)

| Ukuran | N20 SP | N21 SP | N20 NRT | N21 NRT |
|---|---|---|---|---|
| Baris di dalam provinsi | 522.181 | 515.508 | 601.541 | 715.510 |
| Siang / malam | 74,2% / 25,8% | 74,1% / 25,9% | 53,1% / 46,9% | 56,7% / 43,3% |
| Confidence `l` / `n` / `h` | 6,4% / 91,0% / 2,5% | 6,6% / 90,3% / 3,1% | 5,4% / 91,6% / 2,9% | 5,8% / 90,7% / 3,5% |
| `l` pada malam hari | 0 | 0 | 0 | 0 |
| FRP p50 / p90 / p99 (MW) | 4,55 / 14,76 / 52,29 | 5,41 / 17,24 / 58,72 | 4,07 / 15,07 / 58,67 | 4,89 / 17,34 / 65,65 |

Tidak adanya `l` di malam hari sesuai S1: piksel malam berconfidence rendah hanya ada di wilayah anomali Atlantik Selatan, dan sudah dihapus dari data FIRMS.

## 5. Waktu: UTC vs tanggal lokal

Zona waktu diterapkan per provinsi: WIB untuk kode 11–36, 61, 62; WITA untuk 51–53, 63–65, 71–76; WIT untuk 81, 82, 91–96 (OQ-08).

| Ukuran | N20 SP | N21 SP | N20 NRT | N21 NRT |
|---|---|---|---|---|
| Deteksi malam dengan tanggal lokal ≠ tanggal UTC | 134.072 dari 134.518 (99,7%) | 132.729 dari 133.484 (99,4%) | 282.159 dari 282.183 | 307.905 dari 309.534 |
| Deteksi siang dengan tanggal lokal ≠ UTC | 0 | 0 | 0 | 0 |
| Porsi seluruh baris Indonesia yang tanggalnya bergeser | 25,7% | 25,7% | 46,9% | 43,0% |

Implikasinya: agregasi berdasarkan tanggal UTC akan memindahkan ±¼ (SP) sampai ±½ (NRT 2026) deteksi ke hari yang salah. Agregasi wajib memakai tanggal lokal (keputusan OQ-08 terkonfirmasi perlu).

## 6. Duplikat & natural key (per sumber)

| Kandidat kunci | N20 SP | N21 SP | N20 NRT | N21 NRT |
|---|---|---|---|---|
| Baris identik penuh | 0 | 0 | 0 | 0 |
| **K1** `(lat, lon, acq_date, acq_time, satellite)` berulang | 0 | 1 (nilai berbeda) | 1 (nilai berbeda) | 0 |
| **K2** `(lat, lon, acq_date)` muncul >1 kali dalam satu hari UTC | 1 | 2 | 2 | 2 |

- K1 praktis unik **di dalam satu produk**, sehingga cocok sebagai dasar `detection_id` (dengan `processing_level` di dalamnya).
- Dua tabrakan K1 dengan nilai berbeda ditangani deterministik (DQ-08).
- K1 **tidak** cocok untuk mencocokkan NRT dengan SP, karena `acq_time` bisa bergeser ±2 menit ([04](04-nrt-vs-sp-and-latency.md)).
- Deteksi NOAA-20 dan NOAA-21 untuk kebakaran yang sama adalah **dua deteksi berbeda**, bukan duplikat. Satelit dipisahkan lewat filter, bukan dedup.

## 7. Penetapan wilayah (BIG kab/kota edisi Juni 2026, generalisasi 0,001°)

Diuji pada 2.555.369 koordinat unik dari semua sumber: 2.234.753 masuk poligon, dan 101 jatuh di dua poligon sekaligus.

| Status | N20 SP | N21 SP | N20 NRT | N21 NRT |
|---|---|---|---|---|
| Di dalam provinsi | 522.181 (83,3%) | 515.508 (83,5%) | 601.541 (90,6%) | 715.510 (89,7%) |
| Di luar, ≤ 0,5 km dari tepi | 1.854 | 1.658 | 1.092 | 1.378 |
| Di luar, 0,5–2 km | 1.038 | 1.013 | 1.900 | 1.749 |
| Di luar, 2–11 km | 5.831 | 5.590 | 11.678 | 10.556 |
| Di luar, > 11 km (negara tetangga/laut) | 96.040 | 93.830 | 47.890 | 68.068 |
| Kena dua poligon (diambil yang pertama) | 30 | 16 | 34 | 26 |

- **Semua 38 kode provinsi** (11 … 96) muncul di data.
- Di luar provinsi dengan jarak ≤ 0,5 km, mayoritas SP bertipe 3/offshore (N20: 1.037 dari 1.854). Artinya titik itu memang di atas air, bukan salah generalisasi.
- Titik bertipe 0 (vegetasi) yang ≤ 2 km di luar poligon hanya 1.625 untuk N20 SP (0,3%).

## 8. Volume per waktu (di dalam Indonesia)

**Periode rekomendasi:** SP sampai 2026-07-31, lalu NRT mulai 2026-08-01, NOAA-20 + NOAA-21.

| Ukuran | p50 | p90 | p99 | Maks |
|---|---|---|---|---|
| Deteksi nasional per hari lokal | 358 | 3.764 | 17.381 | 24.507 |
| Per provinsi-hari (hanya hari yang ada deteksi) | 8 | 100 | 970 | 13.217 (Kalimantan Tengah, 2026-10-22) |
| Per provinsi-bulan | 155 | 1.932 | 19.200 | 141.914 (Kalimantan Tengah, 2026-10) |

Total di dalam Indonesia: **2.233.114 baris**. Detail per kandidat partisi ada di [00-volume-estimates](../03-specs/database/00-volume-estimates.md).

### Lonjakan Agustus–Oktober 2026 (`VERIFIED` sebagai angka, penyebab `UNKNOWN`)

| Bulan lokal (NOAA-20, di dalam Indonesia) | 2023 (SP) | 2024 (SP) | 2025 (SP) | 2026 (NRT) |
|---|---|---|---|---|
| Agustus | 42.091 | 17.210 | 18.369 | 142.921 |
| September | 70.283 | 33.462 | 20.348 | 211.070 |
| Oktober | 77.260 | 23.135 | 14.992 | 222.973 |

- Musim 2026 tercatat ±3× musim 2023, dengan kontributor terbesar Kalimantan Tengah (Oktober 2026: 73.663 deteksi NOAA-20), lalu Papua Selatan dan Sumatera Selatan. Pola yang sama muncul di NOAA-21 NRT.
- **Lonjakan ini tidak dijelaskan oleh perbedaan NRT vs SP.** Pada 12 bulan tumpang tindih, rasio harian NRT/SP berada di p50 1,00 dan p95 1,04 ([04](04-nrt-vs-sp-and-latency.md)).
- Apakah ini musim kebakaran yang luar biasa belum diverifikasi dengan sumber luar (`UNKNOWN`). Data SP untuk periode ini baru tersedia sekitar 5 bulan lagi, dan saat itu angkanya bisa dicek ulang.
- Dampaknya ke desain: angka maksimum volume (§8) didominasi data 2026, sehingga estimasi partisi **harus** memakai periode ini.
