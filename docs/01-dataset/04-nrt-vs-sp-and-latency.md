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

> **Status: FINAL** (pengamatan selesai). Poller berjalan 2026-11-19 09:09 UTC … 2026-11-20 08:42 UTC: 106 request, semuanya HTTP 200, 2 request per poll (NOAA-20 dan NOAA-21 NRT, `DAY_RANGE` 2), interval 15 menit. Rencananya diperpanjang sampai 14:30 UTC (HD-22), tetapi proses dihentikan otomatis oleh Claude Code pukul 08:42 UTC karena memori laptop hampir habis. Laptop juga sempat sleep 2026-11-19 14:41–23:18 UTC dan 2026-11-20 00:40–02:16 UTC. Angka di bawah berasal dari `data/firms/profile/latency.json` (`python -I scratch/phase1/latency_report.py`). WIB = UTC+7.

**Metode:** sebuah batch muncul di antara poll sebelumnya dan poll pertama yang memuatnya. Karena itu latensi ditulis sebagai rentang `(poll sebelumnya − akuisisi, poll pertama − akuisisi]`, dan resolusinya sama dengan jarak antar-poll. Deteksi yang sudah ada di poll pertama (baseline) hanya memberi batas atas.

| Batch (UTC) | Deteksi | Akuisisi | Muncul di antara poll | Latensi akuisisi terakhir | Latensi akuisisi pertama (maks) | Presisi |
|---|---|---|---|---|---|---|
| NOAA-21 siang 19 Nov | (di baseline) | ≤ 05:50 | sebelum 09:09 | ≤ 3,3 jam | — | Batas atas |
| NOAA-20 siang 19 Nov | 240 | 03:19 … 06:46 | 11:49 … 12:26 | **5,1–5,7 jam** | ≤ 9,1 jam | 37 menit |
| NOAA-21 malam 19 Nov | 104 | 15:07 … 18:30 | 14:41 … 23:18 (laptop sleep) | ≤ 4,8 jam | ≤ 8,2 jam | Batas atas |
| NOAA-20 malam 19 Nov | 171 | 16:05 … 17:47 | 14:41 … 23:18 (laptop sleep) | ≤ 5,5 jam | ≤ 7,2 jam | Batas atas |
| NOAA-21 siang 20 Nov (lintasan 1) | 73 | 03:44 | 06:03 … 06:18 | **2,3–2,6 jam** | 2,6 jam | 15 menit |
| NOAA-20 siang 20 Nov | 220 | 04:42 … 04:46 | 07:18 … 07:33 | **2,5–2,8 jam** | 2,9 jam | 15 menit |
| NOAA-21 siang 20 Nov (lintasan 2) | 284 | 05:27 … 05:29 | 07:18 … 07:33 | **1,8–2,1 jam** | 2,1 jam | 15 menit |

Temuan (`VERIFIED` untuk periode pengamatan ini saja; sampel hanya 2 hari):

1. **Data terbit per lintasan, dan setiap lintasan terbit utuh.** Tidak ada menit akuisisi yang deteksinya tersebar di lebih dari satu batch (0 dari 58). Untuk Indonesia, setiap satelit punya ±1–2 batch siang (03–07 UTC) dan 1 batch malam (15–19 UTC) per hari.
2. **Latensi bervariasi: 1,8 sampai ±9 jam.** Klaim resmi "<3 hours (Global)" (S1) terpenuhi oleh ketiga batch siang 20 Nov (≤ 2,9 jam). NOAA-21 siang 19 Nov hanya diketahui ≤ 3,3 jam. NOAA-20 siang 19 Nov jauh melebihinya (≥ 5,1 jam, dan akuisisi pertamanya hingga ±9 jam). Dua hari belum cukup untuk menyimpulkan distribusi atau perbedaan antar satelit.
3. **Tidak ada rekaman yang berubah setelah terbit.** Dari 106 poll, `changed` = 0: nilai deteksi NRT tetap sama selama ±2 hari di jendela `DAY_RANGE`. Berarti upsert idempoten berdasarkan kunci aman untuk NRT. Perilaku setelah 2 hari tidak diamati (`UNKNOWN`).
4. Latensi lintasan malam hanya diketahui batas atasnya (≤ 4,8–8,2 jam) karena laptop sleep.

Implikasi (`RECOMMENDATION`, diputuskan di C-P2-001 / OQ-10):
- **Interval polling 30 menit** sudah cukup. Batch datang hanya ±2–3 kali sehari per satelit, dengan latensi sumber 2–9 jam, sehingga tambahan tunda polling ≤ 30 menit. Interval 15 menit tetap aman dari sisi kuota (±8 transaksi per poll).
- **"Data terlambat" ditentukan per satelit dari `acq_datetime` terbaru yang sudah dimuat**, bukan dari ada atau tidaknya deteksi baru. Di musim hujan, sebuah lintasan bisa saja punya 0 deteksi. Usulan ambang: peringatan bila akuisisi terbaru > 18 jam lalu, dan basi bila > 30 jam. Angka ini berasal dari jeda ±12 jam antar-lintasan ditambah latensi maks ±9 jam yang teramati. Sebaiknya diverifikasi lagi saat pipeline incremental berjalan (A-P5).
- Teks UI dan laporan sebaiknya menyebut **"biasanya 2–3 jam, kadang hingga ±9 jam"**, bukan "real-time".

## 4. Masukan untuk fase berikutnya

- **A-P3-001 (canonical event):** `processing_level` wajib masuk identitas. Tambahkan `source_acq_date_utc` untuk rekonsiliasi per tanggal.
- **B-P3-001 (access patterns):** operasi "hapus/ganti semua deteksi `(satellite, acq_date UTC)`" harus bisa dilayani tanpa scan. Rekonsiliasi butuh query per tanggal UTC, padahal partisi tampilan memakai tanggal lokal.
- **C-P2-001 (NFR):** ambang kesegaran per satelit dari `acq_datetime` terbaru (usulan: peringatan > 18 jam, basi > 30 jam) dan interval polling 30 menit ([§3](#3-latensi-nrt-a-p1-008)).
