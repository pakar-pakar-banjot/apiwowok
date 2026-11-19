# 06 — Aturan Kualitas Data Awal (A-P1-009)

> Fase 1 · Draf agen 2026-11-19 · Pemilik: R1 (Lanang) · Reviewer: R2 (Abi Funn) · Status: `RECOMMENDATION`. Kebijakan DQ butuh persetujuan di **G1** (HD-11).
> Dampak = jumlah baris di raw zone Fase 1 ([03](03-profiling-report.md)). Urutan sumber di kolom dampak: N20 SP · N21 SP · N20 NRT · N21 NRT.

## Prinsip

1. **Simpan semua yang valid secara struktural** (OQ-09). Kualitas ditandai dengan *flag*, tidak dibuang.
2. **Tolak hanya yang tidak bisa diproses** (struktur rusak, nilai tidak terbaca). Setiap penolakan punya *reason code* dan tercatat di run log/rejected store, sehingga tidak ada baris yang hilang diam-diam.
3. Aturan dijalankan identik di mode backfill dan incremental.

## Aturan

| ID | Kondisi | Aksi | Reason code / flag | Dampak terukur |
|---|---|---|---|---|
| DQ-01 | Header file ≠ header SP (15 kolom) atau NRT (14 kolom) yang terdaftar | **Tolak file**, run gagal untuk file itu | `SCHEMA_MISMATCH` | 0 dari 629 file |
| DQ-02 | Nilai wajib kosong (semua kolom kecuali `type`) | Tolak baris | `MISSING_FIELD` | 0 · 0 · 0 · 0 |
| DQ-03 | Kolom numerik tidak bisa di-parse | Tolak baris | `NON_NUMERIC` | 0 · 0 · 0 · 0 |
| DQ-04 | Lat/lon di luar bbox ekstraksi atau di luar ±90/±180 | Tolak baris | `COORD_OUT_OF_RANGE` | 0 · 0 · 0 · 0 |
| DQ-05 | `acq_time` bukan HHMM valid setelah di-pad 4 digit | Tolak baris | `INVALID_TIME` | 0 · 0 · 0 · 0 |
| DQ-06 | `acq_date` di luar jendela request | Tolak baris | `OUT_OF_WINDOW` | 0 · 0 · 0 · 0 |
| DQ-07 | Titik tidak masuk poligon provinsi mana pun | **Simpan**, `region_status = OUTSIDE`, keluarkan dari ranking & agregat provinsi (OQ-11). Jumlahnya dilaporkan per run. | flag `OUTSIDE` | 104.763 · 102.091 · 62.560 · 81.751 (di antaranya ≤ 2 km dari tepi: 2.892 · 2.671 · 2.992 · 3.127) |
| DQ-07b | Titik masuk >1 poligon (efek generalisasi tepi) | Simpan; ambil poligon pertama secara deterministik (urutan fitur BIG) | flag `MULTI_POLYGON` | 30 · 16 · 34 · 26 |
| DQ-08 | Dua baris dengan kunci identitas sama dalam satu produk | Simpan satu (upsert). Bila nilainya berbeda, pilih deterministik: FRP tertinggi, lalu `bright_ti4` tertinggi; catat. | `DUPLICATE` / `DUPLICATE_CONFLICT` | 0 · 1 · 1 · 0 (semuanya konflik nilai) |
| DQ-09 | `bright_ti4` = 367,0 K (saturasi nominal I4, S3) | Simpan | flag `TI4_SATURATED` | 16.647 · 19.762 · 36.359 · 34.042 |
| DQ-10 | `frp` = 0 | Simpan | flag `FRP_ZERO` | 0 · 9 · 3 · 17 |
| DQ-11 | `type` ∈ {1, 2, 3} (gunung api, sumber statis darat, offshore) | Simpan dengan `type` asli. Apakah dihitung di agregat/tampilan **diputuskan tim** (opsi di bawah). | flag `NON_VEGETATION_TYPE` | Di dalam Indonesia: 54.067 (N20 SP, 10,4%) · 56.788 (N21 SP, 11,0%) · NRT: tidak diketahui (kolom tidak ada) |
| DQ-12 | Tanggal tercantum di tabel `missing_data` FIRMS, atau 0 baris untuk satu `(satelit, tanggal)` | Tandai tanggal itu sebagai **data tidak lengkap** di tabel cakupan. Jangan ditampilkan sebagai "0 deteksi". | flag tanggal `INCOMPLETE_DAY` | N20 SP: 6 hari kosong; N21 SP: 2 kosong + 7 parsial |
| DQ-13 | `confidence` ∉ {`l`,`n`,`h`} | Tolak baris | `INVALID_CONFIDENCE` | 0 · 0 · 0 · 0 |
| DQ-14 | `version` tidak sesuai source ID (SP → `2`, NRT → `2.0NRT`) | Tolak file | `VERSION_MISMATCH` | 0 |
| DQ-15 | `satellite` tidak sesuai source ID | Tolak file | `SATELLITE_MISMATCH` | 0 |

Diamati tetapi **bukan** aturan, karena sumber resmi tidak menyebutnya sebagai error: `bright_ti4` < 280 K (185–296 baris per sumber) dan `bright_ti4` < `bright_ti5` (726–1.146 baris per sumber).

## Keputusan yang dibutuhkan di G1

### A. Perlakuan tipe non-vegetasi (DQ-11)

| Opsi | Akibat |
|---|---|
| **(a) Hitung semua deteksi; sediakan filter "hanya dugaan vegetasi" (tipe 0) untuk periode SP** | Konsisten dengan OQ-09. Perlu catatan di UI bahwa filter ini tidak tersedia untuk periode NRT. |
| (b) Keluarkan tipe 1–3 dari semua agregat | Periode SP dan NRT jadi tidak sebanding: ±10% deteksi statis hanya bisa dibuang di SP. |
| (c) Bangun "masker sumber statis" dari lokasi tipe 2 di SP, lalu terapkan ke NRT | Paling konsisten, tetapi menambah logika dan asumsi (`ASSUMPTION`: lokasi statis tetap dari tahun ke tahun). Cocok sebagai *Could*. |

**Rekomendasi: (a).** Default tampilan diputuskan di Fase 2 bersama confidence (HD-12).

### B. Titik di luar poligon dekat tepi (DQ-07)

| Opsi | Akibat |
|---|---|
| **(a) Tidak ada snapping: titik di luar poligon = `OUTSIDE`** | Sederhana dan deterministik. Kehilangan ≤ 0,6% deteksi dari ranking. |
| (b) Snap ke provinsi terdekat bila ≤ X km | Berisiko salah menetapkan titik di wilayah negara tetangga dekat perbatasan darat (Malaysia, Timor-Leste, PNG), karena batas negara lain tidak dimuat. Selain itu, sebagian besar titik ≤ 0,5 km adalah offshore (tipe 3). |

**Rekomendasi: (a).** Ini sesuai OQ-11, yang sudah diputuskan di Fase 0.
