# 02 — Non-Functional Requirements Kuantitatif (C-P2-001)

> Fase 2 · Draf agen 2026-11-25 · Pemilik: R3 (Zita) · Status: **USULAN**, angka final = keputusan manusia di **G2** (HD-13).
> Label: [legenda](../00-discovery/README.md#label-status-informasi). `VERIFIED` hanya untuk angka yang diukur atau dikutip dari dokumen Fase 1; angka target tanpa pengukuran diberi `ASSUMPTION` atau `RECOMMENDATION` beserta alasannya. Tidak ada benchmark yang dijalankan untuk dokumen ini.
> Dasar terukur: [03-profiling-report](../01-dataset/03-profiling-report.md), [04-nrt-vs-sp-and-latency](../01-dataset/04-nrt-vs-sp-and-latency.md), [00-volume-estimates](../03-specs/database/00-volume-estimates.md), [06-interface-contracts](../10-execution-plan/06-interface-contracts.md) bagian C dan D, [07-three-node-laptop-spec](../00-discovery/07-three-node-laptop-spec.md).

## 1. Cara membaca

Setiap butir berformat: **NFR-xx** — target (angka) · metode ukur/verifikasi · dasar terukur · label · berlaku (`lokal` / `cloud` / `keduanya`).

Kolom **Berlaku**: `cloud` berarti NFR hanya bisa dan perlu diuji setelah deploy (OQ-21, Must setelah integrasi lokal D13). NFR `keduanya` diuji di lokal dan diulang di cloud.

## 2. Dasar terukur yang dipakai

| Fakta | Nilai | Sumber | Label |
|---|---|---|---|
| Total baris di dalam provinsi (dataset Fase 1) | 2.233.114 | profiling §8 | `VERIFIED` |
| Deteksi per provinsi-hari (hari yang ada deteksi) | p50 8 · p90 100 · p99 970 · maks 13.217 | profiling §8 | `VERIFIED` |
| Deteksi nasional per hari lokal | p50 358 · p90 3.764 · p99 17.381 · maks 24.507 | profiling §8 | `VERIFIED` |
| Deteksi per provinsi-bulan | p50 155 · p90 1.932 · p99 19.200 · maks 141.914 | profiling §8 | `VERIFIED` |
| Latensi NRT (sampel 2 hari) | 1,8 sampai ±9 jam; klaim resmi < 3 jam global | latency §3 | `VERIFIED` (periode pengamatan saja) |
| Batch NRT per satelit per hari untuk Indonesia | ±1–2 siang (03–07 UTC), 1 malam (15–19 UTC) | latency §3 | `VERIFIED` (2 hari) |
| Rekaman NRT berubah setelah terbit | 0 dari 106 poll | latency §3 | `VERIFIED` (±2 hari) |
| Kuota FIRMS | 5000 transaksi / 10 menit; ±8 transaksi per poll | STATUS §4, latency §3 | `VERIFIED` |
| Interval polling | 15 menit (keputusan R1, 2026-11-21) | STATUS §3 | `USER` |
| Byte per baris CSV mentah | 80–84 B | profiling §1 | `VERIFIED` |
| Byte per baris event di Cassandra | ±300–400 B | volume-estimates §3 | `ASSUMPTION` |
| Memori Cassandra | produksi minimal 2 core + 8 GB RAM per node; heap ≥ 2 GB; eksperimen 3 node di laptop memakai heap ±1 GB | 07-three-node-laptop-spec | dokumentasi resmi / `ASSUMPTION` |

## 3. Latensi API

Konteks: backend FastAPI membaca Cassandra lewat katalog query yang bounded (kontrak C), tanpa `ALLOW FILTERING`. Belum ada API atau skema, sehingga **semua target di bawah belum pernah diukur** dan berlabel `ASSUMPTION`/`RECOMMENDATION`. Angka diverifikasi ulang di C-P5 (uji beban) dan dikalibrasi dengan hasil nyata.

Kondisi ukur umum: dataset penuh (±2,2 juta baris, volume-estimates), satu klien, cache dingin dan hangat dilaporkan terpisah, 200 request berurutan per endpoint setelah 20 request pemanasan.

| ID | Endpoint | Target p95 | Target p99 | Metode ukur | Dasar | Label | Berlaku |
|---|---|---|---|---|---|---|---|
| NFR-01 | `/health`, `/ready` | ≤ 100 ms | ≤ 250 ms | Skrip uji menembak 200 request, laporkan persentil dari header waktu klien | Tidak menyentuh data besar (`/ready` hanya cek koneksi Cassandra) | `ASSUMPTION` | keduanya |
| NFR-02 | `/api/v1/meta`, `/api/v1/provinces/{code}` | ≤ 300 ms | ≤ 600 ms | Idem | Satu partisi atau data statis (38 provinsi) | `ASSUMPTION` | keduanya |
| NFR-03 | `/api/v1/summary`, `/timeline`, `/provinces/ranking` | ≤ 500 ms | ≤ 1.000 ms | Idem, pada rentang terlama (2023-01-01 sampai sekarang) | Dibaca dari agregat, bukan dari event (kontrak C: ranking dari 38 baris agregat). Bergantung keputusan B-P3-001 | `RECOMMENDATION` | keduanya |
| NFR-04 | `/api/v1/detections` (batas titik, lihat NFR-06) | ≤ 800 ms | ≤ 1.500 ms | Idem, pada kasus terburuk terukur: provinsi-hari dengan 13.217 deteksi (Kalimantan Tengah, 2026-10-22) | Maks terukur provinsi-hari = 13.217 (`VERIFIED`); waktu baca dan serialisasi `ASSUMPTION` | `RECOMMENDATION` | keduanya |
| NFR-05 | `/api/v1/pipeline/status` | ≤ 300 ms | ≤ 600 ms | Idem | Satu partisi (kontrak C) | `ASSUMPTION` | keduanya |

Catatan:
- Di cloud, latensi diukur **dari klien di luar server** dan dari dalam server; target di atas berlaku untuk waktu respons di server (header `X-Process-Time` atau log akses), dan jaringan dicatat terpisah (`ASSUMPTION`: tidak dijanjikan).
- Angka p95/p99 berlaku saat tidak ada backfill berjalan bersamaan. Saat backfill berjalan, target hanya dilaporkan, tidak ditegakkan (`RECOMMENDATION`).

## 4. Batas titik peta dan ukuran respons

| ID | Target | Metode ukur | Dasar | Label | Berlaku |
|---|---|---|---|---|---|
| NFR-06 | `/api/v1/detections`: `limit` default **2.000** titik, maksimum yang boleh diminta **5.000**. Respons selalu menyertakan `limit` dan `truncated`. Bila jumlah hasil melebihi `limit`, `truncated=true`, dan UI menampilkan notice. | Uji kontrak (pytest): minta provinsi-hari 13.217 deteksi, harapkan ≤ 5.000 fitur dan `truncated=true`; `limit` > 5.000 → 422 | p99 provinsi-hari = 970 (`VERIFIED`): satu hari penuh untuk 99% provinsi-hari muat dalam default tanpa terpotong. Rentang beberapa hari atau provinsi-hari ekstrem (maks 13.217) akan terpotong. Angka 2.000/5.000 sendiri `RECOMMENDATION` (kenyamanan render Leaflet belum diuji) | `RECOMMENDATION` | keduanya |
| NFR-07 | Ukuran payload `/api/v1/detections` pada batas maksimum (5.000 titik) ≤ **2 MB** tanpa kompresi, ≤ **600 KB** dengan gzip | Ukur `Content-Length` dan `Content-Encoding: gzip` pada respons 5.000 titik dari data nyata | Ukuran per fitur GeoJSON belum diukur; target `ASSUMPTION`, dikalibrasi ulang saat contoh respons canonical nyata ada (D-P4-002) | `ASSUMPTION` | keduanya |
| NFR-08 | **Rentang tanggal maksimum** `/detections`: 7 hari lokal per request; lebih dari itu → 422 | Uji kontrak | Peta dirancang per provinsi + rentang pendek (kontrak C; HD-21) | `RECOMMENDATION` | keduanya |
| NFR-09 | Setiap endpoint list bounded: `limit` + `truncated`; tidak ada endpoint yang membaca tanpa batas | Tinjau OpenAPI: setiap list punya `limit` maksimum; uji kontrak | Kontrak D "Bounded result" | `VERIFIED` (aturan kontrak) · angka batas tiap endpoint `RECOMMENDATION` | keduanya |

## 5. Kesegaran data dan polling

Berlaku untuk mode incremental (NRT micro-batch). Mode backfill (SP) tidak punya target kesegaran.

| ID | Target | Metode ukur | Dasar | Label | Berlaku |
|---|---|---|---|---|---|
| NFR-10 | **Interval polling 15 menit** untuk NOAA-20 dan NOAA-21 NRT (`DAY_RANGE` 2) | Periksa konfigurasi (`POLL_INTERVAL_SECONDS=900`) dan log poller: selisih antar-poll berurutan ≈ 900 s ± 60 s pada ≥ 95% poll dalam uji 24 jam | Keputusan R1 2026-11-21. Aman terhadap kuota: ±8 transaksi per poll → ±8 × (10/15) ≈ 5,3 transaksi per 10 menit dibanding 5.000 | `USER` (interval) · hitung kuota `VERIFIED` dari angka dokumen | keduanya |
| NFR-11 | **Tunda ingestion** (dari poll yang memuat batch sampai deteksi bisa dibaca API) ≤ **5 menit** per poll (batch tipikal ±100–300 deteksi) | Log poller: `ingest_finished_at − poll_started_at`, p95 dari uji 24 jam | Ukuran batch tipikal dari latency §3 (73–284 deteksi per batch, `VERIFIED`). Waktu tulis Cassandra belum diukur | `ASSUMPTION` | keduanya |
| NFR-12 | **Kesegaran maksimum yang dijanjikan = latensi sumber + ≤ 15 menit polling + ≤ 5 menit ingestion.** Latensi sumber "biasanya 2–3 jam, kadang hingga ±9 jam" tidak dijanjikan lebih rendah | Dokumentasi UI/laporan memuat kalimat itu; `/pipeline/status` mengembalikan `acq_datetime` terbaru per satelit | Latensi sumber terukur 1,8–±9 jam (sampel 2 hari, `VERIFIED` untuk periode itu, distribusi `UNKNOWN`) | `VERIFIED` (rentang pengamatan) · tidak ada klaim "real-time" | keduanya |
| NFR-13 | **Ambang data terlambat** per satelit, dari `acq_datetime` terbaru yang sudah dimuat: **peringatan** bila > **18 jam**, **basi** bila > **30 jam** | Uji otomatis: mock waktu server, harapkan status `ok`/`warning`/`stale` di `/pipeline/status`; UI menampilkan sesuai | Jeda ±12 jam antar-lintasan + latensi maks teramati ±9 jam (latency §3). Disarankan ditinjau ulang saat pipeline incremental berjalan (A-P5) | `RECOMMENDATION` | keduanya |
| NFR-14 | Setiap respons agregat menyertakan `data_updated_at` (UTC, ISO 8601 `Z`) | Uji kontrak | Kontrak D "Kesegaran" | `VERIFIED` (aturan kontrak) | keduanya |
| NFR-15 | **Idempotensi:** menjalankan ingest batch yang sama dua kali tidak menambah jumlah baris maupun mengubah nilai | Jalankan ingest dua kali pada sampel, bandingkan `count(*)` dan checksum nilai: selisih 0 | NRT tidak berubah setelah terbit (0 dari 106 poll, `VERIFIED` ±2 hari); aturan Cassandra STATUS §2 butir 5 | `VERIFIED` (aturan) | keduanya |

## 6. Ketersediaan dan restart poller

| ID | Target | Metode ukur | Dasar | Label | Berlaku |
|---|---|---|---|---|---|
| NFR-16 | Poller **restart otomatis** setelah crash (`restart: unless-stopped`) dan mulai polling kembali ≤ **2 menit** setelah container hidup | Uji: `docker kill` container poller; ukur waktu sampai log poll berikutnya | Poller berjalan terus (OQ-25 opsi C). Pengamatan Fase 1: proses terhenti oleh memori laptop dan laptop sleep, sehingga ada celah pengamatan (`VERIFIED`) | `RECOMMENDATION` | keduanya |
| NFR-17 | **Pemulihan celah (catch-up):** setelah poller mati hingga **48 jam**, poll pertama setelah pulih mengambil kembali semua deteksi yang terlewat tanpa duplikat | Uji: matikan poller (atau simulasikan dengan jam), jalankan ulang; bandingkan dengan sumber untuk jendela itu | `DAY_RANGE` FIRMS maksimum 5 hari (STATUS §4); poll normal memakai 2 hari. Untuk celah > 2 hari, poller memakai `DAY_RANGE` lebih besar sampai 5; celah > 5 hari ditangani backfill | `RECOMMENDATION` | keduanya |
| NFR-18 | Poller **tidak boleh menghentikan loop** karena satu kegagalan: error HTTP/jaringan dicatat, dicoba ulang di poll berikutnya; setelah **3 kegagalan berturut-turut** status pipeline = `degraded` | Uji dengan klien HTTP yang di-mock gagal | Praktik umum; belum diukur | `RECOMMENDATION` | keduanya |
| NFR-19 | **Ketersediaan API** selama jendela demo/penilaian: ≥ **99%** per 24 jam sebelum presentasi (≈ ≤ 14 menit gangguan) | Probe `/health` setiap 1 menit dari luar server selama 24 jam; hitung persentase sukses | Target proyek mahasiswa tanpa SLA; tidak ada dasar terukur | `ASSUMPTION` | cloud |

## 7. Keamanan

Keamanan adalah keputusan yang wajib disetujui manusia (STATUS §2 butir 4); butir di bawah adalah **usulan minimum** berdasarkan OQ-26.

| ID | Target | Metode ukur | Dasar | Label | Berlaku |
|---|---|---|---|---|---|
| NFR-20 | **Secret hanya lewat environment/secret store**: 0 secret (mis. `FIRMS_MAP_KEY`) di repo, image, atau log | Jalankan pemindai secret (mis. `gitleaks`) pada riwayat repo dan image: 0 temuan; `git ls-files` tidak memuat `.env`; `.env.example` hanya berisi nama variabel | OQ-26; AGENTS.md §4 | `RECOMMENDATION` | keduanya |
| NFR-21 | **Port Cassandra (9042, 7000, 7199) tidak dipublikasikan ke host/internet** pada konfigurasi cloud. Di lokal, port hanya terikat ke `127.0.0.1` bila perlu dibuka | `docker compose config` tidak memuat `ports:` untuk Cassandra di berkas produksi; pemindaian port dari luar server (mis. `nmap`) menunjukkan 9042 tertutup | OQ-26; kontrol minimum "Cassandra hanya di jaringan privat" | `RECOMMENDATION` | keduanya (uji pemindaian: cloud) |
| NFR-22 | **HTTPS** untuk semua akses publik; HTTP dialihkan ke HTTPS; sertifikat valid | `curl -I http://…` menghasilkan 301/308 ke https; `curl https://…` tanpa `-k` sukses | OQ-26; US-11 / FR-11 | `RECOMMENDATION` | cloud |
| NFR-23 | **CORS terbatas** ke domain frontend; origin lain tidak mendapat header `Access-Control-Allow-Origin` | `curl -H "Origin: https://evil.example" …` tidak mengembalikan header itu; `Origin` frontend mengembalikannya | OQ-26 | `RECOMMENDATION` | cloud |
| NFR-24 | **API read-only**: hanya `GET`; metode lain → 405. Akun Cassandra untuk API hanya punya `SELECT` | Uji kontrak: `POST/PUT/DELETE` ke setiap endpoint → 405; `LIST PERMISSIONS` menunjukkan hanya SELECT | OQ-26 ("API read-only") | `RECOMMENDATION` | keduanya (role DB: cloud) |
| NFR-25 | **Rate limit sederhana** (usulan: 60 request/menit per IP, `Should`) | Uji: 100 request dalam 1 menit dari satu IP → sebagian 429 | OQ-26 menyebut *Should*; angka 60 tanpa dasar terukur | `ASSUMPTION` (angka) | cloud |
| NFR-26 | **Pesan error tidak membocorkan detail internal** (stack trace, host DB, query). Semua 4xx/5xx memakai format `error{code,message,details,request_id}` | Uji kontrak: paksa error (Cassandra mati, parameter invalid), periksa isi | Kontrak D "Error" | `VERIFIED` (aturan kontrak) | keduanya |
| NFR-27 | Lisensi dan atribusi batas wilayah BIG ditampilkan sebelum hosting publik; **hosting publik tidak boleh aktif sebelum HD-08 (konfirmasi lisensi BIG) dijawab atau cadangan B5 dipakai** | Daftar periksa rilis (C-P7): bukti jawaban BIG atau keputusan B5 tercatat | STATUS §3 (OQ-07, HD-08); lisensi `UNKNOWN` | `VERIFIED` (status: `UNKNOWN`) | cloud |

## 8. Reproduksibilitas

| ID | Target | Metode ukur | Dasar | Label | Berlaku |
|---|---|---|---|---|---|
| NFR-28 | **Fresh clone → stack jalan** dengan ≤ **3 perintah** setelah menyalin `.env.example` ke `.env` (mis. `docker compose up -d`, perintah schema, perintah ingest sampel); semua terdokumentasi di README | Orang yang belum pernah mengerjakan repo (anggota tim lain) mengikuti README pada mesin bersih; catat jumlah perintah dan intervensi tambahan: 0 | US-14 / FR-14; O-E4 | `RECOMMENDATION` | keduanya |
| NFR-29 | **Waktu dari fresh clone sampai API merespons** `/ready` = 200 ≤ **10 menit** (tanpa backfill, di luar unduh image pertama) | Ukur dengan `time` pada mesin bersih; laporkan spesifikasi mesin | Cassandra membutuhkan waktu inisialisasi (Docker Hub note, 07-spec); belum diukur | `ASSUMPTION` | keduanya |
| NFR-30 | **Versi dikunci**: image Docker memakai tag versi eksplisit (tanpa `latest`); dependensi Python/Node di-lock | `grep -r ":latest"` pada Compose/Dockerfile → 0; berkas lock ada dan di-commit | Inventaris toolchain C-P1-001 (belum selesai: versi menunggu sumber resmi) | `RECOMMENDATION` | keduanya |
| NFR-31 | **Backfill dapat diulang**: menjalankan backfill dua kali pada sampel menghasilkan jumlah baris dan checksum yang identik | Sama dengan NFR-15 pada jalur backfill | Aturan idempotensi (STATUS §2 butir 5) | `VERIFIED` (aturan) | keduanya |
| NFR-32 | **Paritas lokal ↔ cloud**: konfigurasi lewat environment variable saja; berkas Compose yang sama dengan override cloud kecil | Diff berkas Compose dasar vs override: hanya variabel, port, dan sumber daya | OQ-23 ("netral terhadap penyedia"); ADR-002 (C-P3-001) | `RECOMMENDATION` | keduanya |
| NFR-33 | **Tes dan CI tidak memanggil API FIRMS** | Pindai kode tes: tidak ada URL `firms.modaps.eosdis.nasa.gov`; CI berjalan tanpa `FIRMS_MAP_KEY` | AGENTS.md §4 | `VERIFIED` (aturan) | keduanya |

## 9. Sumber daya

| ID | Target | Metode ukur | Dasar | Label | Berlaku |
|---|---|---|---|---|---|
| NFR-34 | **Single-node Cassandra untuk aplikasi** berjalan dengan heap ≥ 2 GB dan memori container ≤ **4 GB**; seluruh stack aplikasi (Cassandra, API, poller, frontend) ≤ **8 GB** RAM | `docker stats` pada kondisi stabil setelah memuat data penuh; laporkan maks | Panduan Cassandra: produksi minimal 2 core + 8 GB, heap ≥ 2 GB; laptop 8 GB hanya cukup single-node (07-spec). Angka 4/8 GB adalah batas anggaran, belum diukur | `ASSUMPTION` | keduanya |
| NFR-35 | **Cloud: VM** dengan ≥ **8 GB RAM**, 2 vCPU, ≥ **20 GB** disk untuk stack aplikasi single-node | Spesifikasi VM tercatat di ADR-003/004; `free -h`, `df -h` | Kebutuhan memori Cassandra; data: ±2,2 juta baris × ±300–400 B ≈ ±0,7–0,9 GB sebelum kompresi dan replikasi (`ASSUMPTION` byte per baris). Pilihan penyedia = HD-16 | `ASSUMPTION` | cloud |
| NFR-36 | **Poller** memakai ≤ **256 MB** RAM | `docker stats` selama uji 24 jam | Fase 1: poller yang dijalankan di laptop dihentikan karena memori laptop hampir habis (latency §3, `VERIFIED`); penyebab spesifik tidak diselidiki, sehingga angka 256 MB `ASSUMPTION` | `ASSUMPTION` | keduanya |

## 10. Ringkasan: yang hanya berlaku di cloud

NFR-19 (ketersediaan), NFR-22 (HTTPS), NFR-23 (CORS), NFR-25 (rate limit), NFR-27 (lisensi BIG sebelum publik), NFR-35 (spesifikasi VM). NFR-21 dan NFR-24 berlaku di keduanya, tetapi uji pemindaian port dan role database baru bermakna di cloud.

## 11. Keputusan yang dibutuhkan di G2 (HD-13)

Agen hanya mengusulkan. Manusia memutuskan:

| # | Keputusan | Usulan agen | Alasan |
|---|---|---|---|
| 1 | Target p95 per endpoint (NFR-01–05) | Seperti tabel §3 | Belum ada pengukuran; kalibrasi setelah API berjalan (C-P5) |
| 2 | Batas titik peta (NFR-06) | default 2.000, maks 5.000 | p99 provinsi-hari 970 muat di default; ekstrem 13.217 terpotong dengan notice |
| 3 | Rentang maks `/detections` (NFR-08) | 7 hari | Peta per provinsi + rentang pendek |
| 4 | Ambang data terlambat (NFR-13) | peringatan > 18 jam, basi > 30 jam | Latensi maks teramati ±9 jam + jeda ±12 jam antar-lintasan |
| 5 | Keamanan minimum (NFR-20–27) | Seperti §7 | OQ-26; keputusan keamanan wajib manusia |
| 6 | Rate limit (NFR-25) | `Should`, 60 req/menit/IP | Angka tanpa dasar terukur |

## 12. Keterbatasan dokumen ini

- Latensi sumber hanya dari pengamatan 2 hari; distribusi dan perbedaan antar satelit `UNKNOWN`.
- Volume maksimum didominasi musim 2026 (profiling §8); NFR batas titik memakai maksimum itu. Data SP periode itu baru tersedia ±5 bulan lagi.
- Byte per baris di Cassandra, waktu tulis/baca, dan ukuran payload GeoJSON **belum diukur**; angka terkait berlabel `ASSUMPTION` dan wajib dikalibrasi di B-P5-007 dan C-P5.
- Versi toolchain dan opsi cloud belum diinventarisasi (C-P1-001 belum selesai); NFR-30 dan NFR-35 bergantung padanya.
