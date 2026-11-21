# Fase 1 — Dataset Feasibility: Laporan (A-P1-010)

> Draf agen 2026-11-19 (D1) · Pemilik: R1 (Lanang) · Gerbang: **G1** (target D3, 2026-11-21) · Label: [legenda](../00-discovery/README.md#label-status-informasi)

| # | Dokumen | Tugas | Status |
|---|---|---|---|
| 01 | [Source inventory](01-source-inventory.md) | A-P1-001 | Draf, menunggu review R1 |
| 02 | [Data dictionary + verifikasi asumsi](02-data-dictionary.md) | A-P1-003, A-P1-005 | Draf |
| 03 | [Laporan profiling](03-profiling-report.md) | A-P1-004 | Draf |
| 04 | [NRT vs SP & latensi](04-nrt-vs-sp-and-latency.md) | A-P1-007, A-P1-008 | Draf (latensi final 2026-11-20) |
| 05 | [Sumber batas provinsi](05-boundary-sources.md) | A-P1-006 | Draf, menunggu review R1 |
| 06 | [Aturan kualitas data](06-data-quality-rules.md) | A-P1-009 | Draf |
| 07 | [Rekomendasi dataset](07-dataset-recommendation.md) | A-P1-010 | Draf |
| — | [Estimasi volume](../03-specs/database/00-volume-estimates.md) | B-P1-001 | Draf (R2) |
| — | [Draf user stories](../02-requirements/00-draft-user-stories.md) | D-P1-001 | Draf (R4) |

## 1. Tujuan fase

Memastikan, dengan data nyata, bahwa sumber yang dipilih di Fase 0 (NASA FIRMS VIIRS NOAA-20/21) dan batas wilayah 38 provinsi dapat mendukung MVP. Fase ini juga menetapkan periode, aturan NRT/SP, dan aturan kualitas data sebelum requirements dan model data disusun.

## 2. Konteks saat ini

- G0 dan GATE-EP disetujui 2026-11-19. Rencana eksekusi ada di PR #1.
- Raw zone lokal: 629 file FIRMS (2.705.905 baris, 222 MB), semuanya cocok dengan checksum manifest. Ditambah snapshot batas BIG (22 bagian GeoJSON, ±10 MB). Semuanya di `data/`, tidak di-commit.
- Skrip sekali pakai ada di `scratch/phase1/`. Semua angka di folder ini dapat dihasilkan ulang tanpa memanggil API, kecuali poller latensi.
- Poller latensi NRT selesai: 2026-11-19 09:09 … 2026-11-20 08:42 UTC, 106 request HTTP 200 (HD-22). Proses dihentikan otomatis karena memori laptop hampir habis, sebelum batas perpanjangan 14:30 UTC.

## 3. Tugas yang memerlukan keputusan manusia (G1)

Ketujuh keputusan ada di [07 — ringkasan](07-dataset-recommendation.md#ringkasan-keputusan-g1):
1. Periode (HD-09)
2. Produk
3. Aturan NRT/SP (HD-10)
4. Sumber batas (OQ-07)
5. Lisensi BIG (HD-08)
6. Aturan DQ (HD-11), termasuk dua sub-keputusan di [06](06-data-quality-rules.md#keputusan-yang-dibutuhkan-di-g1)
7. Pembaruan register asumsi ([CR-03](../change-requests/CR-03.md))

## 4. Tugas yang cocok diotomasi

- Profiling dan pemeriksaan checksum dijalankan ulang otomatis setiap raw zone berubah (sudah berupa skrip).
- Aturan DQ-01 … DQ-15 menjadi validator di pipeline (A-P5-002), dengan test positif/negatif per aturan.
- Rekap hari tidak lengkap dari `missing_data` (DQ-12) diambil otomatis per run.
- Yang **tidak** diotomasi: pilihan periode, kebijakan tipe non-vegetasi, lisensi, dan penghapusan NRT saat rekonsiliasi.

## 5. Rencana eksekusi terperinci

Sesuai [rencana eksekusi](../10-execution-plan/05-project-schedule.md): G1 pada D3 → A-P2-001 (semantik data) → A-P3-001 (canonical event) dan B-P3-001/002 (access patterns, model). Masukan langsung dari Fase 1 untuk fase berikutnya ada di [04 §4](04-nrt-vs-sp-and-latency.md#4-masukan-untuk-fase-berikutnya) dan [00-volume-estimates §4](../03-specs/database/00-volume-estimates.md#4-implikasi-untuk-desain-masukan-b-p3-001-recommendation).

## 6. Rekomendasi teknis

1. **Periode:** 2023-01-01 … sekarang, NOAA-20 + NOAA-21 (±2,23 juta deteksi di dalam provinsi).
2. **Satu produk per (satelit, tanggal UTC).** SP bila tersedia, NRT sesudahnya. Penggantian NRT→SP per tanggal karena `acq_time` bergeser ±2 menit, sehingga identitas tidak bisa dicocokkan.
3. **`detection_id` mencakup `processing_level`**; natural key `(lat, lon, acq_date, acq_time, satellite)` praktis unik di dalam satu produk.
4. **Agregasi per tanggal lokal wajib.** ±26% deteksi SP dan ±45% deteksi NRT 2026 berpindah tanggal saat dikonversi dari UTC ke waktu lokal.
5. **BIG edisi Juni 2026** sebagai satu-satunya batas, disimpan sebagai snapshot dengan checksum. Lisensi dikonfirmasi sebelum hosting publik.
6. **Simpan semua, tandai kualitas.** Tidak ada baris yang perlu ditolak di data Fase 1; yang ada hanya flag (saturasi, FRP 0, tipe non-vegetasi, titik di luar provinsi).
7. **Desain partisi memakai data musim 2026.** Partisi provinsi-hari maksimum ±13 ribu baris; provinsi-bulan maksimum ±142 ribu baris, sehingga menjadi kandidat bucketing.

## 7. Artefak yang dihasilkan

- **Dokumen:** 7 dokumen di folder ini, ditambah estimasi volume (R2), draf user stories (R4), dan [CR-03](../change-requests/CR-03.md).
- **Skrip** (`scratch/phase1/`): `download.py`, `download_big.py`, `pip_assign.py`, `profile_firms.py`, `extra_checks.py`, `compare_nrt_sp.py`, `latency_poller.py`, `latency_report.py`, `probe.py`, `mapkey_status.py`, `firms_common.py`.
- **Data lokal:** `data/firms/{raw,profile,latency}/`, `data/boundaries/`.
- Tidak ada kode aplikasi, skema, atau dependensi baru.

## 8. Checklist validasi (untuk reviewer)

- [ ] Jalankan ulang `pip_assign.py` → `profile_firms.py` → `extra_checks.py` → `compare_nrt_sp.py`; angka sama dengan dokumen.
- [ ] Cocokkan 3 baris acak dari raw zone dengan data dictionary (header, format `acq_time`, `version`).
- [ ] Periksa penetapan provinsi untuk 5 titik acak di peta.
- [ ] Pastikan tidak ada MAP_KEY di dokumen, skrip, dan log (`grep`).
- [ ] Setujui atau tolak masing-masing dari 7 keputusan G1.

## 9. Kriteria penerimaan Fase 1

| Kriteria (10-phase-gates G1) | Status |
|---|---|
| Unduhan terverifikasi checksum | Terpenuhi (629/629) |
| Setiap angka dapat ditelusuri ke file profil | Terpenuhi: setiap dokumen menyebut file sumber angkanya |
| Tidak ada klaim `AI-PRIOR` tanpa label | Terpenuhi: batas ukuran partisi dan byte per baris diberi label |
| Keputusan G1 punya opsi + rekomendasi + bukti | Terpenuhi ([07](07-dataset-recommendation.md)) |
| Latensi NRT dilaporkan | Terpenuhi ([04 §3](04-nrt-vs-sp-and-latency.md#3-latensi-nrt-a-p1-008)); malam hanya batas atas |
| Review R1 atas A-P1-001 … A-P1-010 | Terpenuhi: Lanang, 2026-11-21 (cadangan batas → B5; polling 15 menit) |

## 10. Risiko tersisa

| Risiko | Mitigasi |
|---|---|
| Lisensi BIG tidak memperbolehkan hosting publik (RC-06) | Snapshot lokal + cadangan B5 (38 provinsi, keputusan R1). Asal-usul dan lisensi B5 harus dievaluasi dulu |
| Lonjakan volume 2026 adalah artefak sumber, bukan kejadian nyata | Cek ulang saat SP untuk 2026-08 terbit (±5 bulan). Untuk desain, volume 2026 tetap dipakai sebagai kasus terburuk |
| Latensi NRT kadang ±9 jam (NOAA-20, 19 Nov); sampel hanya 2 hari | Indikator kesegaran per satelit dari akuisisi terbaru; ambang diverifikasi ulang saat pipeline incremental berjalan (A-P5) |
| Endpoint `missing_data` tidak terdokumentasi dan bisa berubah | DQ-12 juga mendeteksi hari 0 baris tanpa bergantung pada endpoint itu |

## 11. Gerbang persetujuan G1

Disetujui bila mayoritas 3 dari 4 setuju, dan pemilik area data (R1, Lanang) termasuk yang setuju. Hasilnya dicatat oleh koordinator (Abi Funn, X-P1-902) di STATUS.md dan register keputusan.

## 12. Tindakan berikutnya

1. **Lanang:** selesai 2026-11-21 (A-P1-001 … A-P1-010 disetujui; posisi R1 di [07](07-dataset-recommendation.md#posisi-pemilik-area-data-r1)).
2. **Abi Funn:** review [00-volume-estimates](../03-specs/database/00-volume-estimates.md), lalu siapkan paket G1.
3. **Abigail:** review draf user stories (masukan D-P2-001).
4. **Zita:** C-P1-001 (inventaris toolchain & opsi cloud) belum dikerjakan.
5. Latensi sudah final ([04 §3](04-nrt-vs-sp-and-latency.md#3-latensi-nrt-a-p1-008)); tidak ada pekerjaan agen yang tersisa untuk G1.
