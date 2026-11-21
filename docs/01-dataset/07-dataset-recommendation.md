# 07 — Rekomendasi Dataset (A-P1-010)

> Fase 1 · Draf agen 2026-11-19 · Pemilik: R1 (Lanang) · Status: `RECOMMENDATION`. Semua butir di bawah adalah **keputusan G1** yang menunggu persetujuan tim (HD-05: 3 dari 4 + pemilik area).

## Ringkasan keputusan G1

| # | Keputusan | Rekomendasi | Bukti |
|---|---|---|---|
| 1 | **Periode historis** (OQ-05, HD-09) | **2023-01-01 … sekarang**. NOAA-21 mulai 2023-03-01 (awal ketersediaannya). | §1 |
| 2 | **Produk & satelit** (konfirmasi OQ-04) | VIIRS 375 m NOAA-20 + NOAA-21; SP untuk tanggal yang sudah punya SP, NRT sesudahnya | §2, [04](04-nrt-vs-sp-and-latency.md) |
| 3 | **Aturan tumpang tindih NRT/SP** (HD-10) | Satu produk per `(satellite, acq_date UTC)`; penggantian NRT→SP per tanggal, bukan per deteksi | [04 §2](04-nrt-vs-sp-and-latency.md#2-aturan-tumpang-tindih-nrtsp-yang-diusulkan-keputusan-hd-10) |
| 4 | **Sumber batas provinsi** (OQ-07) | BIG `BATAS_KABKOTA_AR` edisi Juni 2026 (38 provinsi), snapshot tergeneralisasi 0,001° + checksum | [05](05-boundary-sources.md) |
| 5 | **Lisensi batas** (HD-08) | Konfirmasi ke BIG sebelum hosting publik. Cadangan: **B5** (repo komunitas, 38 provinsi; keputusan Lanang (R1), 2026-11-21, dievaluasi dulu sebelum dipakai) | [05 §5](05-boundary-sources.md#5-rekomendasi-recommendation-perlu-persetujuan-di-g1) |
| 6 | **Aturan kualitas data** (HD-11) | DQ-01 … DQ-15. Tipe non-vegetasi dihitung semua dengan filter opsional; tanpa snapping tepi | [06](06-data-quality-rules.md) |
| 7 | **Pembaruan register asumsi** | A-05, A-06, A-07, A-08, A-10, A-26 → VALIDATED; A-09 → sebagian; A-11 tetap OPEN | [CR-03](../change-requests/CR-03.md), [02 §5](02-data-dictionary.md#5-verifikasi-asumsi-fase-0-a-p1-005) |

## Posisi pemilik area data (R1)

**Lanang (R1), 2026-11-21** (disampaikan di sesi Claude Code): **setuju** dengan keputusan 1–4, 6, dan 7. Keputusan 5 disetujui **dengan perubahan**: cadangan bila lisensi BIG tidak memadai adalah **B5** (38 provinsi), bukan HDX (34 provinsi); lihat [05 §5](05-boundary-sources.md#5-rekomendasi-recommendation-perlu-persetujuan-di-g1). Di luar daftar G1, R1 memutuskan interval polling **15 menit** ([04 §3](04-nrt-vs-sp-and-latency.md#3-latensi-nrt-a-p1-008)). Ini suara satu anggota; G1 sah setelah 3 dari 4 anggota setuju (X-P1-902).

## 1. Periode (HD-09)

Target Fase 0: ≥ 2 tahun penuh yang mencakup setidaknya satu musim kemarau dengan aktivitas deteksi tinggi.

| Opsi | Cakupan | Baris di dalam provinsi (diukur) | Musim tinggi tercakup | Biaya unduh ulang (`ASSUMPTION`: 2 transaksi/hari/sumber) |
|---|---|---|---|---|
| **A. 2023-01-01 … sekarang** | ±3,9 tahun; NOAA-21 sejak 2023-03 | **2.233.114** | 2023 (El Niño; puncak Okt 77 ribu/bulan N20) dan 2026 (puncak Okt 223 ribu/bulan N20) | ±5.700 transaksi (2 sumber × ±1.420 hari × 2), di bawah 2 jendela kuota |
| B. 2024-01-01 … sekarang | ±2,9 tahun | 1.735.368 | Hanya 2026 | ±4.200 |
| C. 2025-01-01 … sekarang | ±1,9 tahun | 1.505.502 | Hanya 2026; tidak memenuhi target ≥ 2 tahun | ±2.800 |
| D. 2018-04-01 … sekarang (NOAA-20 saja sebelum 2023) | ±8,6 tahun | `UNKNOWN` (belum diunduh) | 2018, 2019, 2023, 2026 | +±3.500 untuk 2018–2022 |

**Rekomendasi: A.**
- Memenuhi target dua musim tinggi, dan keduanya berbeda karakter, sehingga berguna untuk perbandingan periode (*Should*).
- Kedua satelit tersedia hampir di seluruh periode, sehingga filter satelit tetap bermakna.
- Volumenya sudah terukur dan kecil untuk single-node (A-10).
- Raw zone Fase 1 sudah mencakup seluruh periode ini.

Opsi D ditolak untuk MVP: menambah volume yang belum terukur dan menghasilkan periode 2018–2022 dengan satu satelit saja, sehingga perbandingan antar tahun rawan salah tafsir.

## 2. Produk

- **NOAA-20 SP:** 2023-01-01 … 2026-07-31. **NOAA-21 SP:** 2023-03-01 … 2026-07-31. Setelah itu NRT kedua satelit.
- Akhir ketersediaan SP bergerak maju sekitar sebulan sekali (jeda ±5 bulan), sehingga tanggal batas dibaca dari `data_availability` saat run, bukan di-hardcode.
- Data per satelit **tidak dijumlahkan sebagai "kebakaran"**. Total gabungan N20 + N21 adalah jumlah deteksi dari dua sensor (charter §3). UI wajib menjelaskan bahwa jumlah gabungan bergantung pada jumlah lintasan.

## 3. Hal yang belum selesai di Fase 1

| Item | Status | Dampak ke G1 |
|---|---|---|
| Latensi NRT (A-P1-008) | **Selesai** 2026-11-20: 1,8 sampai ±9 jam, per lintasan ([04 §3](04-nrt-vs-sp-and-latency.md#3-latensi-nrt-a-p1-008)) | Tidak memblokir keputusan di atas; angka dipakai untuk NFR (C-P2-001) |
| Lisensi BIG (HD-08) | Menunggu jawaban BIG | Tidak memblokir pengembangan lokal; memblokir hosting publik dengan BIG |
| Review manusia atas draf A-P1-001 … A-P1-010 | **Selesai:** disetujui Lanang (R1), 2026-11-21, dengan dua perubahan di atas | Prasyarat G1 terpenuhi untuk area data |
