# 04 — NRT vs SP & Latensi NRT (A-P1-007, A-P1-008)

> Fase 1 · Draf agen 2026-11-19 · Pemilik: R1 (Lanang) · Reviewer: R2 (Abi Funn)
> Sumber angka: `data/firms/profile/nrt_vs_sp.json` (skrip `scratch/phase1/compare_nrt_sp.py`) dan `latency.json` (`latency_report.py`). Data lokal, tidak di-commit.

## 1. Perbandingan NOAA-21 NRT vs SP (tumpang tindih 12 bulan)

**Jendela:** 2025-08-01 … 2026-07-31 (365 hari), baris di dalam provinsi saja. Hanya NOAA-21 yang punya NRT dan SP untuk tanggal yang sama; NRT NOAA-20 baru mulai 2026-08-01.

**Aturan pencocokan:** `acq_date` sama, |selisih `acq_time`| ≤ 2 menit, dan titik SP terdekat dalam radius ≤ 1 km.

| Ukuran | Nilai |
|---|---|
| Baris NRT / SP | 121.213 / 120.248 |
| NRT yang punya pasangan SP | **119.867 (98,9%)** |
| NRT tanpa pasangan | 1.346 (1,1%) |
| SP tanpa pasangan NRT | 718 (0,6%) |
| SP yang dipasangkan dengan >1 NRT | 337 |
| Kunci persis `(lat, lon, acq_time)` sama | **47.555 (39,2% dari NRT)** |
| Jarak posisi pasangan | p50 = p90 = p99 = 0 m; 99,6% tepat 0 m; maks 995 m |
| Selisih `acq_time` NRT − SP (menit) | −2: 5.145 · −1: 30.027 · **0: 47.749 (39,8%)** · +1: 29.820 · +2: 7.126 |
| FRP sama persis | 98,4% (selisih p1 = p50 = 0, p99 = 0,03 MW) |
| `bright_ti4` sama | p1 = p50 = p99 selisih 0 |
| Confidence sama | 99,9% (`n→l` 76, `l→n` 24, `h→l` 1) |
| `daynight` sama | 100% |
| Hari hanya ada di NRT / hanya di SP | 0 / 0 |
| Rasio jumlah harian NRT/SP | p5 1,00 · p50 1,00 · p95 1,04 |
| Hari dengan selisih terbesar | 2025-09-05: NRT 75 vs SP 422; 2026-03-11: 67 vs 128; 2026-03-30: 46 vs 85 |

Interpretasi (`RECOMMENDATION`):

1. **Isi NRT dan SP hampir identik.** Posisi, FRP, dan suhu sama. Perbedaannya hanya pada `acq_time`, yang bergeser ±1–2 menit pada ±60% deteksi, ditambah ±1% deteksi yang hanya ada di salah satu produk.
2. **Identitas berbasis kunci tidak bisa menghubungkan NRT dengan SP.** `detection_id` dari NRT tidak akan sama dengan `detection_id` SP untuk deteksi yang sama. Jika keduanya dimuat untuk tanggal yang sama, deteksi akan terhitung **dua kali**.
3. Hari dengan NRT jauh lebih sedikit dari SP (mis. 2025-09-05) cocok dengan peringatan S3 bahwa NRT bisa punya celah cakupan ("coverage gaps resulting from temporary interruptions in the NRT data processing chain"). Ini alasan tambahan untuk memakai SP bila tersedia.

## 2. Aturan tumpang tindih NRT/SP yang diusulkan (keputusan HD-10)

| Situasi | Aturan |
|---|---|
| **Backfill** | Untuk setiap `(satellite, acq_date UTC)`: pakai **SP** jika tanggal itu ≤ akhir ketersediaan SP (`data_availability`); jika tidak, pakai **NRT**. Satu tanggal tidak pernah memuat kedua produk sekaligus. |
| **Incremental (poller)** | Hanya NRT, untuk tanggal setelah akhir ketersediaan SP. |
| **Rekonsiliasi NRT→SP** (*Should*, A-P7-003) | Saat SP terbit untuk tanggal baru: ganti **seluruh** baris NRT `(satellite, acq_date UTC)` dengan SP, lalu hitung ulang agregat untuk **dua** tanggal lokal yang terdampak (tanggal UTC D berisi deteksi malam yang jatuh ke tanggal lokal D+1). Penghapusan NRT adalah operasi destruktif sehingga butuh persetujuan (HD-27). |
| **Identitas** | `detection_id` = hash `(processing_level, satellite, acq_datetime_utc, latitude, longitude)` pada presisi sumber. Kunci ini unik di dalam satu produk ([03 §6](03-profiling-report.md#6-duplikat--natural-key-per-sumber)). Masukan untuk A-P3-001. |
| **Data hilang di NRT** | Bila hari NRT sangat kurang dibanding pola biasa, laporkan saja dan jangan diperbaiki. SP akan menggantinya kelak. |

Opsi lain yang ditolak:
- **Pencocokan per deteksi (toleransi waktu/jarak) lalu update di tempat:** lebih rumit, tidak deterministik saat satu SP cocok dengan >1 NRT (337 kasus), dan tidak menambah akurasi karena isinya identik.
- **Menyimpan NRT dan SP berdampingan dan memilih saat query:** menggandakan volume dan membuat setiap query bergantung pada aturan pilih.

## 3. Latensi NRT (A-P1-008)

> **Status: SEMENTARA.** Poller berjalan sejak 2026-11-19 09:09 UTC, dengan interval 15 menit (2 request per poll: NOAA-20 dan NOAA-21 NRT, `DAY_RANGE` 2), dan berhenti sendiri ±2026-11-20 09:09 UTC. Bagian ini difinalkan setelah itu dengan `python -I scratch/phase1/latency_report.py`.

Metode: latensi = waktu poll pertama yang memuat deteksi − `acq_date`+`acq_time` (UTC). Resolusinya 15 menit. Yang dihitung hanya deteksi yang muncul **setelah** poll pertama, karena poll pertama memuat semua data yang sudah terbit.

Pengamatan sampai 2026-11-19 11:19 UTC (18 poll, semuanya HTTP 200):

| Pengamatan | NOAA-20 NRT | NOAA-21 NRT |
|---|---|---|
| Baris di poll pertama (09:09 UTC) | 474 | 584 |
| Akuisisi terbaru yang sudah ada di poll pertama | 2026-11-18 18xx UTC (lintasan malam lokal 19 Nov) | **2026-11-19 05xx UTC** (lintasan siang 19 Nov), artinya terbit ≤ ±4 jam setelah akuisisi |
| Deteksi baru setelah poll pertama | 0 | 0 |
| Data 2026-11-19 sampai 11:19 UTC | **Belum ada** (> 6 jam setelah lintasan siang NOAA-20 yang biasa terjadi 03–07 UTC) | Ada |
| Rekaman yang berubah nilai antar poll | 0 | 0 |

Yang sudah bisa disimpulkan: data NRT datang **per lintasan** (sekitar 2× sehari per satelit untuk Indonesia, siang 03–07 UTC dan malam 15–18 UTC), bukan mengalir terus. Polling 15–30 menit (OQ-10) lebih dari cukup untuk menangkap setiap batch. Angka latensi dan apakah rekaman NRT berubah setelah terbit masih menunggu akhir pengamatan.

## 4. Masukan untuk fase berikutnya

- **A-P3-001 (canonical event):** `processing_level` wajib masuk identitas. Tambahkan `source_acq_date_utc` untuk rekonsiliasi per tanggal.
- **B-P3-001 (access patterns):** operasi "hapus/ganti semua deteksi `(satellite, acq_date UTC)`" harus bisa dilayani tanpa scan. Rekonsiliasi butuh query per tanggal UTC, padahal partisi tampilan memakai tanggal lokal.
- **C-P2-001 (NFR):** ambang "data basi" sebaiknya dikaitkan dengan jadwal lintasan (> ±8 jam tanpa batch baru), bukan dengan interval polling.
