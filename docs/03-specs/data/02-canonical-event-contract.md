# 02 — Kontrak Canonical Event (A-P3-001)

```yaml
contract: B (ETL → Cassandra), bagian event
contract_version: 1.0.0
status: DRAF            # CE-01…CE-09 disetujui R1 (Lanang, 2026-11-26). PENDING: pemetaan CQL + CE-01/03/04 (R2, §3); G3
owner: R1 (Lanang)      # pemilik event; R2 (Abi Funn) pemilik persistensi dan validator wajib
schema: docs/03-specs/data/samples/canonical-event.schema.json   # JSON Schema 2020-12
samples: docs/03-specs/data/samples/canonical-events.sample.jsonl  # 26 record dari data nyata
```

> Fase 3 · Draf agen 2026-11-26 · Label: [legenda](../../00-discovery/README.md#label-status-informasi). Isi berasal dari keputusan yang sudah disetujui (OQ-08…OQ-12, HD-08…HD-11, [CR-03](../../change-requests/CR-03.md)), [data dictionary](../../01-dataset/02-data-dictionary.md), [aturan DQ](../../01-dataset/06-data-quality-rules.md), [semantik data](01-data-semantics.md), dan kerangka [06 §B](../../10-execution-plan/06-interface-contracts.md#b-etl--cassandra-canonical-event). Pilihan baru yang dibuat dokumen ini diberi ID **CE-xx** ([§2](#2-keputusan-yang-butuh-konfirmasi)). CE-01…CE-07 disetujui Lanang (R1) 2026-11-26 di sesi Claude Code. CE-08 dan CE-09 muncul dari pemeriksaan edge case ([§11a](#11a-edge-case)) dan disetujui Lanang pada sesi yang sama ("yes I allow that").

## 0. Artefak

| File | Isi | Normatif? |
|---|---|---|
| `02-canonical-event-contract.md` (dokumen ini) | Arti setiap field dan aturan | Ya |
| `samples/canonical-event.schema.json` | Bentuk record (tipe, null, enum, aturan bersyarat) | Ya, untuk bentuk |
| `samples/canonical_event.py` | Fungsi referensi: identitas, waktu, zona, flag. Satu definisi yang dipakai builder dan validator | Bentuk yang bisa dijalankan dari §4–§7 |
| `samples/canonical-events.sample.jsonl` | 26 event dari raw zone Fase 1 | Contoh |
| `samples/canonical-events.sample.cases.csv` | Kasus tiap sampel + file dan nomor baris sumbernya | Jejak |
| `samples/build_samples.py`, `samples/validate_samples.py` | Pembangun sampel (deterministik) dan validator (termasuk unit edge case) | Alat |
| `samples/audit_raw_zone.py` | Audit kontrak terhadap **semua** baris raw zone Fase 1 | Alat |
| `samples/.gitattributes` | Memaksa akhir baris LF agar sampel identik byte di semua OS | Alat |

Bila dokumen ini dan skema berbeda, **dokumen ini yang berlaku** dan skema wajib diperbaiki (patch).

## 1. Ruang lingkup

Satu **canonical event** = satu baris produk FIRMS VIIRS 375 m (NOAA-20/NOAA-21, SP/NRT) yang **lolos DQ dan sudah didedup**, sudah dinormalisasi, dan sudah diperkaya wilayah. Event adalah keluaran tahap ETL terakhir sebelum writer milik R2 (`db/`).

Tidak termasuk kontrak ini (pemilik lain):

| Hal | Di mana |
|---|---|
| Baris yang ditolak (DQ-01…06, DQ-13…15), run log, checkpoint, hitungan duplikat | A-P3-002 (ETL spec) |
| Tabel, partisi, clustering, CQL, agregat | B-P3-001/002 (R2) |
| Cara writer menulis (batch, prepared statement, retry) | B-P5-002 (R2) |
| Arti angka dashboard | [01-data-semantics](01-data-semantics.md) |

## 2. Keputusan yang butuh konfirmasi

Baris di bawah berawal dari **rekomendasi agen**. Dokumen, skema, dan sampel ditulis memakai rekomendasi ini. **CE-01…CE-07 disetujui Lanang (R1), 2026-11-26, di sesi Claude Code** ("aku setuju semua, outside hitung di run log aja, boundary version ok, dan version_raw tetap disimpan"). Untuk CE-01, CE-03, dan CE-04 yang juga dimiliki R2, persetujuan R2 diberikan bersama konfirmasi pemetaan CQL (§3). CE-08 dan CE-09 ditemukan saat pemeriksaan edge case dan disetujui Lanang (R1) pada hari yang sama. Mengubah satu pilihan = membangun ulang sampel dengan `build_samples.py`.

| ID | Keputusan | Rekomendasi (dipakai di draf ini) | Alternatif | Pemilik | Status |
|---|---|---|---|---|---|
| **CE-01** | Bentuk `detection_id` | SHA-256 hex (64 karakter) dari string identitas `processing_level\|satellite\|YYYY-MM-DDTHH:MMZ\|lat\|lon`, koordinat dinormalisasi dari **teks sumber** ([§4](#4-identitas-detection_id)) | (a) 128 bit pertama saja (32 hex): lebih hemat ±32 B/baris, risiko tabrakan tetap dapat diabaikan; (b) UUIDv5 dari string yang sama | R1 + R2 | **Disetujui** R1 2026-11-26; R2 ⏳ (§3) |
| **CE-02** | Nama field dan nilai enum | Nama 06 §B dipertahankan bila ada (`province_code`, `confidence_raw`, …). Nama baru: `local_date`, `local_tz`, `source_acq_date_utc`, `dq_flags`, `source_file`. `region_status` ∈ {`INSIDE`, `OUTSIDE`} mengikuti SEM-02, bukan `PROVINCE` dari 06 | Ikuti nama SEM (`province`, `zone`, `confidence`) | R1 | **Disetujui** R1 2026-11-26 |
| **CE-03** | Event OUTSIDE | OUTSIDE **adalah** canonical event yang sah (`province_code`, `province_name`, `local_date`, `local_tz` = null), agar satu bentuk dipakai untuk hitungan run log dan monitoring. Sesuai KEP-02 (Lanang, 2026-11-23: "OUTSIDE hanya di raw zone"), **pipeline tidak mengirim event OUTSIDE ke writer tabel layanan**; jumlahnya masuk run log ([§9](#9-aturan-pemuatan)) | Writer menerima OUTSIDE dan R2 menyimpannya di tabel terpisah | R1 + R2 | **Disetujui** R1 2026-11-26; R2 ⏳ (§3) |
| **CE-04** | Provenance vs idempotensi | Field dibagi dua: **isi** (ditentukan baris sumber + batas wilayah) dan **muat** (`source_file`, `source_file_sha256`, `fetched_at_utc`, `ingest_run_id`). Upsert menimpa field muat dengan nilai pemuatan terakhir. Uji idempotensi = jumlah baris + checksum atas field **isi** ([§8](#8-provenance-dan-idempotensi)) | Field muat ditulis sekali (first-seen) → butuh LWT `IF NOT EXISTS` (mahal di Cassandra) | R1 + R2 | **Disetujui** R1 2026-11-26; R2 ⏳ (§3) |
| **CE-05** | Flag DQ di event | Hanya flag yang merupakan fungsi baris + batas: `TI4_SATURATED`, `FRP_ZERO`, `NON_VEGETATION_TYPE`, `MULTI_POLYGON`. `DUPLICATE`/`DUPLICATE_CONFLICT` dan `INCOMPLETE_DAY` dicatat di run log/tabel cakupan, bukan di event. `OUTSIDE` tidak diulang sebagai flag (sudah di `region_status`) | Semua flag DQ di event | R1 | **Disetujui** R1 2026-11-26 |
| **CE-06** | Format `boundary_version` | `BIG-2026-06-g0.001-0382eeeeb559` (sumber-edisi-generalisasi-12 hex pertama SHA-256 snapshot) | SHA-256 penuh; nama bebas | R1 | **Disetujui** R1 2026-11-26 |
| **CE-07** | Format `ingest_run_id` | Kontrak hanya mewajibkan teks 1–128 karakter, tidak kosong. Formatnya ditetapkan A-P3-002 (run log). Sampel memakai `sample-A-P3-001` (`ILUSTRASI`) | Tetapkan UUID sekarang | R1 (A-P3-002) | **Disetujui** R1 2026-11-26 |
| **CE-08** | Nilai yang bisa di-parse tetapi di luar domain kontrak dan tidak tercakup DQ-01…DQ-15 (`type` ∉ {0,1,2,3}, `daynight` ∉ {D,N}, `instrument` ≠ `VIIRS`, `bright_ti4`/`bright_ti5`/`scan`/`track` ≤ 0, `frp` < 0, tanggal tidak nyata, kode provinsi di luar 38) | **Tolak baris** dengan reason code baru `CONTRACT_VIOLATION`, tercatat di run log seperti penolakan DQ lain. Setiap event diperiksa terhadap skema sebelum dikirim ke writer. Dampak di data Fase 1: lihat [§11a](#11a-edge-case) | (a) Simpan + flag baru; (b) biarkan writer/Cassandra menolak (gagal di tempat yang salah, tanpa reason code) | R1 | **Disetujui** R1 2026-11-26 |
| **CE-09** | Baris **SP** dengan `type` kosong | **Terima**, `type = null` (DQ-02 yang disetujui G1 mengecualikan `type` dari aturan nilai kosong; perlakuannya sama dengan NRT: dihitung, tidak ikut filter tipe) | Tolak sebagai `MISSING_FIELD` (mengubah arti DQ-02 → CR) | R1 | **Disetujui** R1 2026-11-26 |

Keputusan terkait yang juga disetujui Lanang 2026-11-26: **`version_raw` tetap disimpan** di samping `processing_level` (alasan di [§3](#3-field), catatan `version_raw`).

Keputusan lain di dokumen ini hanya **menerapkan** keputusan yang sudah final: CR-03 (`processing_level` masuk identitas), OQ-08 (UTC + tanggal lokal per provinsi), OQ-09 (semua confidence disimpan), OQ-11 (titik luar provinsi diberi status khusus), OQ-12 (`type` nullable), HD-10 (satu produk per `(satellite, tanggal UTC)`), HD-11 (DQ-01…DQ-15, tanpa snapping), SEM-02 butir 2 (poligon pertama).

## 3. Field

Urutan = urutan di skema. "Null" = boleh `null` di JSON. Kolom **CQL (usulan)** hanya usulan tipe untuk dikonfirmasi R2 (kriteria penerimaan); nama tabel, kunci, dan tata letak fisik adalah milik B-P3-002.

| # | Field | JSON | Null | Kelompok | Asal / aturan | CQL (usulan) |
|---|---|---|---|---|---|---|
| 1 | `detection_id` | string `^[0-9a-f]{64}$` | tidak | isi | [§4](#4-identitas-detection_id) | `text` |
| 2 | `source_id` | enum 4 nilai | tidak | isi | Metadata request (`VIIRS_NOAA20_SP`, `VIIRS_NOAA21_SP`, `VIIRS_NOAA20_NRT`, `VIIRS_NOAA21_NRT`), bukan ditebak dari isi | `text` |
| 3 | `processing_level` | `SP` \| `NRT` | tidak | isi | Dari `source_id` | `text` |
| 4 | `version_raw` | `2` \| `2.0NRT` | tidak | isi | Kolom `version` apa adanya; harus cocok dengan `source_id` (DQ-14). Disimpan walau saat ini bisa diturunkan dari `processing_level` (lihat catatan di bawah tabel) | `text` |
| 5 | `satellite` | `N20` \| `N21` | tidak | isi | Kolom `satellite`; harus cocok dengan `source_id` (DQ-15) | `text` |
| 6 | `instrument` | `VIIRS` | tidak | isi | Kolom `instrument` | `text` |
| 7 | `acq_datetime_utc` | string `YYYY-MM-DDTHH:MM:00Z` | tidak | isi | `acq_date` + `acq_time` di-pad 4 digit ([§5](#5-waktu)) | `timestamp` |
| 8 | `source_acq_date_utc` | string `YYYY-MM-DD` | tidak | isi | Kolom `acq_date` (tanggal UTC). Kunci penggantian NRT→SP per `(satellite, source_acq_date_utc)` (HD-10, [04 §4](../../01-dataset/04-nrt-vs-sp-and-latency.md#4-masukan-untuk-fase-berikutnya)) | `date` |
| 9 | `local_date` | string `YYYY-MM-DD` | **ya** (OUTSIDE) | isi | Tanggal `acq_datetime_utc` + offset zona provinsi (SEM-03) | `date` |
| 10 | `local_tz` | `WIB` \| `WITA` \| `WIT` | **ya** (OUTSIDE) | isi | Zona dari `province_code` ([§6](#6-wilayah-dan-id-spasial)) | `text` |
| 11 | `latitude` | number −90…90 | tidak | isi | Kolom `latitude`, nilai sumber tanpa pembulatan | `double` |
| 12 | `longitude` | number −180…180 | tidak | isi | Kolom `longitude`, sama | `double` |
| 13 | `region_status` | `INSIDE` \| `OUTSIDE` | tidak | isi | Point-in-polygon terhadap snapshot BIG (OQ-11, DQ-07) | `text` |
| 14 | `province_code` | 38 kode BIG `KDPPUM` | **ya** (OUTSIDE) | isi | Poligon pertama yang memuat titik (SEM-02 butir 2) | `text` |
| 15 | `province_name` | string | **ya** (OUTSIDE) | isi | `WADMPR` BIG apa adanya (mis. `Daerah Khusus Ibukota Jakarta`) | `text` |
| 16 | `boundary_version` | string | tidak | isi | Versi snapshot batas ([§6](#6-wilayah-dan-id-spasial), CE-06) | `text` |
| 17 | `bright_ti4` | number > 0 (K) | tidak | isi | Kolom sumber | `double` |
| 18 | `bright_ti5` | number > 0 (K) | tidak | isi | Kolom sumber | `double` |
| 19 | `scan` | number > 0 | tidak | isi | Kolom sumber (satuan km: `ASSUMPTION`, data dictionary) | `double` |
| 20 | `track` | number > 0 | tidak | isi | Kolom sumber | `double` |
| 21 | `frp` | number ≥ 0 (MW) | tidak | isi | Kolom sumber; 0 diberi flag `FRP_ZERO` | `double` |
| 22 | `confidence_raw` | `l` \| `n` \| `h` | tidak | isi | Kolom `confidence` (DQ-13) | `text` |
| 23 | `confidence_class` | `low` \| `nominal` \| `high` | tidak | isi | Pemetaan tetap dari `confidence_raw` | `text` |
| 24 | `daynight` | `D` \| `N` | tidak | isi | Kolom sumber. Aturan SP (zenit matahari) ≠ NRT (orbit) | `text` |
| 25 | `type` | 0 \| 1 \| 2 \| 3 | **ya**: selalu null di NRT; di SP null hanya bila kolomnya kosong (CE-09) | isi | Kolom `type` (SP saja); NRT tidak punya kolom ini (OQ-12) | `int` |
| 26 | `dq_flags` | array unik, terurut | tidak (boleh `[]`) | isi | [§7](#7-flag-dq) | `set<text>` |
| 27 | `source_file` | string `<source_id>/[subfolder/…]<nama>.csv` | tidak | muat | Path relatif raw zone (`data/firms/raw/`) dari file yang dimuat. Subfolder diperbolehkan (tata letak raw zone incremental ditetapkan A-P3-002); segmen `..` dilarang | `text` |
| 28 | `source_file_sha256` | string 64 hex | tidak | muat | SHA-256 file sumber dari `manifest.csv` | `text` |
| 29 | `fetched_at_utc` | string ISO-8601 UTC `…Z` | tidak | muat | Waktu ambil file dari `manifest.csv` | `timestamp` |
| 30 | `ingest_run_id` | string 1–128 | tidak | muat | ID run (CE-07) | `text` |

Aturan bersyarat (ditegakkan skema):
- `region_status = INSIDE` ⇔ `province_code`, `province_name`, `local_date`, `local_tz` terisi; `OUTSIDE` ⇔ keempatnya `null`.
- `processing_level = SP` ⇔ `version_raw = "2"`, `source_id` dan `source_file` produk `_SP`, `type` ∈ {0,1,2,3} atau null (CE-09); `NRT` ⇔ `"2.0NRT"`, `_NRT`, `type = null`.
- `province_name` = nama BIG untuk `province_code` (tabel di `canonical_event.py`, dicocokkan dengan snapshot); tanggal harus tanggal kalender nyata; angka harus berhingga (bukan NaN/Infinity). Ketiganya diperiksa validator (`[rules]`), bukan skema.
- `satellite` cocok dengan `source_id` dan `source_file`; `confidence_class` cocok dengan `confidence_raw`.
- Tidak ada field lain (`additionalProperties: false`). Field opsional baru = versi *minor* ([§10](#10-versi-dan-perubahan)).

Catatan `version_raw` (disetujui Lanang 2026-11-26): dengan DQ-14 saat ini nilainya selalu berpasangan dengan `processing_level` (`2` ↔ SP, `2.0NRT` ↔ NRT). Field ini tetap disimpan karena (1) FR-13/US-13 meminta tingkat pemrosesan **dan** versi produk sebagai dua hal; (2) `version` mengandung **koleksi** (Collection 2), sedangkan `processing_level` hanya level. Bila koleksi baru diterima lewat CR atas DQ-14, hanya `version_raw` yang membedakan event SP koleksi lama dan baru selama transisi. Ketidakkonsistenan dicegah skema (mutasi "version_raw tidak cocok" ditolak).

Catatan untuk R2 (`RECOMMENDATION`, keputusan di B-P3-002): `source_file_sha256` (64 B) dan `fetched_at_utc` bergantung pada file, bukan deteksi. Secara fisik keduanya bisa disimpan di tabel file dan cukup dirujuk lewat `source_file` ([00-volume-estimates](../database/00-volume-estimates.md)). Kontrak logis tetap seperti di atas.

## 4. Identitas (`detection_id`)

Dasar: [04 §2](../../01-dataset/04-nrt-vs-sp-and-latency.md#2-aturan-tumpang-tindih-nrtsp-yang-diusulkan-keputusan-hd-10), CR-03, A-08. Bentuk: CE-01.

```
identity = processing_level "|" satellite "|" acq_datetime_utc("YYYY-MM-DDTHH:MMZ") "|" canon(latitude_text) "|" canon(longitude_text)
detection_id = lowercase_hex(SHA-256(ASCII(identity)))
canon(x) = teks sumber (desimal biasa ATAU notasi ilmiah, mis. "-7e-05") → desimal tanpa eksponen, tanpa nol di belakang,
           tanpa titik di akhir, "-0" → "0".   Contoh: "-7e-05" → "-0.00007";  "-2.886740" → "-2.88674"
```

Contoh dari sampel #1 (`VERIFIED`, dihitung sesi ini; baris 2 `VIIRS_NOAA20_SP/2023-01-01_5d.csv`: `-2.88674,116.2264,…,2023-01-01,508,N20,…`):

```
SP|N20|2023-01-01T05:08Z|-2.88674|116.2264  →  91ff7b55df045269b4915214e53dea278a1b6e6237a1958e7ebe663126df3d45
```

Sifat yang dijamin:
1. **Deterministik dan bebas urutan.** Hanya bergantung pada lima nilai dari baris sumber dan metadata request. Tidak bergantung pada urutan input, waktu ingest, file, run, atau versi batas wilayah. Validator mengujinya dengan 50 pengacakan urutan.
2. **Presisi sumber.** Koordinat diambil dari **teks** CSV sebelum diubah ke `double`, sehingga pembulatan floating-point tidak memengaruhi identitas. Normalisasi `canon` membuat `-1.50000` dan `-1.5` menghasilkan ID yang sama (sumber kadang membuang nol di belakang, data dictionary §3).
3. **NRT dan SP berbeda ID** (CR-03). Deteksi yang sama di NRT dan SP **tidak** dicocokkan per ID (`acq_time` bergeser ±1–2 menit; hanya 39% kunci cocok persis, A-09). Penggantian NRT→SP dilakukan per `(satellite, source_acq_date_utc)` (HD-10).
4. **Konsumen tidak menghitung ulang ID.** `detection_id` adalah kunci buram. Hanya pipeline (dari teks sumber) yang membuatnya. Menghitung ulang dari `double` di bahasa lain (mis. Java `Double.toString` → `1.0E-4`) bisa berbeda.
5. **Duplikat dalam satu produk** (DQ-08: 0 · 1 · 1 · 0 kasus di Fase 1) menghasilkan ID sama dan menjadi satu event. Pemilihan nilai saat berbeda (FRP tertinggi, lalu `bright_ti4` tertinggi) dilakukan pipeline dalam satu run. Antar-run, upsert menimpa (catatan untuk A-P3-002/B-P5-002).

## 5. Waktu

| Aturan | Isi |
|---|---|
| Kanonis | `acq_datetime_utc` = `acq_date` + `acq_time` (di-pad ke 4 digit: `508` → `05:08`), UTC, resolusi menit, detik selalu `00`, ditulis dengan akhiran `Z` |
| Tanggal UTC sumber | `source_acq_date_utc` = `acq_date` = tanggal dari `acq_datetime_utc` |
| Tanggal lokal | `local_date` = tanggal dari `acq_datetime_utc` + offset `local_tz` (WIB +7, WITA +8, WIT +9). Tanpa DST. Zona ditentukan **provinsi**, bukan koordinat (SEM-03) |
| Lintas tanggal | UTC ≥ 17:00 (WIB), ≥ 16:00 (WITA), ≥ 15:00 (WIT) → `local_date` = `source_acq_date_utc` + 1 hari. Lintasan malam Indonesia ±15–19 UTC sering membelah dua tanggal lokal |
| OUTSIDE | `local_date` = `local_tz` = null (tidak punya provinsi) |
| Waktu muat | `fetched_at_utc` (dari manifest), UTC dengan `Z` |

## 6. Wilayah dan ID spasial

- **ID spasial = `province_code`**: kode provinsi BIG `KDPPUM` (2 digit, 38 nilai di skema), dari snapshot `BATAS_KABKOTA_AR` edisi Juni 2026 yang digeneralisasi 0,001° (HD-08). Koordinat titik (`latitude`, `longitude`) dibawa apa adanya. Kunci spasial tambahan untuk peta (grid, geohash, bucket) belum ada karena kebutuhan query B-P2-001 belum tersedia. Bila dibutuhkan, kunci itu ditambahkan sebagai field opsional (*minor*) atau diturunkan R2 di model fisik.
- **Kabupaten/kota** (`KDPKAB`) tidak masuk v1 (kabupaten = *Could*, OQ-06). Bisa ditambah sebagai field opsional (*minor*).
- **Penetapan:** ray casting even-odd terhadap semua poligon; titik di >1 poligon diberi provinsi dari **poligon pertama** menurut urutan fitur BIG (urutan file `part_*.geojson` lalu urutan fitur) dan flag `MULTI_POLYGON`. Tanpa snapping (HD-11). Algoritmanya sama dengan `scratch/phase1/pip_assign.py`.
- **`boundary_version`** = `BIG-2026-06-g0.001-0382eeeeb559`. 12 hex terakhir adalah awal SHA-256 gabungan 22 file snapshot berurutan nama: `0382eeeeb559991a41dbb9ba84d593740c4cea7614703f4c2a93d10495f3e478` (`VERIFIED` sesi ini; sama dengan [05-boundary-sources](../../01-dataset/05-boundary-sources.md)). Mengganti batas = versi baru = proses ulang `region_status`, `province_*`, `local_*` (SEM-02). `detection_id` tidak berubah.

Zona per kode provinsi. Diturunkan dari tabel SEM-03, yang memakai nama; dipetakan ke kode karena dua nama BIG berbeda dari tabel SEM-03 (`Daerah Khusus Ibukota Jakarta`, `Daerah Istimewa Yogyakarta`). Ke-38 kode dan nama sudah dicocokkan dengan snapshot (`VERIFIED`). Ketepatan zona tetap `AI-PRIOR` sampai A-P5-005.

| Zona | `province_code` |
|---|---|
| WIB (18) | 11 12 13 14 15 16 17 18 19 21 31 32 33 34 35 36 61 62 |
| WITA (12) | 51 52 53 63 64 65 71 72 73 74 75 76 |
| WIT (8) | 81 82 91 92 93 94 95 96 |

## 7. Flag DQ

`dq_flags` = himpunan terurut dari flag yang **murni fungsi baris + batas wilayah** (CE-05), sehingga memuat ulang data yang sama selalu menghasilkan flag yang sama. Flag tidak mengubah hitungan dashboard (SEM-09).

| Flag | Kondisi | Aturan |
|---|---|---|
| `TI4_SATURATED` | `bright_ti4` = 367,0 | DQ-09 |
| `FRP_ZERO` | `frp` = 0 | DQ-10 |
| `NON_VEGETATION_TYPE` | `type` ∈ {1, 2, 3} | DQ-11 |
| `MULTI_POLYGON` | titik di >1 poligon snapshot. Poligon BIG adalah **kab/kota**, jadi flag ini juga muncul bila kedua poligon berada di provinsi yang sama (94 dari 101 koordinat Fase 1; hanya 7 melintasi batas provinsi, [§11a](#11a-edge-case)) | DQ-07b |

Bukan flag event: `OUTSIDE` (= `region_status`), `DUPLICATE`/`DUPLICATE_CONFLICT` (DQ-08, hitungan run log), `INCOMPLETE_DAY` (DQ-12, sifat tanggal di tabel cakupan, bukan deteksi). Baris yang ditolak tidak pernah menjadi event.

## 8. Provenance dan idempotensi

Dasar: FR-13, US-13, SEM-13, CE-04.

- Setiap event dapat ditelusuri: `source_id` + `processing_level` + `version_raw` → produk; `source_file` + `source_file_sha256` → file mentah di raw zone dan barisnya; `boundary_version` → snapshot batas; `ingest_run_id` → run log.
- **Field isi** (kelompok "isi" di §3; daftar `CONTENT_FIELDS` di `canonical_event.py`) ditentukan seluruhnya oleh baris sumber dan versi batas. **Field muat** (`LOAD_FIELDS`) menjelaskan pemuatan terakhir. Dalam mode incremental, deteksi NRT yang sama muncul di beberapa file poll (`DAY_RANGE` 2, poll tiap 15 menit), jadi field muat sah berubah antar-run.
- **Idempotensi yang diuji** (A-P5, harness run 2×): jumlah baris dan checksum atas field **isi** identik. Field muat dikecualikan dari checksum.

## 9. Aturan pemuatan

Mengikat pipeline (R1) dan writer (R2). Butir 1–5 dari 06 §B, butir 6 dari CE-03.

1. Upsert berdasarkan `detection_id`. Menulis ulang event yang sama tidak mengubah jumlah baris.
2. Agregat dihitung ulang sebagai nilai absolut. Tidak ada increment dan tidak ada counter table.
3. Batch hanya untuk partisi yang sama.
4. Rekaman yang ditolak tidak masuk tabel event, tetapi tercatat dengan reason code di run log/rejected store (A-P3-002).
5. Writer milik R2 (`db/`). Pipeline memanggil API writer, bukan menulis CQL sendiri.
6. Event `OUTSIDE` tidak dikirim ke writer dan tidak disimpan di Cassandra (CE-03, disetujui Lanang 2026-11-26). Jumlahnya per run dicatat di run log (FR-13, format di A-P3-002); barisnya tetap di raw zone (KEP-02) dan dapat dibentuk ulang kapan saja karena pipeline deterministik. Validasi bentuk event tetap berlaku untuk OUTSIDE.
7. Penggantian NRT→SP (*Should*, A-P7-003) menghapus semua event `(satellite, source_acq_date_utc)` produk NRT lalu memuat SP, kemudian menghitung ulang agregat untuk dua `local_date` yang terdampak. Ini operasi destruktif yang butuh persetujuan (HD-27); kontrak ini hanya menjamin field kuncinya tersedia.
8. Setiap event diperiksa terhadap skema dan aturan sebelum dikirim ke writer. Yang gagal ditolak dengan reason code (`CONTRACT_VIOLATION`, CE-08) dan tidak dikirim.

## 10. Versi dan perubahan

`contract_version` mengikuti semver ([06 §0](../../10-execution-plan/06-interface-contracts.md#0-register-kontrak)). Skema membawa versi yang sama di `x-contract-version`.

| Jenis | Contoh | Syarat |
|---|---|---|
| Patch (1.0.x) | Perbaikan teks/regex tanpa mengubah record yang valid | Pemilik |
| Minor (1.x.0) | Field opsional baru (mis. `regency_code`, kunci grid peta) | Pemilik + kabari konsumen |
| Major (x.0.0) | Mengubah/menghapus field, mengubah arti, mengubah rumus `detection_id` | **CR** ([10 §5](../../10-execution-plan/10-phase-gates.md#5-change-management)) + persetujuan semua konsumen |

Setelah G3, perubahan apa pun dilakukan lewat CR. Sebelum G3, konfirmasi CE-xx boleh mengubah draf ini langsung.

## 11. Sampel dan verifikasi

**Sampel** (`VERIFIED`, dibangun sesi ini dari raw zone Fase 1: 629 file, 2.705.905 baris). Builder membaca file berurutan, mengambil kandidat per bucket (produk × siang/malam × jam UTC malam × confidence × type × FRP 0 × TI4 jenuh × pita bujur), menetapkan wilayah dengan point-in-polygon, lalu memilih kandidat pertama yang memenuhi tiap kasus. Dua kasus jarang diambil dengan bantuan: MULTI_POLYGON (101 koordinat, lewat `coord_assign.csv` Fase 1) dan latitude dalam notasi ilmiah (22 baris). Membangun ulang menghasilkan file yang identik byte demi byte (diuji dengan `sha256sum`).

| # | Kasus | Produk | UTC | Tanggal lokal | Provinsi | `type` | conf | flag |
|---|---|---|---|---|---|---|---|---|
| 1 | INSIDE siang | N20 SP | 2023-01-01 05:08 | 2023-01-01 WITA | 63 Kalimantan Selatan | 0 | n | — |
| 2 | INSIDE malam, lintas tanggal | N20 SP | 2023-01-01 17:48 | **2023-01-02** WITA | 65 Kalimantan Utara | 0 | n | — |
| 3 | OUTSIDE | N20 SP | 2023-01-01 05:10 | — | — | 0 | n | — |
| 4 | INSIDE siang | N21 SP | 2023-03-01 03:43 | 2023-03-01 WIT | 93 Papua Selatan | 0 | n | — |
| 5 | INSIDE malam, lintas tanggal | N21 SP | 2023-03-01 16:26 | **2023-03-02** WIT | 82 Maluku Utara | 1 | n | NON_VEGETATION_TYPE |
| 6 | OUTSIDE | N21 SP | 2023-03-01 05:28 | — | — | 0 | n | — |
| 7 | INSIDE siang | N20 NRT | 2026-08-01 04:19 | 2026-08-01 WIT | 93 Papua Selatan | null | l | — |
| 8 | INSIDE malam, lintas tanggal | N20 NRT | 2026-08-01 15:26 | **2026-08-02** WIT | 93 Papua Selatan | null | n | — |
| 9 | OUTSIDE | N20 NRT | 2026-08-01 04:19 | — | — | null | n | — |
| 10 | INSIDE siang | N21 NRT | 2025-08-01 04:10 | 2025-08-01 WIT | 81 Maluku | null | n | — |
| 11 | INSIDE malam, lintas tanggal | N21 NRT | 2025-08-01 15:14 | **2025-08-02** WIT | 91 Papua | null | n | — |
| 12 | OUTSIDE | N21 NRT | 2025-08-01 04:10 | — | — | null | n | — |
| 13 | WIB malam, lintas tanggal | N20 NRT | 2026-08-01 17:05 | **2026-08-02** WIB | 62 Kalimantan Tengah | null | n | — |
| 14 | WITA malam, lintas tanggal | N20 NRT | 2026-08-01 17:05 | **2026-08-02** WITA | 53 Nusa Tenggara Timur | null | n | — |
| 15 | WIT malam, lintas tanggal | N20 NRT | 2026-08-01 15:26 | **2026-08-02** WIT | 93 Papua Selatan | null | n | — |
| 16 | WIB malam, tanggal tetap (16:54 UTC) | N20 NRT | 2026-08-07 16:54 | 2026-08-07 WIB | 35 Jawa Timur | null | n | — |
| 17 | WITA siang | N20 NRT | 2026-08-01 04:23 | 2026-08-01 WITA | 71 Sulawesi Utara | null | n | — |
| 18 | WIT siang | N20 NRT | 2026-08-01 04:19 | 2026-08-01 WIT | 93 Papua Selatan | null | l | — |
| 19 | type 1 (gunung api) | N20 SP | 2023-01-02 17:29 | **2023-01-03** WITA | 71 Sulawesi Utara | 1 | n | NON_VEGETATION_TYPE |
| 20 | type 2 (sumber statis darat) | N20 SP | 2023-01-01 17:50 | **2023-01-02** WITA | 63 Kalimantan Selatan | 2 | n | NON_VEGETATION_TYPE |
| 21 | type 3 (offshore) | N20 SP | 2023-01-01 05:10 | — (OUTSIDE) | — | 3 | n | NON_VEGETATION_TYPE |
| 22 | confidence h + TI4 367 K | N20 NRT | 2026-08-01 04:19 | — (OUTSIDE) | — | null | h | TI4_SATURATED |
| 23 | confidence l | N20 NRT | 2026-08-01 04:21 | 2026-08-01 WIT | 93 Papua Selatan | null | l | — |
| 24 | frp = 0 | N20 NRT | 2026-09-19 05:46 | 2026-09-19 WIB | 62 Kalimantan Tengah | null | l | FRP_ZERO, TI4_SATURATED |
| 25 | >1 poligon | N20 NRT | 2026-08-25 05:14 | 2026-08-25 WITA | 64 Kalimantan Timur | null | n | MULTI_POLYGON |
| 26 | latitude ditulis `-7e-05` (dekat ekuator) | N20 NRT | 2026-08-05 06:29 | 2026-08-05 WIB | 61 Kalimantan Barat | null | n | — |

File dan nomor baris sumber tiap sampel ada di `canonical-events.sample.cases.csv`. Satu-satunya nilai buatan adalah `ingest_run_id = sample-A-P3-001` (`ILUSTRASI`, CE-07).

Pengamatan dari sampel (`VERIFIED`, hanya contoh; bukan statistik): #24 menunjukkan baris dengan `frp = 0`, `bright_ti4` = 367 K, dan confidence `l` sekaligus, jadi flag bisa muncul bersamaan dan TI4 jenuh tidak selalu berarti `h`. Data dictionary hanya menyatakan arah sebaliknya: setiap `h` punya TI4 367 K.

**Verifikasi** (perintah dari root repo; `data/` ada di checkout utama karena tidak di-commit):

```
python -I docs/03-specs/data/samples/build_samples.py    --data-dir <repo>/data   # bangun ulang (deterministik)
python -I docs/03-specs/data/samples/validate_samples.py --data-dir <repo>/data   # semua cek; tanpa --data-dir: tanpa [trace]
python -I docs/03-specs/data/samples/audit_raw_zone.py   --data-dir <repo>/data   # audit semua baris raw zone (±9 menit)
```

| Cek | Isi | Hasil sesi ini |
|---|---|---|
| `[schema]` | Setiap record terhadap `canonical-event.schema.json` (validator subset 2020-12 berbasis stdlib; kata kunci yang tidak dikenal = error) | PASS 26/26 |
| `[rules]` | `detection_id` dihitung ulang, `source_acq_date_utc`, `local_tz` = zona provinsi, `local_date`, flag sesuai nilai, pemetaan `source_id`, `source_file` di direktori produk, nama provinsi = nama BIG, tanggal kalender nyata, angka berhingga | PASS 26/26 |
| `[coverage]` | ≥ 20; SP & NRT; N20 & N21; keempat `source_id`; OUTSIDE; lintas tanggal di WIB, WITA, WIT; `type` null dan 0–3; confidence l/n/h; keempat flag; ID unik | PASS |
| `[selftest]` | 34 record mutasi (NRT ber-`type`, `type` 4, INSIDE tanpa provinsi, nama provinsi salah, OUTSIDE ber-tanggal lokal, ID salah, zona salah, NaN/Infinity, tanggal 30 Februari, jam 24:00, path `..`, field tambahan/hilang, …) wajib ditolak; CE-09 (SP `type` null) wajib diterima; set ID tidak bergantung urutan | PASS |
| `[edge]` | 156 unit edge case pada input sintetis ([§11a](#11a-edge-case)) | PASS 156/156 |
| `[trace]` | Setiap record = hasil bangun ulang dari baris mentahnya; SHA-256 file = manifest = event; checksum snapshot batas; wilayah = `coord_assign.csv` Fase 1 (penetapan independen) | PASS |
| Silang | Library resmi `jsonschema` 4.26.0 (venv sementara, **bukan** dependensi proyek): `check_schema` lolos, 0 error pada 26 record, 6 mutasi ditolak | PASS |

Lint: `ruff check` dan `ruff format --check` (line length 120) bersih. Repo belum punya `ruff.toml`/pre-commit (dibuat di Fase 4). Skrip hanya memakai stdlib + numpy (sudah dipakai `scratch/phase1/`); tidak ada dependensi baru. Python ≥ 3.11.

## 11a. Edge case

Dua lapis pemeriksaan: **unit** (input sintetis, `validate_samples.py [edge]`) dan **data nyata** (semua baris raw zone, `audit_raw_zone.py`). Suite unit diuji dengan sabotase: delapan kerusakan sengaja pada fungsi referensi (offset WIB salah, tanpa normalisasi desimal, regex angka longgar, notasi ilmiah ditolak, `acq_time` longgar, flag kosong, ID tanpa `processing_level`, CE-09 dimatikan) semuanya terdeteksi.

### Aturan parsing (berlaku untuk pipeline A-P5)

| Input | Perlakuan | Reason code |
|---|---|---|
| `acq_time` 1–4 digit ASCII (`0` → 00:00, `5` → 00:05, `508` → 05:08) | Pad ke 4 digit | — |
| `acq_time` `2400`, `1260`, `12345`, `-5`, `5.0`, `+508`, digit non-ASCII, berspasi di tengah | Tolak | `INVALID_TIME` (DQ-05) |
| `acq_date` bukan `YYYY-MM-DD` atau bukan tanggal nyata (`2023-02-29`) | Tolak | `CONTRACT_VIOLATION` (CE-08) |
| Angka: desimal biasa **atau notasi ilmiah** (`-7e-05`) | Terima; ID memakai bentuk desimal kanonis | — |
| Angka: `NaN`, `Infinity`, `+1.5`, `1_000`, `1.`, `.5`, `1,5`, hex, kosong | Tolak | `NON_NUMERIC` (DQ-03) / `MISSING_FIELD` (DQ-02) |
| Angka yang meluap (`1e400`) | Tolak | `COORD_OUT_OF_RANGE` (koordinat) / `NON_NUMERIC` |
| `type` SP kosong | Terima, `type = null` | — (CE-09) |
| `type` ∉ {0,1,2,3}, `daynight` ∉ {D,N}, `instrument` ≠ VIIRS, `bright_ti4/ti5/scan/track` ≤ 0, `frp` < 0 | Tolak | `CONTRACT_VIOLATION` (CE-08) |
| Baris NRT yang punya kolom `type` | Tolak | `SCHEMA_MISMATCH` (DQ-01) |
| Spasi di awal/akhir nilai | Dibuang sebelum diproses | — |
| Nilai JSON `NaN`/`Infinity` | Ditolak pembaca JSONL dan tidak pernah ditulis (`allow_nan=False`) | — |
| `fetched_at_utc` tanpa offset zona | Tolak | `CONTRACT_VIOLATION` |

Batas tanggal lokal yang diuji: 16:59/17:00 UTC (WIB), 15:59/16:00 (WITA), 14:59/15:00 (WIT), pergantian tahun (2023-12-31 → 2024-01-01), hari kabisat (2024-02-28 → 02-29, 2024-02-29 → 03-01, 2023-02-28 → 03-01).

### Temuan pada data nyata (`VERIFIED`, `audit_raw_zone.py`, 2026-11-26, 517 detik)

| Pemeriksaan | Hasil |
|---|---|
| Semua 2.705.905 baris → event | **0 ditolak** (sesuai DQ-01…DQ-15 Fase 1) |
| Schema + rules (1 dari 10 baris, dipilih dari hash ID: 270.682 baris) | 0 gagal |
| **Notasi ilmiah di latitude** | **22 baris** (N20 NRT 9 · N20 SP 4 · N21 NRT 6 · N21 SP 3), mis. `-7e-05`, `1e-05`: titik dalam ±0,0001° dari ekuator. Data dictionary Fase 1 tidak mencatat bentuk ini. Parser yang hanya menerima desimal biasa akan salah menolaknya (terjadi pada draf parser ketat sesi ini, lalu diperbaiki). Sampel #26 |
| Duplikat `detection_id` per produk (DQ-08) | N20 SP 0 · N21 SP 1 · N20 NRT 1 · N21 NRT 0: **sama persis** dengan DQ-08 dan dengan kunci teks mentah A-08. Kedua pasangan adalah baris berurutan (`VIIRS_NOAA21_SP/2023-10-22_5d.csv:4061–4062`, `VIIRS_NOAA20_NRT/2026-08-26_5d.csv:6311–6312`) yang berbeda di `bright_ti4`, `bright_ti5`, `frp` → `DUPLICATE_CONFLICT`, diselesaikan pipeline (FRP tertinggi) |
| Tabrakan ID antar-produk | 0. Juga 0 bila ID dipotong ke 64 bit (alternatif CE-01(a) aman untuk volume ini) |
| `acq_time` | Hanya 3 digit (1.747.373, siang) dan 4 digit (958.532, malam). Bentuk 1–2 digit (00:00–00:59 UTC) tidak muncul di data, tetapi diuji di `[edge]` |
| Koordinat | Desimal 0–5; **tidak ada** teks dengan nol di belakang; 0 di luar bbox (DQ-04); 0 di luar jendela request (DQ-06) |
| Wilayah (sampel 1%: 26.972 baris) | INSIDE 23.510 · OUTSIDE 3.462 · MULTI_POLYGON 1; provinsi = `coord_assign.csv` Fase 1 untuk 26.957/26.957 koordinat |
| Pergeseran tanggal lokal (INSIDE) | Siang: selalu 0 hari. Malam: +1 hari (WIB 5.344, WITA 1.833, WIT 1.420) atau 0 hari (WIB 28, UTC < 17:00). Tidak pernah lebih dari 1 hari |
| Titik di >1 poligon (101 koordinat) | **94 di dua poligon kab/kota dalam provinsi yang sama; 7 di perbatasan dua provinsi** (mis. 92/96, 62/63, 73/74, 16/18, 33/35). Hanya 7 titik ini yang provinsinya bergantung pada aturan "poligon pertama" (SEM-02 butir 2) |

## 12. Selisih terhadap kerangka 06 §B

06 §B berlabel `PROPOSAL` dan menyatakan "final di A-P3-001". Selisih di bawah perlu diselaraskan koordinator di 06 saat X-P3-901 (cek konsistensi lintas kontrak). Agen ini tidak mengubah `docs/10-execution-plan/`.

| 06 §B | Kontrak ini | Alasan |
|---|---|---|
| `detection_id` = f(`satellite`, `acq_datetime_utc`, `latitude`, `longitude`) | + `processing_level` | CR-03 (disetujui G1) |
| `acq_date_local`, `local_tz` | `local_date`, `local_tz` | Nama SEM-00/SEM-03 (CE-02) |
| `region_status` ∈ {`PROVINCE`, `OUTSIDE`} | {`INSIDE`, `OUTSIDE`} | SEM-02 (CE-02) |
| — | `source_acq_date_utc` | Masukan 04 §4 (rekonsiliasi per tanggal UTC) |
| — | `dq_flags` | SEM-13 (flag DQ wajib dibawa) |
| — | `source_file` | FR-13 (file sumber dapat ditelusuri) |
| `confidence_raw`, `confidence_class` "tidak null" | Sama | — |
| `frp`, `bright_ti4`, … "tidak null" | Sama, + batas nilai di skema | — |

## 13. Masukan untuk tugas lain

| Penerima | Masukan |
|---|---|
| B-P3-001/002 (R2) | Konfirmasi tipe CQL §3. Dimensi query: `province_code`, `local_date`, `satellite`, `confidence_raw`, `type` (nullable). Operasi ganti/hapus per `(satellite, source_acq_date_utc, processing_level)` harus bisa tanpa scan. Pertimbangkan tabel file untuk field muat |
| B-P5-002 (R2) | Writer diuji dengan `canonical-events.sample.jsonl` yang sama (risiko tipe/null A↔B, [09](../../10-execution-plan/09-risk-capacity-plan.md)). Event OUTSIDE tidak dikirim (CE-03). Edge case Cassandra (`AI-PRIOR`, perlu diuji di B-P5-002): koleksi kosong (`set<text>` = `[]`) dibaca kembali sebagai `null`, jadi `dq_flags` harus dipetakan `null` ↔ `[]` saat membaca; `timestamp` beresolusi milidetik (aman, kontrak beresolusi detik); `double` menyimpan koordinat persis seperti nilai JSON |
| A-P3-002 (R1) | Format `ingest_run_id` (CE-07); pemilihan nilai DQ-08 antar-run; pengecualian field muat dari checksum idempotensi (CE-04) |
| A-P5-005 (R1) | Cocokkan zona per `province_code` (§6) dengan atribut BIG; uji tepat 38 kode |
| X-P3-901 (koordinator) | Selaraskan 06 §B dengan §12 |

## 14. Asumsi dan hal terbuka

| Item | Label |
|---|---|
| Zona per provinsi (§6) | `AI-PRIOR` (dari SEM-03), diverifikasi A-P5-005 |
| Satuan `scan`/`track` = km | `ASSUMPTION` (data dictionary) |
| FIRMS tidak mengubah format koordinat antar-file untuk deteksi yang sama; bila berubah, `canon` tetap menyamakan nol di belakang | `ASSUMPTION` (Fase 1: `changed` = 0 dalam 106 poll, [04 §3](../../01-dataset/04-nrt-vs-sp-and-latency.md#3-latensi-nrt-a-p1-008)) |
| Kunci spasial untuk peta (grid/geohash) | `PENDING`: menunggu B-P2-001/B-P3-001 |
| Lisensi batas BIG | `UNKNOWN` (HD-08), tidak memengaruhi bentuk kontrak |
| CE-01…CE-09 | Disetujui R1 (Lanang, 2026-11-26). CE-01, CE-03, CE-04: konfirmasi R2 bersama pemetaan CQL (§3) |
