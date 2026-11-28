# 01 — Kebutuhan Query Aplikasi (`Q-xx`) — `B-P2-001`

> Fase 2 · Draf agen 2026-11-28 · Pemilik: R2 (Abi Funn) · Status: `RECOMMENDATION`, menunggu persetujuan G2
> Input: [01-functional-requirements.md](../../02-requirements/01-functional-requirements.md) (D-P2-001), [02-non-functional-requirements.md](../../02-requirements/02-non-functional-requirements.md) (C-P2-001), [01-data-semantics.md](../data/01-data-semantics.md) (A-P2-001), [00-volume-estimates.md](00-volume-estimates.md) (B-P1-001), [06-interface-contracts.md](../../10-execution-plan/06-interface-contracts.md) §C.
> Serah-terima: R4 (Abigail) untuk D-P2-003; R2 (Abi Funn) untuk B-P3-001 (desain access patterns & tabel CQL); X-P2-901 (Gerbang G2).

## 1. Konvensi & Batasan Desain

- **Query-driven modeling (STATUS §2 butir 5):** Setiap `Q-xx` di bawah melayani minimal satu FR yang membaca data. Tidak ada `ALLOW FILTERING` dan tidak ada full scan pada jalur aplikasi.
- **Definisi hitungan (`SEM-00`, `SEM-02`):** Semua angka dashboard hanya menghitung deteksi berstatus `INSIDE` (38 provinsi BIG) berdasarkan `local_date` provinsi (WIB/WITA/WIT). Deteksi `OUTSIDE` tidak masuk tabel layanan dashboard (`SEM-02`, putusan Lanang 2026-11-23), tetapi jumlahnya dilaporkan terpisah dari catatan ingest/raw zone (`FR-02`).
- **Filter global (`FR-G6`, `FR-08`, `FR-09`, `FR-10`):**
  - `satellite` ∈ `{N20, N21}` (default: keduanya).
  - `confidence` ∈ `{l, n, h}` (default rekomendasi: semua, `KEP-01`).
  - `exclude_non_veg` (opsional, `type = 0` saja): hanya aktif bila seluruh rentang tanggal terpilih berasal dari produk SP (`SEM-05`, `FR-10`).
- **Bounded result (`NFR-06`, `NFR-08`, `NFR-09`):** Semua kueri list memiliki batas eksplisit (`limit` + `truncated`).
- **Label status informasi:** Angka terukur dari `00-volume-estimates.md` berlabel `VERIFIED`; estimasi ukuran baris/byte dan batas yang belum diuji berlabel `ASSUMPTION` atau `RECOMMENDATION`.

---

## 2. Katalog Kebutuhan Query (`Q-01` … `Q-08`)

### Ringkasan Katalog

| ID | Nama Query | FR Terkait | Endpoint Kontrak D | Kardinalitas / Ukuran Hasil | Pra-agregasi? |
|---|---|---|---|---|---|
| `Q-01` | Metadata sistem, provinsi & rentang tersedia | `FR-G2`, `FR-G5`, `FR-09`, `FR-12`, `FR-20`, `FR-24` | `/api/v1/meta`, `/ready` | 38 provinsi + 1 metadata (`< 50` baris) | Tidak |
| `Q-02` | Ringkasan KPI periode & provinsi aktif | `FR-01`, `FR-02`, `FR-08`–`FR-10`, `FR-12`, `FR-20`, `FR-G2`, `FR-G4`, `FR-G6` | `/api/v1/summary`, `/api/v1/provinces/{code}` | 1 ringkasan (baca ≤ `38 × N_hari` baris agregat) | **Ya (Wajib)** |
| `Q-03` | Timeline deteksi harian / bulanan | `FR-01`, `FR-05`, `FR-07`, `FR-08`–`FR-10`, `FR-12`, `FR-G4`, `FR-G6`, `FR-G7` | `/api/v1/timeline` | ≤ 1.419 baris (harian) / ≤ 47 baris (bulanan) | **Ya (Wajib)** |
| `Q-04` | Ranking Top-N provinsi | `FR-06`, `FR-08`–`FR-10`, `FR-12`, `FR-G4`, `FR-G6` | `/api/v1/provinces/ranking` | ≤ 38 baris | **Ya (Wajib)** |
| `Q-05` | Titik deteksi peta (bounded per provinsi) | `FR-03`, `FR-04`, `FR-08`–`FR-10`, `FR-12`, `FR-24`, `FR-G6` | `/api/v1/detections` | Default ≤ 2.000, maks 5.000 titik (`NFR-06`) | Tidak |
| `Q-06` | Distribusi / histogram FRP | `FR-11` (`Should`), `FR-08`–`FR-10`, `FR-12`, `FR-G6` | `/api/v1/summary` / `/api/v1/frp/distribution` | ±5–10 bin (`< 20` baris) | **Ya (Disarankan)** |
| `Q-07` | Daftar hari tidak lengkap (`INCOMPLETE_DAY`) | `FR-G7`, `FR-01`, `FR-05`, `FR-07` | `/api/v1/timeline`, `/api/v1/summary`, `/api/v1/meta` | `< 50` baris (`missing_data`) | Tidak |
| `Q-08` | Status pipeline & daftar run ingest | `FR-13`, `FR-14`, `FR-19`–`FR-24` | `/api/v1/pipeline/status`, `/ready` | ≤ 100 baris run terbaru | Tidak |

---

### `Q-01` — Metadata sistem, daftar provinsi, dan rentang data tersedia
- **FR:** `FR-G2`, `FR-G5`, `FR-09`, `FR-12`, `FR-20`, `FR-24`
- **Parameter:** opsional `boundary_version`
- **Filter:** —
- **Urutan:** `province_code` naik (`ASC`)
- **Kardinalitas & ukuran hasil:** 38 baris provinsi (`VERIFIED`, BIG Juni 2026) + 1 baris metadata (`min_date`, `max_date`, `data_updated_at`, `boundary_version`, status ketersediaan satelit). Total `< 50` baris (`< 10 KB`, `ASSUMPTION`).
- **Pra-agregasi:** Tidak perlu (data referensi statis + 1 partisi metadata).

### `Q-02` — Ringkasan KPI periode (nasional atau satu provinsi)
- **FR:** `FR-01`, `FR-02`, `FR-08`, `FR-09`, `FR-10`, `FR-12`, `FR-20`, `FR-G2`, `FR-G4`, `FR-G6`
- **Parameter:** `date_from`, `date_to` (`local_date`), opsional `province_code`
- **Filter:** `satellite` ∈ `{N20, N21}`, `confidence` ∈ `{l, n, h}`, opsional `exclude_non_veg` (khusus rentang 100% SP, `SEM-05`)
- **Urutan:** — (mengembalikan total deteksi `INSIDE`, jumlah provinsi aktif dengan `≥ 1` deteksi, rincian per `confidence`, jumlah `OUTSIDE` terpisah untuk periode terkait, dan `data_updated_at`)
- **Kardinalitas & ukuran hasil:** Output ke API = 1 objek ringkasan (`< 5 KB`, `ASSUMPTION`). Baris yang dibaca dari tabel agregat harian untuk 1 tahun penuh lintas 38 provinsi: maks `38 × 366 = 13.908` baris (atau `× 6` bila dimensi `satellite × confidence` ada di kunci ≈ `83.448` baris; untuk rentang bulanan maks `38 × 12 = 456` baris dasar).
- **Pra-agregasi:** **Ya (WAJIB).** Memindai tabel detail hingga 2.233.114 baris (`VERIFIED`) untuk menghitung KPI tidak memenuhi `NFR-03` (p95 ≤ 500 ms).
- **Implikasi `B-P3-001` (`RC-03`):**
  1. `satellite` dan `confidence` **harus** masuk kunci tabel agregat agar filter global (`FR-08`, `FR-09`) dilayani tanpa scan detail.
  2. Untuk `FR-02` (`OUTSIDE`), karena baris `OUTSIDE` tidak disimpan di tabel layanan detail (`SEM-02`), jumlah `OUTSIDE` per tanggal/run disimpan sebagai agregat ringan tersendiri oleh ETL (`FR-13`).
  3. Untuk `FR-10` (`exclude_non_veg`), `B-P3-001` harus menentukan apakah flag `is_vegetation` masuk kunci agregat SP atau dihitung dari agregat terpisah khusus SP.

### `Q-03` — Timeline jumlah deteksi harian / bulanan
- **FR:** `FR-01`, `FR-05`, `FR-07` (perbandingan 2 periode memanggil `Q-03` untuk masing-masing periode), `FR-08`, `FR-09`, `FR-10`, `FR-12`, `FR-G4`, `FR-G6`, `FR-G7`
- **Parameter:** `granularity` ∈ `{daily, monthly}`, `date_from`, `date_to` (`local_date`), opsional `province_code`
- **Filter:** `satellite`, `confidence`, opsional `exclude_non_veg` (SP-only)
- **Urutan:** `local_date` (atau `local_month`) naik (`ASC`)
- **Kardinalitas & ukuran hasil:**
  - Terukur (`00-volume-estimates.md`, `VERIFIED`): dataset mencakup `1.419` tanggal lokal (`47` bulan) dan `38` provinsi.
  - Output API: ≤ `1.419` titik (harian) atau ≤ `47` titik (bulanan); tipikal 30–90 titik (`< 50 KB`, `ASSUMPTION`).
  - Pembacaan DB (bila nasional diagregasi dari tabel provinsi): maks `38 × 1.419 ≈ 53.922` baris agregat harian dasar (`±324 ribu` baris bila `satellite × confidence` masuk kunci), atau jauh lebih kecil bila memakai tabel agregat bulanan (`38 × 47 = 1.786` baris dasar) / partisi agregat nasional.
- **Pra-agregasi:** **Ya (WAJIB).**

### `Q-04` — Ranking Top-N provinsi
- **FR:** `FR-06`, `FR-08`, `FR-09`, `FR-10`, `FR-12`, `FR-G4`, `FR-G6`
- **Parameter:** `date_from`, `date_to` (`local_date`), `limit` (default `10`, maks `38`)
- **Filter:** `satellite`, `confidence`, opsional `exclude_non_veg` (SP-only). `OUTSIDE` selalu dikecualikan (`FR-06`, `SEM-02`).
- **Urutan:** `detection_count` turun (`DESC`), tie-break deterministik `province_code` naik (`ASC`) (`AC-06.3`).
- **Kardinalitas & ukuran hasil:** ≤ `38` baris (`VERIFIED`, 38 provinsi BIG; `< 10 KB`, `ASSUMPTION`). Pembacaan DB sama dengan `Q-02`/`Q-03` (dari agregat per provinsi, bukan tabel detail).
- **Pra-agregasi:** **Ya (WAJIB).**

### `Q-05` — Titik deteksi untuk peta interaktif (bounded per provinsi + rentang pendek)
- **FR:** `FR-03`, `FR-04`, `FR-08`, `FR-09`, `FR-10`, `FR-12`, `FR-24`, `FR-G6`
- **Parameter:** `province_code` (wajib, `HD-21`), `date_from`, `date_to` (`local_date`, maks **7 hari** per `NFR-08`), `limit` (default **2.000**, maks **5.000** per `NFR-06`)
- **Filter:** `satellite`, `confidence`, opsional `exclude_non_veg` (SP-only)
- **Urutan:** Deterministik (mis. `acq_datetime_utc DESC, detection_id ASC`) agar hasil terpotong (`truncated = true`) identik saat diulang (`AC-03.5`).
- **Kardinalitas & ukuran hasil:**
  - Terukur (`00-volume-estimates.md`, `VERIFIED`): per `(province, local_date)` p50 = `8` baris, p90 = `100`, p99 = `970`, maks = `13.217` (Kalimantan Tengah, 2026-10-22).
  - Untuk rentang 7 hari di puncak, hasil mentah dapat melebihi `limit`, sehingga query harus dibatasi `limit ≤ 5.000` dengan flag `truncated` dan `total_count` (dari agregat `Q-02` untuk notice `FR-03`).
  - Ukuran payload pada batas maks 5.000 titik target ≤ `2 MB` tanpa kompresi / ≤ `600 KB` gzip (`NFR-07`, `ASSUMPTION`).
- **Pra-agregasi:** **Tidak.** Membaca tabel detail deteksi per `(province_code, local_date)` dengan `N` kueri partisi harian (`N ≤ 7`), tanpa viewport query (`HD-21`).

### `Q-06` — Distribusi / histogram FRP
- **FR:** `FR-11` (`Should`), `FR-08`, `FR-09`, `FR-10`, `FR-12`, `FR-G6`
- **Parameter:** `date_from`, `date_to` (`local_date`), opsional `province_code`
- **Filter:** `satellite`, `confidence`, opsional `exclude_non_veg` (SP-only)
- **Urutan:** Batas bawah bin FRP naik (`ASC`)
- **Kardinalitas & ukuran hasil:** ±5–10 bin histogram (`< 20` baris, `< 2 KB`, `ASSUMPTION`).
- **Pra-agregasi:** **Ya (Disarankan).** Menghitung histogram langsung dari tabel detail untuk rentang multi-tahun tidak memenuhi `NFR-03`. Definisi bin tetap ditetapkan bersama di `D-P3-001` / `B-P3-001`.

### `Q-07` — Daftar hari tidak lengkap (`INCOMPLETE_DAY`)
- **FR:** `FR-G7`, `FR-01`, `FR-05`, `FR-07`
- **Parameter:** `date_from`, `date_to`, opsional `satellite`
- **Filter:** `satellite`
- **Urutan:** `date_utc` / `local_date` naik (`ASC`)
- **Kardinalitas & ukuran hasil:** `< 50` baris untuk seluruh rentang (`VERIFIED` dari daftar `missing_data` di kontrak A: `2023-07-19..22`, `2023-09-30`, `2024-02-04`, plus tanggal parsial bila ada).
- **Pra-agregasi:** Tidak perlu (1 partisi kecil).

### `Q-08` — Status pipeline & daftar run ingest terbaru
- **FR:** `FR-13`, `FR-14`, `FR-19`, `FR-20`, `FR-21`, `FR-22`, `FR-23`, `FR-24`
- **Parameter:** `limit` (default `20`, maks `100`), opsional `mode` (`backfill` | `incremental`)
- **Filter:** `mode`, `status`
- **Urutan:** `started_at_utc` turun (`DESC`)
- **Kardinalitas & ukuran hasil:** ≤ `100` baris run terbaru + 1 ringkasan `last_success_at` & `latest_acq_datetime_utc` per satelit (`< 50 KB`, `ASSUMPTION`).
- **Pra-agregasi:** Tidak perlu (bounded `limit`, partisi ber-bucket per bulan/tahun agar partisi tidak tumbuh tanpa batas).

---

## 3. Matriks Traceability `FR-xx ↔ Q-xx`

Setiap FR pada [01-functional-requirements.md](../../02-requirements/01-functional-requirements.md) dipetakan di bawah. Seluruh FR yang membaca data memiliki minimal satu `Q-xx`.

| FR | Deskripsi Singkat | MoSCoW | Query (`Q-xx`) | Catatan |
|---|---|---|---|---|
| `FR-G1` | Istilah "deteksi hotspot" | Must | — | Non-query (aturan label UI) |
| `FR-G2` | Disclaimer & waktu pembaruan terakhir | Must | `Q-01`, `Q-02` | `data_updated_at` dari metadata/agregat |
| `FR-G3` | Seluruh teks UI berbahasa Indonesia | Must | — | Non-query (aturan UI) |
| `FR-G4` | Tanggal lokal provinsi, simpan UTC | Must | `Q-02`, `Q-03`, `Q-04` | Kunci partisi/agregasi memakai `local_date` |
| `FR-G5` | Atribusi FIRMS, BIG, basemap | Must | `Q-01` | Metadata atribusi & `boundary_version` |
| `FR-G6` | Filter global tersinkron ke URL | Must | `Q-02`, `Q-03`, `Q-04`, `Q-05`, `Q-06` | Filter diterapkan seragam di seluruh `Q-xx` analitik |
| `FR-G7` | Tanggal `INCOMPLETE_DAY` tidak tampil sebagai 0 | Must | `Q-07`, `Q-03` | Digabungkan dengan hasil `Q-03` |
| `FR-G8` | State memuat, kosong, galat | Must | — | Non-query (aturan UI) |
| `FR-01` | Ringkasan total, provinsi aktif, timeline nasional | Must | `Q-02`, `Q-03`, `Q-07` | |
| `FR-02` | Jumlah deteksi `OUTSIDE` terpisah | Must | `Q-02` | Dari agregat/log `OUTSIDE`, bukan tabel detail layanan |
| `FR-03` | Peta titik per provinsi + rentang pendek + notice | Must | `Q-05`, `Q-02` | `Q-02` memberi `total_count` saat `truncated=true` |
| `FR-04` | Detail titik saat diklik | Must | `Q-05` | Atribut titik dikembalikan bersama fitur GeoJSON |
| `FR-05` | Timeline harian & bulanan (nasional / provinsi) | Must | `Q-03`, `Q-07` | |
| `FR-06` | Ranking Top-N provinsi (tanpa `OUTSIDE`) | Must | `Q-04` | |
| `FR-07` | Perbandingan dua periode | Should | `Q-02`, `Q-03`, `Q-07` | Memanggil kueri yang sama untuk 2 rentang tanggal |
| `FR-08` | Filter confidence (`l`/`n`/`h`) | Must | `Q-02`, `Q-03`, `Q-04`, `Q-05`, `Q-06` | Wajib menjadi dimensi kunci agregat |
| `FR-09` | Filter satelit (NOAA-20, NOAA-21, keduanya) | Must | `Q-01`, `Q-02`, `Q-03`, `Q-04`, `Q-05`, `Q-06` | Wajib menjadi dimensi kunci agregat |
| `FR-10` | Filter opsional tipe non-vegetasi (SP-only) | Should | `Q-02`, `Q-03`, `Q-04`, `Q-05`, `Q-06` | Aktif hanya bila rentang 100% SP (`SEM-05`) |
| `FR-11` | Histogram distribusi FRP | Should | `Q-06` | |
| `FR-12` | Pemilih provinsi memfilter seluruh panel | Must | `Q-01`, `Q-02`, `Q-03`, `Q-04`, `Q-05`, `Q-06` | |
| `FR-13` | Catatan setiap run ingest & metrik DQ | Must | `Q-08` | |
| `FR-14` | Endpoint status pipeline & daftar run | Must | `Q-08` | |
| `FR-15` | Eksperimen partisi/bucketing | Must | — | Non-query aplikasi (eksperimen `B-P7-001`) |
| `FR-16` | Eksperimen replikasi & failure 3 node | Should | — | Non-query aplikasi (eksperimen `B-P7-003`) |
| `FR-17` | Hosting HTTPS & Cassandra privat | Must | — | Non-query (infrastruktur/deploy) |
| `FR-18` | Reproduksibilitas fresh clone via README | Must | — | Non-query (reproduksibilitas) |
| `FR-19` | Poller NRT berkala & upsert idempoten | Must | `Q-08` | Baca checkpoint/run terakhir saat poll |
| `FR-20` | Indikator kesegaran data & peringatan basi | Must | `Q-01`, `Q-02`, `Q-08` | Menggunakan `latest_acq_datetime_utc` per satelit |
| `FR-21` | Backfill arsip SP dengan pipeline yang sama | Must | `Q-08` | Tercatat di log run yang sama |
| `FR-22` | Presedensi SP > NRT per `(satelit, tanggal UTC)` | Must | `Q-08` | Status produk aktif per tanggal tercatat di metadata |
| `FR-23` | Penggantian manual NRT → SP | Should | `Q-08` | Memeriksa/memperbarui status produk per tanggal |
| `FR-24` | Provenance setiap deteksi | Must | `Q-01`, `Q-05`, `Q-08` | Tersimpan di detail (`Q-05`), metadata (`Q-01`), run (`Q-08`) |

---

## 4. Ringkasan Implikasi untuk `B-P3-001` (Access Patterns & Skema)

1. **Tabel pra-agregasi wajib ada untuk `Q-02`, `Q-03`, `Q-04`** (dan disarankan untuk `Q-06`).
2. **Dimensi kunci agregat (`RC-03`):** Karena `FR-08` (`confidence`) dan `FR-09` (`satellite`) memfilter semua panel, kedua kolom ini harus menjadi bagian dari kunci agregat agar tidak ada `ALLOW FILTERING` atau scan tabel detail.
3. **Partisi detail `Q-05`:** Kunci partisi `(province_code, local_date)` menghasilkan maks `13.217` baris (~4–5 MB, `VERIFIED`/`ASSUMPTION`), sehingga aman untuk kueri peta bounded `≤ 7` hari (`NFR-08`).
4. **Filter `FR-10` (`exclude_non_veg`):** Karena hanya berlaku pada rentang 100% SP (`SEM-05`), `B-P3-001` perlu memutuskan apakah `is_vegetation` masuk kunci agregat atau ditangani lewat tabel/kolom agregat SP.
