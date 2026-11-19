# 06 — Interface Contracts

> Status: **kerangka kontrak** (`RECOMMENDATION`). Isi normatif setiap kontrak ditulis dan disetujui di **G3** oleh pemiliknya: A-P3-001, B-P3-001/002, C-P3-002, D-P3-001. Dokumen ini menetapkan **apa yang wajib ada** di tiap kontrak, siapa pemiliknya, dan cara versinya dikelola. Fakta tentang data sumber diberi label; field yang diusulkan berlabel `PROPOSAL`.

## 0. Register kontrak

| Kontrak | Dari → Ke | Pemilik (A) | Validator wajib | Artefak normatif | Tugas | Status |
|---|---|---|---|---|---|---|
| A. Source → ETL | FIRMS → pipeline | R1 | R2 | `docs/01-dataset/02-data-dictionary.md` | A-P1-003 | `PENDING` (G1) |
| B. ETL → Cassandra | pipeline → db | R1 (event) / R2 (persistensi) | R2 / R1 | `docs/03-specs/data/02-canonical-event-contract.md` + `samples/*.jsonl` | A-P3-001, B-P5-002 | `PENDING` (G3) |
| C. Cassandra → Backend | db → api | R2 | R3 | `docs/03-specs/database/02-access-patterns.md`, `03-data-model.md`, `schema-v1.cql` | B-P3-001/002 | `PENDING` (G3) |
| D. Backend → Frontend | api → web | R3 | R4 | `docs/03-specs/api/openapi.yaml` | C-P3-002 | `PENDING` (G3) |
| E. Frontend → User | web → pengguna | R4 | R1 (terminologi), R3 | `docs/03-specs/ui/01-ui-spec.md` | D-P3-001 | `PENDING` (G3) |

**Versi:** setiap kontrak memakai semver di header (`contract_version: 1.0.0`).
- *Patch*: perbaikan teks tanpa mengubah bentuk.
- *Minor*: menambah field opsional; konsumen lama tetap jalan.
- *Major*: mengubah atau menghapus field, atau mengubah makna. **Wajib change request** ([10 §5](10-phase-gates.md#5-change-management)) dan persetujuan semua konsumen.

---

## A. Source → ETL

**Fakta terukur dari data Fase 1** (`VERIFIED`, unduhan 2026-11-19, bbox `94,-11.5,141.5,6.5`):

| Aspek | Fakta | Implikasi kontrak |
|---|---|---|
| File sumber | Respons CSV Area API, satu file per request (`{SOURCE}/{start}_{N}d.csv`) + `manifest.csv` (SHA-256, waktu ambil) | Raw zone tidak berubah setelah ditulis; pipeline membaca dari file, bukan langsung dari API |
| Identitas produk | Ditentukan dari **source ID request** (`VIIRS_NOAA20_SP`, `…_NRT`, `VIIRS_NOAA21_*`). Kolom `satellite` = `N20`/`N21`. | `source_id` dan `processing_level` (SP/NRT) wajib dibawa dari metadata request, bukan ditebak dari isi |
| Header SP | `latitude,longitude,bright_ti4,scan,track,acq_date,acq_time,satellite,instrument,confidence,version,bright_ti5,frp,daynight,type` | — |
| Header NRT | Sama, **tanpa `type`** | `type` nullable; NRT tidak punya atribusi sumber statis (keterbatasan OQ-12) |
| `version` | SP = `2`, NRT = `2.0NRT` | Dinormalisasi ke `processing_level`; nilai mentah tetap disimpan |
| `acq_time` | Integer HHMM **tanpa nol di depan** (contoh `337` = 03:37). Dokumentasi resmi: UTC. | Pad 4 digit, lalu gabung dengan `acq_date` menjadi UTC |
| `confidence` VIIRS | Dokumentasi: low/nominal/high. Kode huruf yang teramati di data: lihat data dictionary (A-P1-003). | Simpan mentah + kelas ternormalisasi |
| Cakupan | bbox memuat titik negara tetangga | Wajib clip ke batas Indonesia (status wilayah, OQ-11) |
| Hari hilang | Tabel resmi FIRMS `missing_data`: NOAA-20 SP 2023-07-19..22, 2023-09-30, 2024-02-04 | Kelengkapan harian dilaporkan; hari kosong ≠ nol deteksi |

Wajib ada di kontrak A (final di data dictionary): tipe dan rentang setiap kolom, aturan null, aturan nilai di luar rentang (→ DQ), dan pemetaan setiap kolom ke field canonical.

## B. ETL → Cassandra (canonical event)

Field minimum yang **diusulkan** (`PROPOSAL`, final di A-P3-001, diverifikasi B):

| Field | Tipe logis | Null | Asal / aturan |
|---|---|---|---|
| `detection_id` | text (hash deterministik) | tidak | Fungsi dari `satellite`, `acq_datetime_utc`, `latitude`, `longitude` pada presisi sumber. Tidak bergantung urutan input atau waktu ingest. Dipakai bersama aturan presedensi SP > NRT dari A-P1-007. |
| `source_id`, `processing_level`, `version_raw` | text | tidak | Metadata request + kolom `version` |
| `satellite`, `instrument` | text | tidak | Kolom sumber |
| `acq_datetime_utc` | timestamp (UTC) | tidak | `acq_date` + `acq_time` yang di-pad |
| `acq_date_local`, `local_tz` | date, text (WIB/WITA/WIT) | ya, bila di luar provinsi | Zona waktu provinsi (OQ-08) |
| `latitude`, `longitude` | double | tidak | Presisi sumber dipertahankan |
| `province_code`, `province_name` | text | ya | Snapshot batas BIG (`boundary_version`) |
| `region_status` | text enum (`PROVINCE`, `OUTSIDE`) | tidak | OQ-11 |
| `confidence_raw`, `confidence_class` | text | tidak | — |
| `frp`, `bright_ti4`, `bright_ti5`, `scan`, `track` | double | tidak (DQ menolak non-numerik) | — |
| `daynight` | text | tidak | Catatan: aturan NRT (orbit) ≠ SP (sudut zenit matahari) |
| `type` | int | ya (NRT) | — |
| `source_file_sha256`, `fetched_at_utc`, `ingest_run_id`, `boundary_version` | text/timestamp | tidak | Provenance |

**Semantik pemuatan (wajib):**
1. Upsert berdasarkan identitas. Menulis ulang event yang sama tidak mengubah jumlah baris.
2. Agregat dihitung ulang sebagai nilai absolut. Tidak ada increment dan tidak ada counter table.
3. Batch hanya untuk partisi yang sama.
4. Rekaman yang ditolak tidak masuk tabel event, tetapi tercatat dengan reason code di run log/rejected store.
5. Writer milik R2 (`db/`). Pipeline R1 memanggil API writer, bukan menulis CQL sendiri.

**Contoh record wajib:** ≥20 baris JSONL dari data nyata. Harus mencakup deteksi malam yang tanggal lokalnya berbeda dari tanggal UTC, titik di luar provinsi, SP dan NRT, serta NOAA-20 dan NOAA-21.

## C. Cassandra → Backend

Kontrak berbentuk **katalog query**. Setiap metode repository C memetakan tepat satu Q-xx yang disetujui. Q-xx di bawah hanya contoh turunan dari fitur MVP (`PROPOSAL`). Daftar final ada di B-P2-001 dan B-P3-001.

| Metode repository (usulan) | Fitur | Parameter | Batas & urutan | Catatan desain yang **wajib dijawab di B-P3-001** |
|---|---|---|---|---|
| `get_timeline(scope, province_code?, granularity, date_from, date_to, filters)` | #1, #3 | rentang tanggal lokal | urut tanggal naik | Bila filter confidence/satelit berlaku untuk agregat, dimensi itu harus ada di kunci agregat. Tanpa itu, filter tidak bisa dilayani tanpa scan. |
| `get_province_ranking(date_from, date_to, filters, limit)` | #4 | — | urut jumlah turun, top-N | Ranking nasional lintas partisi: hitung dari agregat per provinsi (38 baris), bukan dari event |
| `get_province_detail(province_code, …)` | #8 | — | — | — |
| `get_detections(province_code, date_from, date_to, filters, limit)` | #2 | rentang pendek | batas titik (NFR) + flag `truncated` | Peta per provinsi + tanggal (C-11). Viewport/bbox bebas bukan pola Cassandra (HD-21). |
| `get_pipeline_status()` | #9 | — | run terakhir per mode | Satu partisi |

Aturan: prepared statements; tanpa `ALLOW FILTERING`; consistency level didokumentasikan; repository tidak membuat atau mengubah tabel.

## D. Backend → Frontend (OpenAPI)

Usulan bentuk (`PROPOSAL`, final di C-P3-002):

| Endpoint | Metode | Kegunaan |
|---|---|---|
| `/health`, `/ready` | GET | liveness & readiness (cek Cassandra) |
| `/api/v1/meta` | GET | daftar provinsi, rentang data tersedia, atribusi, versi batas |
| `/api/v1/summary` | GET | KPI periode |
| `/api/v1/timeline` | GET | seri harian/bulanan, nasional atau per provinsi |
| `/api/v1/provinces/ranking` | GET | top-N provinsi |
| `/api/v1/provinces/{code}` | GET | ringkasan satu provinsi |
| `/api/v1/detections` | GET | titik peta (GeoJSON FeatureCollection) |
| `/api/v1/pipeline/status` | GET | run terakhir, kesegaran data |

Konvensi yang wajib tercantum di OpenAPI:
- **Tanggal:** parameter `date_from`/`date_to` adalah tanggal **lokal** (ISO `YYYY-MM-DD`) sesuai SEM-xx. Semua timestamp di respons memakai UTC ISO 8601 dengan `Z`.
- **Filter:** `confidence` (multi), `satellite` (multi), `province_code`. Nilai yang tidak dikenal → 422.
- **Bounded result:** setiap respons list punya `limit` dan `truncated`. Peta tidak pernah mengirim lebih dari batas NFR.
- **Error:** `{"error": {"code": "string", "message": "string", "details": {}, "request_id": "string"}}` untuk 4xx/5xx.
- **Kesegaran:** respons agregat menyertakan `data_updated_at` (UTC).
- **Contoh:** setiap respons punya contoh dari sampel canonical nyata. Contoh ini menjadi sumber mock D-P4-002.

## E. Frontend → User

| Perilaku | Aturan |
|---|---|
| Terminologi | Selalu "deteksi hotspot", tidak pernah "kebakaran" (charter §3) |
| Disclaimer ilmiah | Terlihat di setiap halaman; teks final disetujui tim |
| Atribusi | FIRMS (teks dari halaman Acknowledgments), BIG (batas wilayah), penyedia basemap |
| Kesegaran | Indikator "data terakhir diperbarui …" dari `data_updated_at`; peringatan bila melebihi ambang NFR |
| Filter | Tersinkron ke URL; perubahan filter memperbarui semua panel |
| Peta | Notice jelas bila `truncated = true`; tidak menampilkan titik melebihi batas |
| State | Setiap panel punya state loading, kosong (dengan penjelasan), dan error (pesan + coba lagi) |
| Hari tanpa data | Dibedakan dari nol deteksi bila sumber menandai data hilang |
| Perbandingan periode (Should) | Hanya produk/satelit yang sama; catatan metodologi tampil |

## 7. Checklist mock-to-real

Dijalankan saat **C-P6-007** (repository fake → Cassandra) dan **D-P6-007** (mock API → API nyata). Target G6.

- [ ] `openapi.yaml` di branch utama = versi yang dipakai mock (hash atau versi sama).
- [ ] Contract test C lulus terhadap API nyata dengan data nyata.
- [ ] Untuk fixture yang sama, hasil repository fake = hasil repository Cassandra.
- [ ] Flag mock di web dimatikan; tidak ada handler mock yang terpanggil (cek log).
- [ ] Setiap halaman Must dibuka dengan filter default, filter ekstrem, dan rentang kosong.
- [ ] Perbedaan bentuk data dicatat sebagai CR, **bukan** ditambal diam-diam di frontend.
- [ ] Waktu respons diukur terhadap NFR; hasil dicatat.
- [ ] Mock tetap tersedia untuk test, tetapi tidak aktif di build produksi.
