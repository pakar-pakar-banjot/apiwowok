# 03 — Register Asumsi

Status: **DIPERBARUI 2026-11-19** setelah jawaban tim. Setiap asumsi harus divalidasi atau dibatalkan pada fase yang tercantum. Asumsi yang terbukti salah **tidak dihapus**: statusnya diubah dan dampaknya dicatat.

Kolom *Status*:
- `OPEN`: belum divalidasi.
- `VALIDATED`: terbukti/dikonfirmasi.
- `INVALIDATED`: terbukti salah; dampak dicatat.
- `WITHDRAWN`: tidak relevan lagi.

| ID | Asumsi | Label | Dampak jika salah | Cara validasi | Fase validasi | Status |
|---|---|---|---|---|---|---|
| A-01 | Apache Cassandra adalah teknologi wajib. | `USER` | — | Dikonfirmasi tim (OQ-01). | 0 | **VALIDATED** |
| A-02 | Tim terdiri dari 4 orang, sisa waktu 21 hari. | `USER` | — | Dikonfirmasi tim (OQ-02). | 0 | **VALIDATED** |
| A-03 | Ketersediaan tiap anggota 4 jam/hari (≈336 jam-orang sebagai batas atas). | `USER` | MVP perlu dipangkas bila kapasitas nyata lebih kecil. | Dipantau lewat standup harian. | Berkelanjutan | **VALIDATED** (sebagai asumsi perencanaan dari tim) |
| A-04 | ~~Aplikasi hanya dijalankan lokal; tidak perlu hosting.~~ | `ASSUMPTION` | **Dampak:** perlu workstream deployment cloud, desain keamanan minimum, dan konfigurasi lewat environment variable (OQ-23–OQ-27). | Jawaban tim (OQ-21): hosting diperlukan, lokal diprioritaskan lebih dulu. | 0 | **INVALIDATED** |
| A-05 | Data NASA FIRMS dapat diakses gratis; API memerlukan MAP_KEY. | `VERIFIED` (halaman resmi FIRMS API, dibaca 2026-11-19) | — | Hasil verifikasi: MAP_KEY gratis, dikirim via email; batas **5000 transaksi/10 menit**; Area API menerima bounding box, `DAY_RANGE` **1–5 hari**, dengan parameter `DATE` opsional; sumber `VIIRS_SNPP_SP/NRT`, `VIIRS_NOAA20_SP/NRT`, `VIIRS_NOAA21_SP/NRT`, `MODIS_SP/NRT`; endpoint `data_availability` tersedia. **Country API berstatus "currently not available".** Uji unduhan nyata tetap dilakukan di Fase 1. | 1 | **VALIDATED** (sebagian; uji unduhan di Fase 1) |
| A-06 | Field FIRMS mencakup latitude, longitude, tanggal & waktu akuisisi, satelit, instrumen, confidence, FRP, tetapi nama dan formatnya berbeda antar produk. | `USER` + `AI-PRIOR` | Data dictionary dan normalisasi berubah. | Inspeksi header dan sampel file nyata. | 1 | OPEN |
| A-07 | `acq_date` dan `acq_time` dalam UTC; `acq_time` berformat HHMM (mungkin tanpa nol di depan). | `AI-PRIOR` | Seluruh logika waktu dan agregasi harian salah. | Dokumentasi resmi FIRMS + cek sampel. | 1 | OPEN |
| A-08 | FIRMS tidak menyediakan ID unik per deteksi, sehingga deduplikasi membutuhkan natural key komposit. | `AI-PRIOR` | Jika ada ID, dedup jauh lebih sederhana. | Inspeksi kolom. | 1 | OPEN |
| A-09 | Data NRT kemudian digantikan versi arsip standar, dan keduanya dapat dibedakan dari field `version`. | `AI-PRIOR` | Kebijakan dedup NRT vs arsip berubah. | Bandingkan file NRT dan arsip untuk tanggal yang sama. | 1 | OPEN |
| A-10 | Volume deteksi VIIRS untuk Indonesia selama beberapa tahun dapat diproses Pandas di memori satu mesin dan disimpan di Cassandra single-node. | `ASSUMPTION` | Butuh pemrosesan per-chunk atau pemangkasan periode. | Hitung baris dan ukuran file nyata. | 1 | OPEN |
| A-11 | Ada sumber batas provinsi Indonesia (versi 38 provinsi) dengan lisensi yang memperbolehkan penggunaan akademik **dan publikasi di aplikasi yang di-hosting**. | `ASSUMPTION` | Pengayaan memakai versi lama dengan keterbatasan terdokumentasi. | Evaluasi kandidat sumber. | 1 | OPEN |
| A-12 | ~~Minimal satu laptop anggota mampu menjalankan cluster Cassandra 3 node.~~ | `ASSUMPTION` | Digantikan A-25. | Jawaban tim (OQ-15): spesifikasi laptop tidak relevan untuk pengembangan harian. | 0 | **WITHDRAWN** |
| A-13 | ~~Laptop anggota memakai Windows dengan Docker Desktop/WSL2.~~ | `ASSUMPTION` | — | Jawaban tim (OQ-15). Instruksi setup tetap perlu lintas-OS, tetapi tidak menjadi asumsi perencanaan. | 0 | **WITHDRAWN** |
| A-14 | Dashboard read-only; tidak membutuhkan autentikasi pengguna, termasuk saat di-hosting. | `ASSUMPTION` | Tambahan fitur keamanan. | Konfirmasi tim (Fase 2) bersama OQ-26. | 2 | OPEN |
| A-15 | Ingestion batch dengan checkpoint dan trigger manual sudah memenuhi syarat "incremental processing". | `ASSUMPTION` | Butuh penjadwal otomatis. | Konfirmasi tim (Fase 2). | 2 | OPEN |
| A-16 | ~~Penilaian lebih menekankan rekayasa data daripada estetika UI.~~ | `ASSUMPTION` | Diganti oleh A-23: tidak ada rubrik; prioritas tim adalah **produk jadi dan implementasi teknis**. Alokasi waktu frontend perlu setara dengan backend. | Jawaban tim (OQ-01). | 0 | **INVALIDATED** |
| A-17 | Dokumentasi berbahasa Indonesia; identifier kode, path API, dan konvensi teknis berbahasa Inggris. | `USER` | — | — | — | VALIDATED |
| A-18 | Tim memiliki akses ke Claude Code dan OpenAI Codex selama proyek. | `USER` | Pembagian kerja agen berubah. | — | — | OPEN |
| A-19 | Repositori awal kosong (hanya `README.md` kosong, 1 commit) dengan remote GitHub `pakar-pakar-banjot/apiwowok`. | `VERIFIED` (2026-11-19) | — | — | — | VALIDATED |
| A-20 | Satu versi batas wilayah yang tetap dipakai untuk seluruh periode historis. | `ASSUMPTION` | Jika memakai batas historis per tahun, pengayaan jauh lebih kompleks. | Diputuskan bersama OQ-07. | 1 | OPEN |
| A-21 | Tile peta dasar publik (mis. OpenStreetMap) boleh dipakai dengan atribusi. Untuk aplikasi yang di-hosting, kebijakan penggunaannya perlu dicek ulang. | `AI-PRIOR` | Ganti penyedia tile. | Cek kebijakan penggunaan tile. | 3 | OPEN |
| A-22 | **D1 = 2026-11-19, D21 = 2026-12-09** (dari jawaban "waktu tinggal 21 hari"). | `ASSUMPTION` | Jadwal di charter §10 bergeser. | Koreksi tim bila berbeda. | 0 | OPEN |
| A-23 | Prioritas proyek: produk jadi dan implementasi teknis. Laporan, presentasi, dan video ditangani tim; agen hanya menyediakan dokumentasi teknis pendukung. | `USER` | — | Jawaban tim (OQ-01, OQ-21). | 0 | VALIDATED |
| A-25 | Laptop dengan RAM 16 GB (≥8 GB untuk Docker/WSL2), 4 core, dan SSD ≥20 GB kosong mampu menjalankan cluster Cassandra 3 node dengan heap ±1 GB per node untuk eksperimen. | `ASSUMPTION` (tidak ada angka minimum dev di dokumentasi resmi) | Eksperimen pindah ke laptop lebih besar atau ke cloud. | Smoke test di [07-three-node-laptop-spec.md §4](07-three-node-laptop-spec.md#4-smoke-test-kelayakan-wajib-sebelum-eksperimen). | 4/7 | OPEN |
| A-24 | Arsitektur berbasis container dengan konfigurasi lewat environment variable dapat dipindahkan dari lokal ke cloud tanpa perubahan desain besar. | `ASSUMPTION` | Deployment memakan waktu lebih banyak dari perkiraan (R-23). | Desain di Fase 3/4; uji deploy pertama setelah D13. | 3–5 | OPEN |
