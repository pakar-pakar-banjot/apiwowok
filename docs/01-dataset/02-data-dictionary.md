# 02 — Data Dictionary (A-P1-003, A-P1-005)

> Fase 1 · Draf agen 2026-11-19 · Pemilik: R1 (Lanang) · Reviewer: R2 (Abi Funn) · Label: [legenda](../00-discovery/README.md#label-status-informasi)
> Data: 629 respons Area API (bbox `94,-11.5,141.5,6.5`) yang diunduh 2026-11-19, berisi **2.705.905 baris**. Checksum SHA-256 semua file cocok dengan `data/firms/manifest.csv`. Angka di dokumen ini berasal dari `data/firms/profile/profile.json` dan `extra_checks.json` (skrip `scratch/phase1/profile_firms.py`, `extra_checks.py`).

## 1. Sumber resmi yang dibaca (2026-11-19)

| Kode | Dokumen | URL |
|---|---|---|
| **S1** | NASA Earthdata — VIIRS I-Band 375 m Active Fire Data (tabel atribut NRT) | https://www.earthdata.nasa.gov/data/instruments/viirs/viirs-i-band-375-m-active-fire-data |
| **S2** | NASA Earthdata — FIRMS FAQ | https://www.earthdata.nasa.gov/data/tools/firms/faq |
| **S3** | Giglio, Hall, Schroeder — *VIIRS Collection 2 375 m Active Fire Product User's Guide* v1.2 (6/2025) | https://www.earthdata.nasa.gov/s3fs-public/2025-06/VIIRS_C2_AF-375m_User_Guide_1.2.pdf |
| **S4** | FIRMS Archive Download | https://firms.modaps.eosdis.nasa.gov/download/ |

## 2. Header per sumber (`VERIFIED`, dari data)

| Source ID | Jumlah file | Header (urutan persis) |
|---|---|---|
| `VIIRS_NOAA20_SP`, `VIIRS_NOAA21_SP` | 262, 250 | `latitude,longitude,bright_ti4,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_ti5,frp,daynight,type` (15 kolom) |
| `VIIRS_NOAA20_NRT`, `VIIRS_NOAA21_NRT` | 22, 95 | Sama, **tanpa `type`** (14 kolom) |

Setiap sumber hanya memakai satu header di semua filenya. Tidak ada nilai kosong dan tidak ada nilai non-numerik di kolom numerik, di keempat sumber (`empty_values = {}`, `non_numeric = {}`).

## 3. Kolom

Rentang di bawah adalah min–maks dari seluruh baris bbox. p1/p50/p99 ada di [03-profiling-report](03-profiling-report.md).

| Kolom | Tipe (usulan) | Definisi resmi | Nilai teramati | Catatan normalisasi |
|---|---|---|---|---|
| `latitude` | double | "Center of nominal 375 m fire pixel" (S1). Lokasi adalah titik tengah piksel, "not necessarily the coordinates of the actual fire" (S2). | −11,5 … 6,49985; umumnya 5 desimal, sebagian 1–4 desimal (nol di belakang dibuang) | Simpan presisi sumber; **jangan** dibulatkan sebelum membuat identitas |
| `longitude` | double | Sama (S1) | 94,27016 … 141,5 | Sama |
| `bright_ti4` | double (K) | "VIIRS I-4 channel brightness temperature of the fire pixel measured in Kelvin" (S1). 367 K = "nominal saturation temperature" (S3 §7). | 207,38 … **367,0** | 367,0 = piksel jenuh → tandai `ti4_saturated` (DQ-09) |
| `bright_ti5` | double (K) | "I-5 Channel brightness temperature … in Kelvin" (S1) | 228,31 … 376,43 | — |
| `scan` | double | "Along Scan pixel size"; ±375 m di nadir (S1) | 0,32 … 0,80 | Satuan tidak disebut S1. Nilainya konsisten dengan **km** (0,375 km di nadir): `ASSUMPTION` |
| `track` | double | "Along Track pixel size" (S1) | 0,36 … 0,78 | Sama |
| `acq_date` | date | "Date of VIIRS acquisition" (S1). Produk ML: tanggal UTC (S3 §3.2.2). | `YYYY-MM-DD`, selalu di dalam jendela request (0 baris di luar) | Tanggal **UTC** |
| `acq_time` | int (HHMM) | "Time of acquisition/overpass of the satellite (in UTC)" (S1) | 3 digit untuk semua deteksi siang (mis. `538` = 05:38), 4 digit untuk semua deteksi malam; 0 nilai HHMM invalid | Pad ke 4 digit lalu gabung dengan `acq_date` → `acq_datetime_utc` |
| `satellite` | text | `N20` = NOAA-20, `N21` = NOAA-21 (S1) | `N20` hanya di sumber NOAA20, `N21` hanya di NOAA21 | Konsisten dengan source ID (DQ-15) |
| `instrument` | text | Tidak ada di tabel S1 | Selalu `VIIRS` | — |
| `confidence` | text | Kelas low/nominal/high (S1); kode "L/N/H" (S3) | `l`, `n`, `h` (huruf kecil); di dalam Indonesia **tidak ada `l` pada malam hari** di keempat sumber | Simpan mentah + `confidence_class` (`low`/`nominal`/`high`). Hampir semua `h` = piksel jenuh (lihat §4) |
| `version` | text | "Version (Collection and source)": NRT diberi akhiran `NRT`, standard = koleksi saja (S1, dengan contoh C1 `1.0NRT` / `1.0`) | SP = `2`, NRT = `2.0NRT` | Turunkan `processing_level` (`SP`/`NRT`); simpan `version_raw` |
| `frp` | double (MW) | "pixel-integrated fire radiative power in MW" (S1) | 0,0 … 1.081,07; nilai 0: 0–17 baris per sumber | Simpan; tandai `frp_zero` (DQ-10) |
| `daynight` | text | `D` = daytime, `N` = nighttime (S1). SP: berdasarkan sudut zenit matahari (85°); NRT: berdasarkan orbit naik/turun (S2) | `D`/`N`; 100% konsisten dengan jam matahari lokal (siang 06–18) di semua sumber | Aturannya berbeda antara NRT dan SP, tetapi tidak ada pasangan NRT–SP yang berbeda label (lihat [04](04-nrt-vs-sp-and-latency.md)) |
| `type` | int, **nullable** | 0 = presumed vegetation fire, 1 = active volcano, 2 = other static land source, 3 = offshore detection (S3 §3.2.2). NRT tidak membawa atribusi ini (S2). | SP: 0, 1, 2, 3. NRT: kolom tidak ada. | `null` untuk NRT (OQ-12 = keterbatasan) |

Kolom yang **tidak** ada: ID unik per deteksi (A-08), zona waktu lokal, kode wilayah, dan nama file sumber.

## 4. Perbedaan antar produk (`VERIFIED`, angka dari data)

| Aspek | SP (`2`) | NRT (`2.0NRT`) |
|---|---|---|
| Kolom `type` | Ada. Di dalam Indonesia: NOAA-20 tipe 0 = 468.114 (89,6%), 1 = 11.188, 2 = 41.427, 3 = 1.452; NOAA-21 tipe 0 = 458.720 (89,0%), 1 = 10.787, 2 = 44.565, 3 = 1.436 | Tidak ada (0 dari 1.461.362 baris) |
| `version` | `2` (100%) | `2.0NRT` (100%) |
| Penentuan day/night | Sudut zenit matahari | Orbit |
| Nilai `bright_ti4` = 367,0 | N20 16.647 (2,7%), N21 19.762 (3,2%) | N20 36.359 (5,5%), N21 34.042 (4,3%) |
| Confidence `h` = `ti4` 367,0 | 100% baris `h` punya `ti4` = 367,0 (N20 16.435 dari 16.435) | 100% (N20 35.903 dari 35.903) |

NOAA-20 vs NOAA-21: header, tipe, dan domain nilainya identik. Yang berbeda hanya kode `satellite` dan cakupan waktunya (NOAA-21 SP mulai 2023-03-01).

## 5. Verifikasi asumsi Fase 0 (A-P1-005)

Usulan pembaruan register diajukan sebagai [CR-03](../change-requests/CR-03.md), untuk disetujui di G1.

| ID | Asumsi (ringkas) | Hasil | Bukti |
|---|---|---|---|
| A-05 | FIRMS gratis, API dengan MAP_KEY, kuota 5000/10 menit | **VALIDATED** | 629 request, semua HTTP 200; biaya terukur 2 transaksi/hari data ([01](01-source-inventory.md)) |
| A-06 | Field inti ada, tetapi nama/format berbeda antar produk | **VALIDATED (dengan koreksi)** | Nama kolom **sama** di semua produk. Satu-satunya perbedaan: `type` tidak ada di NRT, dan nilai `version` berbeda (§2, §4) |
| A-07 | `acq_date`/`acq_time` UTC; `acq_time` HHMM, mungkin tanpa nol di depan | **VALIDATED** | S1 ("in UTC"); deteksi siang selalu 3 digit, malam 4 digit; 0 nilai invalid |
| A-08 | Tidak ada ID unik; dedup butuh natural key komposit | **VALIDATED** | Tidak ada kolom ID. Kunci `(lat, lon, acq_date, acq_time, satellite)` unik per sumber kecuali 0–1 baris (§ dedup di [03](03-profiling-report.md)) |
| A-09 | NRT kemudian diganti versi standar; keduanya dibedakan lewat `version` | **SEBAGIAN VALID** | `version` membedakan produk (VALID). Tetapi: (a) API **tetap menyajikan NRT** untuk tanggal yang sudah punya SP (NOAA-21, 2025-08 … 2026-07); (b) deteksi yang sama punya `acq_time` berbeda ±1–2 menit di NRT dan SP, dan hanya 39% yang kuncinya cocok persis. Akibatnya, penggantian **tidak bisa** berdasarkan identitas, melainkan harus per `(satellite, tanggal)` ([04](04-nrt-vs-sp-and-latency.md)) |
| A-10 | Volume beberapa tahun muat diproses di memori satu mesin & Cassandra single-node | **VALIDATED** | 2,7 juta baris / 222 MB CSV (2023-01 … 2026-11). Profiling penuh di satu laptop: point-in-polygon 48 detik untuk 2,56 juta koordinat unik. 2.233.114 baris di dalam Indonesia untuk periode rekomendasi ([00-volume-estimates](../03-specs/database/00-volume-estimates.md)) |
| A-11 | Ada sumber batas 38 provinsi berlisensi jelas untuk hosting publik | **OPEN** | BIG memuat 38 provinsi, tetapi lisensinya `UNKNOWN` (HD-08, [05](05-boundary-sources.md)) |
| A-26 | NRT muncul beberapa kali sehari dengan latensi beberapa jam | **VALIDATED** | Poller 2026-11-19/20, 106 request: data terbit per lintasan (±2–3 batch per hari per satelit), latensi 1,8 sampai ±9 jam, tidak ada rekaman yang berubah setelah terbit. Lihat [04 §3](04-nrt-vs-sp-and-latency.md#3-latensi-nrt-a-p1-008) |
