# 00 — Estimasi Volume per Kandidat Partisi (B-P1-001)

> Fase 1 · Draf agen 2026-11-19 · **Disetujui Lanang (R1) 2026-11-22** · Pemilik: R2 (Abi Funn) · Reviewer: R1 (Lanang) · Masukan untuk B-P3-001/002 (G3)
> Jumlah baris = **diukur** dari raw zone Fase 1 (`data/firms/profile/prov_day.csv`, `extra_checks.json`). Byte per baris di Cassandra = `ASSUMPTION` sampai diukur di B-P5-007. Batas ukuran partisi = `AI-PRIOR`, diverifikasi di B-P3-001.

## 1. Dasar perhitungan

- **Periode:** rekomendasi Fase 1 ([07](../../01-dataset/07-dataset-recommendation.md)): 2023-01-01 … 2026-11-18.
- **Produk:** NOAA-20 + NOAA-21; SP sampai 2026-07-31, NRT mulai 2026-08-01, tanpa tumpang tindih.
- **Cakupan:** hanya deteksi di dalam 38 provinsi. Titik `OUTSIDE` (±10–17%) disimpan di tabel event, tetapi tidak dihitung di partisi provinsi.
- **Tanggal:** tanggal lokal provinsi (WIB/WITA/WIT).
- **Total baris di dalam provinsi:** **2.233.114**, tersebar di 1.419 tanggal lokal. 66,8% dari semua kombinasi provinsi-hari punya ≥1 deteksi.

## 2. Distribusi baris per kandidat kunci partisi (diukur)

| Kandidat partisi (tabel detail deteksi) | Jumlah partisi | p50 | p90 | p99 | Maks | Puncak |
|---|---|---|---|---|---|---|
| **(province, local_date)**, kedua satelit | 36.005 | 8 | 100 | 970 | **13.217** | Kalimantan Tengah, 2026-10-22 |
| (province, local_date, satellite), maksimum per sumber | — | 5–36 | 37–350 | 247–2.434 | **7.831** | N21 NRT |
| (province, local_month), kedua satelit | 1.769 | 155 | 1.932 | 19.200 | **141.914** | Kalimantan Tengah, 2026-10 |
| (local_date), nasional | 1.419 | 358 | 3.764 | 17.381 | **24.507** | — |

Rincian per sumber untuk (province, local_date):

| Sumber | Partisi | p50 | p90 | p99 | Maks |
|---|---|---|---|---|---|
| N20 SP | 27.316 | 5 | 37 | 251 | 2.349 |
| N21 SP | 26.912 | 5 | 37 | 247 | 3.081 |
| N20 NRT | 3.626 | 36 | 350 | 2.434 | 7.434 |
| N21 NRT | 11.588 | 8 | 102 | 1.078 | 7.831 |

Bulan dan provinsi puncak, gabungan kedua satelit:
1. Kalimantan Tengah 2026-10: 141.914
2. Kalimantan Tengah 2026-09: 137.776
3. Kalimantan Barat 2026-08: 73.934
4. Papua Selatan 2026-10: 70.957
5. Kalimantan Tengah 2026-08: 59.744

Puncak di luar 2026 tertinggi adalah Sumatera Selatan 2023-10 (30.735). Penjelasan lonjakan 2026 ada di [03 §8](../../01-dataset/03-profiling-report.md#8-volume-per-waktu-di-dalam-indonesia).

## 3. Perkiraan ukuran (`ASSUMPTION`)

| Ukuran | Nilai | Dasar |
|---|---|---|
| Byte per baris CSV mentah | 80–84 B | Diukur (`profile.json`) |
| Byte per baris event di Cassandra (sebelum kompresi) | **±300–400 B** (`ASSUMPTION`) | ±20 kolom canonical ([06 §B](../../10-execution-plan/06-interface-contracts.md#b-etl--cassandra-canonical-event)) + overhead kolom/clustering. SHA-256 file sumber (64 karakter) per baris adalah porsi besar; bisa dipindah ke tabel file dan cukup direferensikan dengan `source_file_id` |
| Partisi (province, local_date) terbesar | ±4–5 MB | 13.217 × 300–400 B |
| Partisi (province, local_month) terbesar | ±43–57 MB | 141.914 × 300–400 B |
| Seluruh tabel event di dalam provinsi | ±0,7–0,9 GB | 2.233.114 × 300–400 B, RF = 1, sebelum kompresi |
| Tabel agregat harian per provinsi | ±54 ribu baris (38 × 1.419); ×6 bila dimensi confidence (3) × satelit (2) masuk kunci | — |

## 4. Implikasi untuk desain (masukan B-P3-001, `RECOMMENDATION`)

1. **Partisi per (province, local_date) aman**: maksimum ±13 ribu baris, ±5 MB. Batas umum yang sering dirujuk (partisi ≪ 100 MB, idealnya ≤ ±10 MB) berstatus `AI-PRIOR` dan perlu diverifikasi di B-P3-001.
2. **Partisi per (province, local_month) berisiko di musim puncak.** p50 hanya 155 baris, tetapi maksimumnya 141 ribu baris (±50 MB). Distribusinya sangat timpang (p99/p50 ≈ 124×). Ini kandidat alami untuk eksperimen bucketing yang *Must* (OQ-13): bandingkan bulan vs hari, atau bulan + bucket.
3. Partisi nasional per hari (maks 24,5 ribu baris) tidak diperlukan bila tampilan peta selalu per provinsi (C-11, HD-21).
4. Agregat sangat kecil (puluhan ribu baris), sehingga rebuild penuh dari detail realistis dilakukan setiap run.
5. **Laju incremental:** p50 ±360 deteksi/hari nasional, tetapi mencapai ±24.500/hari di puncak. Kedua angka ini perlu masuk NFR throughput poller (C-P2-001).
