# 02 — Work Breakdown Structure

> **File hasil generator** — jangan diedit manual. Sumber: `tools/build_plan.py`. Koordinator integrasi yang dipakai: Role B (R2) (HD-02, disetujui GATE-EP 2026-11-19). Kapasitas: HD-03 + HD-07(b).

Status: `RECOMMENDATION` — menunggu GATE-EP. Estimasi dalam **jam kerja manusia** (termasuk mengarahkan dan me-review agen). PERT = (O + 4M + P) / 6. Tanggal = hasil penjadwalan berkapasitas (05-project-schedule.md).

Kode peran: **A = R1** Data/ETL · **B = R2** Cassandra · **C = R3** Backend & DevOps · **D = R4** Frontend & Delivery. Tugas bernomor 9xx adalah tugas koordinasi (saat ini Role B).

Kolom yang sama untuk semua tugas dan tidak diulang di detail: *files allowed to modify* = area peran pemilik (07-file-ownership-matrix.md); *files must not modify* = area peran lain + `.env` + `docs/00-discovery/`; *Definition of Done* = DoD umum (10-phase-gates.md §3). Versi lengkap per tugas ada di CSV.

## P1 — Dataset Feasibility

| ID | Judul | Pemilik | Prio | O/M/P → PERT (j) | Dependensi | Rencana | Status |
|---|---|---|---|---|---|---|---|
| **A-P1-001** | Review inventaris sumber FIRMS | A (R1) | Must | 0.25/0.5/1 → 0.54 | — | D3–D3 | Draf selesai (agen) — menunggu review |
| **A-P1-002** ⚑ | Unduh sampel nyata + checksum | A (R1) | Must | 0.25/0.5/1 → 0.54 | — | D2–D2 | Unduhan selesai (agen) — menunggu verifikasi checksum |
| **A-P1-003** ⚑ | Data dictionary dari header & nilai nyata | A (R1) | Must | 0.5/1/1.5 → 1.0 | A-P1-002·H | D2–D2 | Belum mulai |
| **A-P1-004** ⚑ | Laporan profiling dataset | A (R1) | Must | 0.5/1/2 → 1.08 | A-P1-002·H, A-P1-006·S | D2–D2 | Belum mulai |
| **A-P1-005** ⚑ | Verifikasi asumsi AI-PRIOR A-06–A-09 | A (R1) | Must | 0.25/0.5/1 → 0.54 | A-P1-003·H | D3–D3 | Belum mulai |
| **A-P1-006** ⚑ | Review evaluasi sumber batas provinsi | A (R1) | Must | 0.25/0.5/1 → 0.54 | — | D2–D2 | Draf selesai (agen) — menunggu review |
| **A-P1-007** ⚑ | Perbandingan NRT vs SP + aturan tumpang tindih | A (R1) | Must | 0.5/1/1.5 → 1.0 | A-P1-002·H | D3–D3 | Belum mulai |
| **A-P1-008** | Pengamatan latensi NRT | A (R1) | Must | 0.25/0.5/1 → 0.54 | A-P1-002·S | D3–D3 | Berjalan (poller 24 jam) |
| **A-P1-009** ⚑ | Aturan kualitas data awal | A (R1) | Must | 0.5/1/2 → 1.08 | A-P1-004·H | D2–D3 | Belum mulai |
| **A-P1-010** ⚑ | Rekomendasi dataset + laporan Fase 1 (12 bagian) | A (R1) | Must | 0.5/1/1.5 → 1.0 | A-P1-004·H, A-P1-005·H, A-P1-007·H, A-P1-009·H, B-P1-001·S | D3–D3 | Belum mulai |
| **B-P1-001** | Estimasi volume per provinsi per hari/bulan | B (R2) | Must | 1.5/2/3 → 2.08 | A-P1-004·H | D2–D3 | Belum mulai |
| **C-P1-001** | Inventaris toolchain & opsi cloud (NA-07) | C (R3) | Must | 1.5/2/3 → 2.08 | — | D2–D2 | Belum mulai |
| **D-P1-001** | Draf user stories & FR dari charter | D (R4) | Must | 2/3/4 → 3.0 | — | D2–D2 | Belum mulai |
| **X-P1-901** | Tetapkan anggota↔peran, koordinator, ketersediaan; setujui rencana eksekusi | B (R2) | Must | 1/1.5/2 → 1.5 | — | D2–D2 | Belum mulai |
| **X-P1-902** ⚑ | Paket gerbang G1 + catat keputusan + perbarui STATUS | B (R2) | Must | 0.5/1/1.5 → 1.0 | A-P1-010·H | D3–D3 | Belum mulai |

⚑ = berada di rantai kritis.

### A-P1-001 — Review inventaris sumber FIRMS

- **Fase / prioritas / status:** P1 · Must · Draf selesai (agen) — menunggu review · ID lama P1-01
- **Tujuan:** Memastikan inventaris sumber, mekanisme akses, kuota, dan atribusi akurat.
- **Alasan:** Semua desain ekstraksi bergantung pada fakta akses FIRMS.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 0.25 / M 0.5 / P 1 → PERT 0.54 jam · **Rencana:** D3 (2026-11-21) – D3 (2026-11-21)
- **Input:** docs/01-dataset/01-source-inventory.md
- **Dependensi:** —
- **Output:** Inventaris sumber tervalidasi
- **File dimiliki:** `docs/01-dataset/01-source-inventory.md`
- **Langkah:** Baca draf → Cocokkan tiap klaim VERIFIED dengan sumber yang dirujuk → Catat koreksi di PR
- **Spesifikasi teknis:** Label status per klaim (legenda Fase 0)
- **Kriteria penerimaan:** Keempat source ID tercatat dengan rentang tanggal, biaya transaksi terukur, dan atribusi; tidak ada MAP_KEY di dokumen.
- **Verifikasi otomatis:** grep pola MAP_KEY (32 hex) di docs/ → 0 hasil
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G1
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P1-002 — Unduh sampel nyata + checksum

- **Fase / prioritas / status:** P1 · Must · Unduhan selesai (agen) — menunggu verifikasi checksum · ID lama P1-02
- **Tujuan:** Menyimpan respons mentah FIRMS untuk periode kandidat beserta checksum.
- **Alasan:** Raw zone membuat profiling dan ETL bisa diulang tanpa memanggil API (R-04, R-20).
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 0.25 / M 0.5 / P 1 → PERT 0.54 jam · **Rencana:** D2 (2026-11-20) – D2 (2026-11-20)
- **Input:** MAP_KEY di .env; rencana unduh di scratch/phase1/download.py
- **Dependensi:** —
- **Output:** data/firms/raw/**, data/firms/manifest.csv
- **File dimiliki:** `scratch/phase1/download.py, data/firms/`
- **Langkah:** Tunggu unduhan selesai → Hitung ulang SHA-256 dan cocokkan dengan manifest → Catat request gagal (harus 0)
- **Spesifikasi teknis:** Area API, bbox 94,-11.5,141.5,6.5, DAY_RANGE 5
- **Kriteria penerimaan:** Setiap file punya baris manifest dengan SHA-256 yang cocok; 0 request gagal; log tanpa MAP_KEY.
- **Verifikasi otomatis:** Skrip verifikasi checksum (sha256 ulang vs manifest)
- **Bukti test:** Output verifikasi checksum
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P1-003 — Data dictionary dari header & nilai nyata

- **Fase / prioritas / status:** P1 · Must · Belum mulai · ID lama P1-03
- **Tujuan:** Mendokumentasikan setiap kolom per sumber dari data nyata.
- **Alasan:** Kontrak canonical event (A-P3-001) diturunkan dari sini.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 0.5 / M 1 / P 1.5 → PERT 1.0 jam · **Rencana:** D2 (2026-11-20) – D2 (2026-11-20)
- **Input:** data/firms/raw/**; halaman atribut resmi FIRMS
- **Dependensi:** A-P1-002 (Hard)
- **Output:** docs/01-dataset/02-data-dictionary.md
- **File dimiliki:** `docs/01-dataset/02-data-dictionary.md`
- **Langkah:** Kumpulkan header per sumber → Isi tipe, contoh, rentang terukur, null, arti resmi + URL → Tandai perbedaan SP vs NRT dan N20 vs N21
- **Spesifikasi teknis:** Satu baris per kolom per sumber; label VERIFIED/UNKNOWN
- **Kriteria penerimaan:** Semua kolom di semua header tercakup; perbedaan `type` dan `version` antar produk tercatat dengan angka.
- **Verifikasi otomatis:** Skrip membandingkan daftar kolom dokumen vs header file → selisih 0
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G1
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P1-004 — Laporan profiling dataset

- **Fase / prioritas / status:** P1 · Must · Belum mulai · ID lama P1-04
- **Tujuan:** Mengukur baris, null, nilai di luar rentang, duplikat, cakupan temporal & geografis.
- **Alasan:** Aturan DQ, partisi, dan NFR membutuhkan angka nyata.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** B
- **Estimasi:** O 0.5 / M 1 / P 2 → PERT 1.08 jam · **Rencana:** D2 (2026-11-20) – D2 (2026-11-20)
- **Input:** data/firms/raw/**, coord_assign.csv
- **Dependensi:** A-P1-002 (Hard); A-P1-006 (Soft)
- **Output:** docs/01-dataset/03-profiling-report.md, data/firms/profile/*
- **File dimiliki:** `docs/01-dataset/03-profiling-report.md, scratch/phase1/profile_firms.py`
- **Langkah:** Jalankan pip_assign.py lalu profile_firms.py → Bandingkan hari kosong dengan tabel missing_data FIRMS → Tulis laporan dengan angka hasil ukur saja
- **Spesifikasi teknis:** Minimal 2 kandidat natural key untuk analisis duplikat
- **Kriteria penerimaan:** Setiap angka di laporan dapat ditelusuri ke file profil; hari kosong dijelaskan atau ditandai UNKNOWN.
- **Verifikasi otomatis:** Jalankan ulang skrip → hash profile.json identik (deterministik)
- **Bukti test:** Hash profile.json dua kali run
- **Persetujuan manusia:** G1
- **Serah-terima:** Serahkan 'docs/01-dataset/03-profiling-report.md, data/firms/profile/*' ke R2 untuk B-P1-001. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P1-005 — Verifikasi asumsi AI-PRIOR A-06–A-09

- **Fase / prioritas / status:** P1 · Must · Belum mulai · ID lama P1-05
- **Tujuan:** Menguji zona waktu acq_time, format confidence, field version dan type.
- **Alasan:** Asumsi salah merusak logika waktu dan dedup (R-03, R-07).
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 0.25 / M 0.5 / P 1 → PERT 0.54 jam · **Rencana:** D3 (2026-11-21) – D3 (2026-11-21)
- **Input:** Data dictionary, dokumentasi atribut FIRMS
- **Dependensi:** A-P1-003 (Hard)
- **Output:** Tabel verifikasi A-05–A-09 + usulan pembaruan register (sebagai CR)
- **File dimiliki:** `docs/01-dataset/02-data-dictionary.md (bagian verifikasi)`
- **Langkah:** Uji tiap asumsi dengan data → Kutip sumber resmi → Tulis usulan CR untuk register Fase 0
- **Spesifikasi teknis:** Register Fase 0 tidak diedit langsung
- **Kriteria penerimaan:** Setiap asumsi berstatus VALIDATED/INVALIDATED dengan bukti.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G1
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P1-006 — Review evaluasi sumber batas provinsi

- **Fase / prioritas / status:** P1 · Must · Draf selesai (agen) — menunggu review · ID lama P1-06
- **Tujuan:** Memvalidasi rekomendasi BIG edisi Juni 2026 (38 provinsi).
- **Alasan:** OQ-07; batas 34 provinsi merusak ranking Papua.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 0.25 / M 0.5 / P 1 → PERT 0.54 jam · **Rencana:** D2 (2026-11-20) – D2 (2026-11-20)
- **Input:** docs/01-dataset/05-boundary-sources.md
- **Dependensi:** —
- **Output:** Rekomendasi sumber batas tervalidasi
- **File dimiliki:** `docs/01-dataset/05-boundary-sources.md`
- **Langkah:** Cek jumlah provinsi dan edisi → Nilai risiko lisensi → Siapkan keputusan HD-08
- **Spesifikasi teknis:** Kriteria OQ-07
- **Kriteria penerimaan:** Rekomendasi menyatakan lisensi UNKNOWN secara eksplisit beserta cadangan.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G1 (OQ-07, HD-08)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P1-007 — Perbandingan NRT vs SP + aturan tumpang tindih

- **Fase / prioritas / status:** P1 · Must · Belum mulai · ID lama P1-09, P1-11
- **Tujuan:** Membandingkan NOAA-21 NRT vs SP pada tanggal yang sama dan mengusulkan aturan presedensi.
- **Alasan:** Kunci dedup lintas sumber (R-06, C-15).
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** B
- **Estimasi:** O 0.5 / M 1 / P 1.5 → PERT 1.0 jam · **Rencana:** D3 (2026-11-21) – D3 (2026-11-21)
- **Input:** data/firms/raw/VIIRS_NOAA21_*
- **Dependensi:** A-P1-002 (Hard)
- **Output:** docs/01-dataset/04-nrt-vs-sp-and-latency.md (bagian perbandingan)
- **File dimiliki:** `docs/01-dataset/04-nrt-vs-sp-and-latency.md, scratch/phase1/compare_nrt_sp.py`
- **Langkah:** Jalankan compare_nrt_sp.py → Ukur jarak posisi, selisih waktu, FRP, confidence → Usulkan aturan: SP menggantikan NRT per tanggal
- **Spesifikasi teknis:** Aturan pencocokan tertulis (toleransi waktu & jarak)
- **Kriteria penerimaan:** Proporsi match/unmatched dan sebaran selisih dilaporkan; aturan backfill diusulkan.
- **Verifikasi otomatis:** Skrip deterministik
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G1 (P1-09)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P1-008 — Pengamatan latensi NRT

- **Fase / prioritas / status:** P1 · Must · Berjalan (poller 24 jam) · ID lama P1-10
- **Tujuan:** Mengukur kapan data NRT muncul relatif terhadap acq_time dan apakah rekaman berubah.
- **Alasan:** Masukan interval polling (A-26, NFR).
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 0.25 / M 0.5 / P 1 → PERT 0.54 jam · **Rencana:** D3 (2026-11-21) – D3 (2026-11-21)
- **Input:** data/firms/latency/*
- **Dependensi:** A-P1-002 (Soft)
- **Output:** docs/01-dataset/04-nrt-vs-sp-and-latency.md (bagian latensi)
- **File dimiliki:** `scratch/phase1/latency_poller.py`
- **Langkah:** Analisis observations.csv → Hitung sebaran first_seen − acq_time → Rekomendasikan interval polling
- **Spesifikasi teknis:** Hasil sementara ditandai PENDING bila < 24 jam
- **Kriteria penerimaan:** Sebaran latensi dan jumlah rekaman berubah dilaporkan dengan periode pengamatan.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak (masukan G2)
- **Serah-terima:** Serahkan 'docs/01-dataset/04-nrt-vs-sp-and-latency.md (bagian latensi)' ke R3 untuk C-P2-001. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P1-009 — Aturan kualitas data awal

- **Fase / prioritas / status:** P1 · Must · Belum mulai · ID lama —
- **Tujuan:** Menetapkan aturan validasi, penolakan, dan penandaan berbasis profil nyata.
- **Alasan:** Kebijakan kualitas data wajib disetujui manusia.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 0.5 / M 1 / P 2 → PERT 1.08 jam · **Rencana:** D2 (2026-11-20) – D3 (2026-11-21)
- **Input:** Laporan profiling
- **Dependensi:** A-P1-004 (Hard)
- **Output:** docs/01-dataset/06-data-quality-rules.md
- **File dimiliki:** `docs/01-dataset/06-data-quality-rules.md`
- **Langkah:** Turunkan aturan DQ-xx dari temuan → Tentukan aksi: tolak / tandai / simpan → Kaitkan setiap aturan ke reason code
- **Spesifikasi teknis:** Tiap aturan: ID, kondisi, aksi, reason code, jumlah baris terdampak (terukur)
- **Kriteria penerimaan:** Setiap aturan punya angka dampak dari profil.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G1 (kebijakan DQ)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P1-010 — Rekomendasi dataset + laporan Fase 1 (12 bagian)

- **Fase / prioritas / status:** P1 · Must · Belum mulai
- **Tujuan:** Merangkum rekomendasi periode final, produk, batas, dan aturan.
- **Alasan:** Paket keputusan G1.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 0.5 / M 1 / P 1.5 → PERT 1.0 jam · **Rencana:** D3 (2026-11-21) – D3 (2026-11-21)
- **Input:** Semua dokumen 01-dataset
- **Dependensi:** A-P1-004 (Hard); A-P1-005 (Hard); A-P1-007 (Hard); A-P1-009 (Hard); B-P1-001 (Soft)
- **Output:** docs/01-dataset/07-dataset-recommendation.md, docs/01-dataset/README.md
- **File dimiliki:** `docs/01-dataset/README.md, docs/01-dataset/07-dataset-recommendation.md`
- **Langkah:** Tulis rekomendasi → Susun laporan 12 bagian → Daftar keputusan untuk G1
- **Spesifikasi teknis:** Format 12 bagian (00-discovery/README.md)
- **Kriteria penerimaan:** Semua keputusan G1 punya opsi + rekomendasi + bukti.
- **Verifikasi otomatis:** Cek tautan relatif
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G1
- **Serah-terima:** Serahkan 'docs/01-dataset/07-dataset-recommendation.md, docs/01-dataset/README.md' ke R2 untuk X-P1-902. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P1-001 — Estimasi volume per provinsi per hari/bulan

- **Fase / prioritas / status:** P1 · Must · Belum mulai · ID lama P1-07
- **Tujuan:** Mengukur baris per provinsi-hari dan provinsi-bulan (median, p99, maks).
- **Alasan:** Masukan ukuran partisi Fase 3 (R-05).
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D2 (2026-11-20) – D3 (2026-11-21)
- **Input:** data/firms/profile/prov_day.csv, prov_month.csv
- **Dependensi:** A-P1-004 (Hard)
- **Output:** docs/03-specs/database/00-volume-estimates.md
- **File dimiliki:** `docs/03-specs/database/00-volume-estimates.md`
- **Langkah:** Hitung distribusi baris per kandidat kunci partisi → Estimasi byte per baris dari ukuran CSV → Tandai provinsi/bulan puncak
- **Spesifikasi teknis:** Hanya angka hasil ukur; proyeksi ditandai ASSUMPTION
- **Kriteria penerimaan:** Tabel per kandidat partisi dengan p50/p99/maks baris dan perkiraan MB.
- **Verifikasi otomatis:** Skrip analisis dapat dijalankan ulang
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak (masukan G3)
- **Serah-terima:** Serahkan 'docs/03-specs/database/00-volume-estimates.md' ke R1, R3 untuk A-P1-010, C-P2-001. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P1-001 — Inventaris toolchain & opsi cloud (NA-07)

- **Fase / prioritas / status:** P1 · Must · Belum mulai
- **Tujuan:** Mendaftar versi Python/Node/Cassandra/driver yang kompatibel dan opsi cloud tim.
- **Alasan:** Masukan ADR stack (C-P3-001) dan OQ-23 sebelum D12.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D2 (2026-11-20) – D2 (2026-11-20)
- **Input:** Charter §8, OQ-23–OQ-27, dokumen 07
- **Dependensi:** —
- **Output:** docs/03-specs/architecture/00-toolchain-and-cloud-options.md
- **File dimiliki:** `docs/03-specs/architecture/00-toolchain-and-cloud-options.md`
- **Langkah:** Cek kompatibilitas versi dari dokumentasi resmi → Kumpulkan opsi cloud/kredit dari anggota → Bandingkan biaya & memori minimum Cassandra
- **Spesifikasi teknis:** Setiap versi diberi sumber resmi + tanggal baca
- **Kriteria penerimaan:** Matriks versi terverifikasi + ≥2 opsi cloud dengan biaya/batas.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak (masukan HD-16)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P1-001 — Draf user stories & FR dari charter

- **Fase / prioritas / status:** P1 · Must · Belum mulai · ID lama P1-08
- **Tujuan:** Menulis draf user story dan FR untuk 12 fitur MoSCoW.
- **Alasan:** Memulai Fase 2 paralel agar G2 tidak terlambat (R-02).
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D2 (2026-11-20) – D2 (2026-11-20)
- **Input:** Charter §4–§7
- **Dependensi:** —
- **Output:** docs/02-requirements/00-draft-user-stories.md
- **File dimiliki:** `docs/02-requirements/00-draft-user-stories.md`
- **Langkah:** Satu story per fitur Must/Should → Kaitkan ke persona OQ-19 → Tandai hal yang menunggu data Fase 1
- **Spesifikasi teknis:** Format: Sebagai <persona>, saya ingin …, agar …
- **Kriteria penerimaan:** Setiap fitur Must punya ≥1 story.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak (masukan G2)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### X-P1-901 — Tetapkan anggota↔peran, koordinator, ketersediaan; setujui rencana eksekusi

- **Fase / prioritas / status:** P1 · Must · Belum mulai
- **Tujuan:** Mengisi HD-01–HD-06 dan menyetujui docs/10-execution-plan/.
- **Alasan:** Tanpa pemilik nyata, tugas tidak bisa mulai.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 1 / M 1.5 / P 2 → PERT 1.5 jam · **Rencana:** D2 (2026-11-20) – D2 (2026-11-20)
- **Input:** docs/10-execution-plan/
- **Dependensi:** —
- **Output:** 12-human-decision-register.md terisi; catatan persetujuan
- **File dimiliki:** `docs/10-execution-plan/12-human-decision-register.md`
- **Langkah:** Rapat/obrolan tim 30–45 menit → Isi matriks skill di 01-role-charters.md → Catat keputusan
- **Spesifikasi teknis:** Mekanisme persetujuan HD-05
- **Kriteria penerimaan:** HD-01–HD-06 berstatus DECIDED.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tim (GATE-EP)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Manusia (agen hanya mencatat)

### X-P1-902 — Paket gerbang G1 + catat keputusan + perbarui STATUS

- **Fase / prioritas / status:** P1 · Must · Belum mulai
- **Tujuan:** Mengumpulkan keputusan G1 dan memperbarui docs/STATUS.md.
- **Alasan:** Fase 2/3 butuh keputusan dataset final.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 0.5 / M 1 / P 1.5 → PERT 1.0 jam · **Rencana:** D3 (2026-11-21) – D3 (2026-11-21)
- **Input:** Laporan Fase 1
- **Dependensi:** A-P1-010 (Hard)
- **Output:** Keputusan G1 tercatat; STATUS.md diperbarui
- **File dimiliki:** `docs/STATUS.md`
- **Langkah:** Bagikan paket → Kumpulkan persetujuan → Perbarui STATUS + register lewat CR
- **Spesifikasi teknis:** Checklist G1 (10-phase-gates)
- **Kriteria penerimaan:** Setiap butir checklist G1 berstatus disetujui/ditolak.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tim (G1)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Manusia + agen pencatat

## P2 — Requirements Engineering

| ID | Judul | Pemilik | Prio | O/M/P → PERT (j) | Dependensi | Rencana | Status |
|---|---|---|---|---|---|---|---|
| **D-P2-001** | Functional requirements final | D (R4) | Must | 2.5/3.5/5 → 3.58 | D-P1-001·H, GATE-G1·S | D2–D3 | Belum mulai |
| **D-P2-002** | Acceptance criteria per FR | D (R4) | Must | 2/3/4 → 3.0 | D-P2-001·H | D3–D4 | Belum mulai |
| **C-P2-001** | Non-functional requirements kuantitatif | C (R3) | Must | 2/3/4 → 3.0 | B-P1-001·H, A-P1-008·S | D3–D3 | Belum mulai |
| **A-P2-001** ⚑ | Semantik data & aturan perhitungan | A (R1) | Must | 2/3/4 → 3.0 | GATE-G1·HA | D4–D4 | Belum mulai |
| **B-P2-001** | Kebutuhan query aplikasi (Q-xx) | B (R2) | Must | 2/3/4 → 3.0 | D-P2-001·H, A-P2-001·S | D3–D4 | Belum mulai |
| **D-P2-003** | Kunci MVP + urutan pemotongan cakupan | D (R4) | Must | 1/1.5/2.5 → 1.58 | D-P2-002·H, C-P2-001·H, B-P2-001·S | D6–D6 | Belum mulai |
| **X-P2-901** ⚑ | Paket gerbang G2 | B (R2) | Must | 0.5/1/1.5 → 1.0 | D-P2-003·H, A-P2-001·H, B-P2-001·H | D7–D7 | Belum mulai |

⚑ = berada di rantai kritis.

### D-P2-001 — Functional requirements final

- **Fase / prioritas / status:** P2 · Must · Belum mulai
- **Tujuan:** Menulis FR bernomor untuk fitur Must/Should dengan data Fase 1.
- **Alasan:** Dasar query requirements dan UI spec.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 2.5 / M 3.5 / P 5 → PERT 3.58 jam · **Rencana:** D2 (2026-11-20) – D3 (2026-11-21)
- **Input:** Draf story, keputusan G1
- **Dependensi:** D-P1-001 (Hard); GATE-G1 (Soft)
- **Output:** docs/02-requirements/01-functional-requirements.md
- **File dimiliki:** `docs/02-requirements/01-functional-requirements.md`
- **Langkah:** Ubah story menjadi FR-xx → Kaitkan ke fitur #1–#12 → Tandai MoSCoW
- **Spesifikasi teknis:** FR-xx: pernyataan, persona, prioritas, sumber
- **Kriteria penerimaan:** Setiap fitur Must ↔ ≥1 FR; tidak ada FR tanpa fitur.
- **Verifikasi otomatis:** Matriks traceability fitur↔FR lengkap
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G2
- **Serah-terima:** Serahkan 'docs/02-requirements/01-functional-requirements.md' ke R2 untuk B-P2-001. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P2-002 — Acceptance criteria per FR

- **Fase / prioritas / status:** P2 · Must · Belum mulai
- **Tujuan:** Menulis kriteria Given/When/Then yang dapat diuji.
- **Alasan:** Dipakai test API/UI dan checklist G8.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D3 (2026-11-21) – D4 (2026-11-22)
- **Input:** FR
- **Dependensi:** D-P2-001 (Hard)
- **Output:** Bagian AC di 01-functional-requirements.md
- **File dimiliki:** `docs/02-requirements/01-functional-requirements.md`
- **Langkah:** ≥1 AC per FR → Sertakan kasus kosong/error → Tandai AC yang butuh data nyata
- **Spesifikasi teknis:** Given/When/Then
- **Kriteria penerimaan:** Setiap FR Must punya AC terukur.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G2
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P2-001 — Non-functional requirements kuantitatif

- **Fase / prioritas / status:** P2 · Must · Belum mulai
- **Tujuan:** Menetapkan target latensi API, batas titik peta, kesegaran data, interval polling, keamanan, reproduksibilitas.
- **Alasan:** Charter menunda target angka ke Fase 2.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** A, B
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D3 (2026-11-21) – D3 (2026-11-21)
- **Input:** Volume terukur, latensi NRT
- **Dependensi:** B-P1-001 (Hard); A-P1-008 (Soft)
- **Output:** docs/02-requirements/02-non-functional-requirements.md
- **File dimiliki:** `docs/02-requirements/02-non-functional-requirements.md`
- **Langkah:** Usulkan angka dengan dasar terukur → Tentukan cara ukur tiap NFR → Tandai yang hanya berlaku di cloud
- **Spesifikasi teknis:** NFR-xx: target, metode ukur, alasan
- **Kriteria penerimaan:** Setiap NFR punya angka dan metode verifikasi.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G2
- **Serah-terima:** Serahkan 'docs/02-requirements/02-non-functional-requirements.md' ke R4 untuk D-P2-003. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P2-001 — Semantik data & aturan perhitungan

- **Fase / prioritas / status:** P2 · Must · Belum mulai
- **Tujuan:** Menetapkan definisi 'jumlah deteksi': tanggal lokal, default confidence, titik luar provinsi, sumber statis, presedensi SP/NRT, penggabungan satelit.
- **Alasan:** Mencegah agregat yang salah tafsir (R-15) dan perbedaan antar lapisan.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D4 (2026-11-22) – D4 (2026-11-22)
- **Input:** Keputusan G1, OQ-08–OQ-12
- **Dependensi:** GATE-G1 (Human approval)
- **Output:** docs/03-specs/data/01-data-semantics.md
- **File dimiliki:** `docs/03-specs/data/01-data-semantics.md`
- **Langkah:** Tulis aturan SEM-xx → Beri contoh numerik → Tandai keputusan yang butuh persetujuan
- **Spesifikasi teknis:** Mengikuti OQ-08–OQ-12
- **Kriteria penerimaan:** Setiap angka di dashboard dapat dijelaskan oleh satu aturan SEM-xx.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G2 (kebijakan data)
- **Serah-terima:** Serahkan 'docs/03-specs/data/01-data-semantics.md' ke R2 untuk B-P2-001, X-P2-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P2-001 — Kebutuhan query aplikasi (Q-xx)

- **Fase / prioritas / status:** P2 · Must · Belum mulai
- **Tujuan:** Menerjemahkan setiap FR menjadi kebutuhan query: parameter, filter, urutan, kardinalitas, ukuran hasil.
- **Alasan:** Input access patterns; mencegah desain relasional (R-09).
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** C, D
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D3 (2026-11-21) – D4 (2026-11-22)
- **Input:** FR, semantik data, volume
- **Dependensi:** D-P2-001 (Hard); A-P2-001 (Soft)
- **Output:** docs/03-specs/database/01-query-requirements.md
- **File dimiliki:** `docs/03-specs/database/01-query-requirements.md`
- **Langkah:** Satu Q-xx per kebutuhan baca → Estimasi baris hasil dari volume → Tandai query yang butuh pra-agregasi
- **Spesifikasi teknis:** Q-xx ↔ FR-xx
- **Kriteria penerimaan:** Setiap FR yang membaca data ↔ ≥1 Q-xx.
- **Verifikasi otomatis:** Matriks FR↔Q lengkap
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G2
- **Serah-terima:** Serahkan 'docs/03-specs/database/01-query-requirements.md' ke R4 untuk D-P2-003. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P2-003 — Kunci MVP + urutan pemotongan cakupan

- **Fase / prioritas / status:** P2 · Must · Belum mulai
- **Tujuan:** Mengunci daftar Must final dan urutan fitur yang dipotong bila terlambat.
- **Alasan:** Mitigasi scope creep (R-01).
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 1 / M 1.5 / P 2.5 → PERT 1.58 jam · **Rencana:** D6 (2026-11-24) – D6 (2026-11-24)
- **Input:** FR, NFR, Q
- **Dependensi:** D-P2-002 (Hard); C-P2-001 (Hard); B-P2-001 (Soft)
- **Output:** docs/02-requirements/03-mvp-lock.md
- **File dimiliki:** `docs/02-requirements/03-mvp-lock.md`
- **Langkah:** Tulis daftar Must final → Tulis urutan descoping → Ajukan ke G2
- **Spesifikasi teknis:** Charter §6
- **Kriteria penerimaan:** Daftar descoping berurutan disetujui tim.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G2 (ruang lingkup)
- **Serah-terima:** Serahkan 'docs/02-requirements/03-mvp-lock.md' ke R2 untuk X-P2-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### X-P2-901 — Paket gerbang G2

- **Fase / prioritas / status:** P2 · Must · Belum mulai
- **Tujuan:** Mengumpulkan persetujuan G2.
- **Alasan:** Fase 3 tidak boleh mulai tanpa requirements.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 0.5 / M 1 / P 1.5 → PERT 1.0 jam · **Rencana:** D7 (2026-11-25) – D7 (2026-11-25)
- **Input:** Dokumen Fase 2
- **Dependensi:** D-P2-003 (Hard); A-P2-001 (Hard); B-P2-001 (Hard)
- **Output:** Keputusan G2; STATUS.md
- **File dimiliki:** `docs/STATUS.md`
- **Langkah:** Bagikan paket → Catat keputusan
- **Spesifikasi teknis:** Checklist G2
- **Kriteria penerimaan:** Checklist G2 lengkap.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tim (G2)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Manusia + agen pencatat

## P3 — Architecture & Technical Specs

| ID | Judul | Pemilik | Prio | O/M/P → PERT (j) | Dependensi | Rencana | Status |
|---|---|---|---|---|---|---|---|
| **B-P3-001** | Access pattern matrix | B (R2) | Must | 2/3/4 → 3.0 | B-P2-001·H | D4–D5 | Belum mulai |
| **A-P3-001** ⚑ | Kontrak canonical event v1 + sampel record | A (R1) | Must | 2/3/5 → 3.17 | A-P1-003·H, A-P2-001·S | D4–D5 | Belum mulai |
| **A-P3-002** | Spesifikasi ETL (dua mode) | A (R1) | Must | 3/4/5.5 → 4.08 | A-P3-001·S, A-P1-009·H | D5–D6 | Belum mulai |
| **B-P3-002** ⚑ | Model data logis & fisik + spesifikasi CQL | B (R2) | Must | 2.5/3.5/5 → 3.58 | B-P3-001·H, A-P3-001·I | D5–D6 | Belum mulai |
| **B-P3-003** ⚑ | Strategi read model/agregat & rebuild | B (R2) | Must | 1/2/3 → 2.0 | B-P3-002·H | D7–D7 | Belum mulai |
| **C-P3-001** | Arsitektur end-to-end + ADR stack | C (R3) | Must | 2/3/4 → 3.0 | C-P1-001·S, C-P2-001·S | D4–D5 | Belum mulai |
| **D-P3-001** | Spesifikasi UI + wireframe low-fi | D (R4) | Must | 3/4/6 → 4.17 | D-P2-001·H, D-P2-002·S | D4–D5 | Belum mulai |
| **C-P3-002** | Kontrak API v1 (OpenAPI) | C (R3) | Must | 3/4/6 → 4.17 | B-P3-001·I, D-P3-001·S, C-P2-001·H | D5–D6 | Belum mulai |
| **C-P3-003** | ADR deployment & keamanan (OQ-24–OQ-26) | C (R3) | Must | 1.5/2/3 → 2.08 | C-P3-001·H | D9–D9 | Belum mulai |
| **B-P3-004** | Rencana eksperimen Cassandra | B (R2) | Must | 1.5/2/3 → 2.08 | B-P3-002·S | D9–D9 | Belum mulai |
| **X-P3-901** ⚑ | Paket G3 + cek konsistensi lintas kontrak | B (R2) | Must | 1/2/3 → 2.0 | GATE-G2·HA, A-P3-001·H, A-P3-002·H, B-P3-002·H, B-P3-003·H, C-P3-001·H, C-P3-002·H, D-P3-001·H, B-P3-004·S, C-P3-003·S | D8–D8 | Belum mulai |

⚑ = berada di rantai kritis.

### B-P3-001 — Access pattern matrix

- **Fase / prioritas / status:** P3 · Must · Belum mulai
- **Tujuan:** Memetakan Q-xx ke tabel, kunci partisi, kunci clustering, dan estimasi ukuran partisi.
- **Alasan:** Skema hanya boleh mengikuti access pattern yang disetujui.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** A
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D4 (2026-11-22) – D5 (2026-11-23)
- **Input:** Q-xx, volume
- **Dependensi:** B-P2-001 (Hard)
- **Output:** docs/03-specs/database/02-access-patterns.md
- **File dimiliki:** `docs/03-specs/database/02-access-patterns.md`
- **Langkah:** Satu baris per Q-xx → Pilih partisi + bucketing bila perlu → Hitung ukuran partisi p99 dari volume
- **Spesifikasi teknis:** Tanpa ALLOW FILTERING/scan penuh
- **Kriteria penerimaan:** Setiap Q-xx terpetakan ke tepat satu tabel/query; ukuran partisi p99 di bawah batas yang ditetapkan.
- **Verifikasi otomatis:** Review silang C (konsumen)
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G3
- **Serah-terima:** Serahkan 'docs/03-specs/database/02-access-patterns.md' ke R3 untuk C-P3-002. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P3-001 — Kontrak canonical event v1 + sampel record

- **Fase / prioritas / status:** P3 · Must · Belum mulai
- **Tujuan:** Mendefinisikan field, tipe, nullability, identitas dedup, ID spasial, konvensi waktu, provenance.
- **Alasan:** Antarmuka ETL→Cassandra (kontrak B di 06).
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** B
- **Estimasi:** O 2 / M 3 / P 5 → PERT 3.17 jam · **Rencana:** D4 (2026-11-22) – D5 (2026-11-23)
- **Input:** Data dictionary, semantik data
- **Dependensi:** A-P1-003 (Hard); A-P2-001 (Soft)
- **Output:** docs/03-specs/data/02-canonical-event-contract.md, docs/03-specs/data/samples/canonical-events.sample.jsonl
- **File dimiliki:** `docs/03-specs/data/02-canonical-event-contract.md, docs/03-specs/data/samples/`
- **Langkah:** Tabel field → Definisikan detection_id deterministik → Hasilkan ≥20 contoh dari data nyata (termasuk luar provinsi & malam lintas tanggal)
- **Spesifikasi teknis:** Versi kontrak semver; perubahan lewat CR
- **Kriteria penerimaan:** B mengonfirmasi tiap field dapat dipetakan ke CQL; contoh lolos validasi skema JSON.
- **Verifikasi otomatis:** Validasi sampel terhadap JSON Schema
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G3 (kontrak antarmuka)
- **Serah-terima:** Serahkan 'docs/03-specs/data/02-canonical-event-contract.md, docs/03-specs/data/samples/canonical-events.sample.jsonl' ke R2 untuk B-P3-002, X-P3-901, B-P5-002. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P3-002 — Spesifikasi ETL (dua mode)

- **Fase / prioritas / status:** P3 · Must · Belum mulai
- **Tujuan:** Menentukan tahap, mode backfill & incremental, checkpoint, run log, rejected records, semantik re-run, penjaga kuota.
- **Alasan:** Dasar implementasi Fase 5.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 3 / M 4 / P 5.5 → PERT 4.08 jam · **Rencana:** D5 (2026-11-23) – D6 (2026-11-24)
- **Input:** Aturan DQ, kontrak canonical
- **Dependensi:** A-P3-001 (Soft); A-P1-009 (Hard)
- **Output:** docs/03-specs/data/03-etl-spec.md
- **File dimiliki:** `docs/03-specs/data/03-etl-spec.md`
- **Langkah:** Diagram tahap → Definisikan checkpoint per mode → Definisikan reason code & run log
- **Spesifikasi teknis:** Source adapter (OQ-28)
- **Kriteria penerimaan:** Setiap tahap punya input/output/kegagalan; idempotensi didefinisikan secara terukur.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G3
- **Serah-terima:** Serahkan 'docs/03-specs/data/03-etl-spec.md' ke R2 untuk X-P3-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P3-002 — Model data logis & fisik + spesifikasi CQL

- **Fase / prioritas / status:** P3 · Must · Belum mulai
- **Tujuan:** Menulis tabel, tipe, kunci, TTL (bila ada), dan file CQL spesifikasi (belum dieksekusi).
- **Alasan:** Kontrak Cassandra→backend.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** C
- **Estimasi:** O 2.5 / M 3.5 / P 5 → PERT 3.58 jam · **Rencana:** D5 (2026-11-23) – D6 (2026-11-24)
- **Input:** Access patterns, kontrak canonical, volume
- **Dependensi:** B-P3-001 (Hard); A-P3-001 (Interface)
- **Output:** docs/03-specs/database/03-data-model.md, docs/03-specs/database/schema-v1.cql
- **File dimiliki:** `docs/03-specs/database/`
- **Langkah:** Logical model → Physical model + bucketing → CQL draft + contoh query per Q-xx
- **Spesifikasi teknis:** Tanpa counter table untuk agregat
- **Kriteria penerimaan:** Setiap tabel ↔ ≥1 Q-xx; CQL valid secara sintaks (cqlsh di container dev).
- **Verifikasi otomatis:** Parse CQL di Cassandra dev (setelah B-P4-001)
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G3 (skema)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P3-003 — Strategi read model/agregat & rebuild

- **Fase / prioritas / status:** P3 · Must · Belum mulai
- **Tujuan:** Mendefinisikan cara agregat dihitung ulang secara absolut per partisi dan prosedur rebuild.
- **Alasan:** Mencegah agregat ganda (R-10).
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 1 / M 2 / P 3 → PERT 2.0 jam · **Rencana:** D7 (2026-11-25) – D7 (2026-11-25)
- **Input:** Model data
- **Dependensi:** B-P3-002 (Hard)
- **Output:** docs/03-specs/database/04-aggregates.md
- **File dimiliki:** `docs/03-specs/database/04-aggregates.md`
- **Langkah:** Pilih granularitas agregat → Definisikan pemicu hitung ulang → Definisikan rebuild penuh
- **Spesifikasi teknis:** Nilai absolut, bukan increment
- **Kriteria penerimaan:** Re-run input yang sama menghasilkan agregat identik (dapat diuji).
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G3
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P3-001 — Arsitektur end-to-end + ADR stack

- **Fase / prioritas / status:** P3 · Must · Belum mulai
- **Tujuan:** Menulis arsitektur, diagram aliran data, dan ADR versi stack serta paritas lokal↔cloud.
- **Alasan:** Semua peran butuh gambaran komponen yang sama.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D4 (2026-11-22) – D5 (2026-11-23)
- **Input:** Charter, NFR, inventaris toolchain
- **Dependensi:** C-P1-001 (Soft); C-P2-001 (Soft)
- **Output:** docs/03-specs/architecture/01-architecture.md, docs/03-specs/architecture/adr/ADR-001..002
- **File dimiliki:** `docs/03-specs/architecture/`
- **Langkah:** Diagram komponen & aliran → ADR-001 versi stack → ADR-002 paritas lokal/cloud
- **Spesifikasi teknis:** Format ADR: konteks, keputusan, konsekuensi
- **Kriteria penerimaan:** Setiap komponen punya pemilik dan antarmuka tertaut ke 06-interface-contracts.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G3 (arsitektur)
- **Serah-terima:** Serahkan 'docs/03-specs/architecture/01-architecture.md, docs/03-specs/architecture/adr/ADR-001..002' ke R2 untuk X-P3-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P3-001 — Spesifikasi UI + wireframe low-fi

- **Fase / prioritas / status:** P3 · Must · Belum mulai
- **Tujuan:** Inventaris halaman, wireframe, perilaku filter, drill-down, state loading/empty/error, indikator kesegaran, disclaimer.
- **Alasan:** Masukan kontrak API dan dasar implementasi UI.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 3 / M 4 / P 6 → PERT 4.17 jam · **Rencana:** D4 (2026-11-22) – D5 (2026-11-23)
- **Input:** FR + AC
- **Dependensi:** D-P2-001 (Hard); D-P2-002 (Soft)
- **Output:** docs/03-specs/ui/01-ui-spec.md, docs/03-specs/ui/wireframes/
- **File dimiliki:** `docs/03-specs/ui/`
- **Langkah:** Inventaris halaman → Wireframe tiap halaman → Tabel interaksi → kebutuhan data
- **Spesifikasi teknis:** Bahasa UI Indonesia (OQ-20)
- **Kriteria penerimaan:** Setiap elemen data di wireframe ↔ field API yang diminta.
- **Verifikasi otomatis:** Review silang C
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G3 (perilaku UI)
- **Serah-terima:** Serahkan 'docs/03-specs/ui/01-ui-spec.md, docs/03-specs/ui/wireframes/' ke R2, R3 untuk C-P3-002, X-P3-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P3-002 — Kontrak API v1 (OpenAPI)

- **Fase / prioritas / status:** P3 · Must · Belum mulai
- **Tujuan:** Menulis openapi.yaml: endpoint, parameter, skema respons, skema error, contoh, batas jumlah titik.
- **Alasan:** Memungkinkan backend & frontend paralel dengan mock.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** B
- **Estimasi:** O 3 / M 4 / P 6 → PERT 4.17 jam · **Rencana:** D5 (2026-11-23) – D6 (2026-11-24)
- **Input:** Access patterns, UI spec, NFR
- **Dependensi:** B-P3-001 (Interface); D-P3-001 (Soft); C-P2-001 (Hard)
- **Output:** docs/03-specs/api/openapi.yaml, docs/03-specs/api/01-api-notes.md
- **File dimiliki:** `docs/03-specs/api/`
- **Langkah:** Endpoint per kebutuhan UI → Contoh respons dari sampel canonical → Skema error seragam
- **Spesifikasi teknis:** OpenAPI 3.1; path bahasa Inggris
- **Kriteria penerimaan:** openapi.yaml valid; setiap endpoint ↔ Q-xx; D menyetujui cakupan kebutuhan UI.
- **Verifikasi otomatis:** Validator OpenAPI (CLI) → 0 error
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G3 (kontrak antarmuka)
- **Serah-terima:** Serahkan 'docs/03-specs/api/openapi.yaml, docs/03-specs/api/01-api-notes.md' ke R2, R4 untuk X-P3-901, D-P4-002. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P3-003 — ADR deployment & keamanan (OQ-24–OQ-26)

- **Fase / prioritas / status:** P3 · Must · Belum mulai
- **Tujuan:** Mengusulkan cara Cassandra & poller berjalan di cloud dan kontrol keamanan minimum, netral penyedia.
- **Alasan:** Cloud Must setelah D13; keputusan penyedia ≤ D12.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D9 (2026-11-27) – D9 (2026-11-27)
- **Input:** Opsi cloud, NFR
- **Dependensi:** C-P3-001 (Hard)
- **Output:** docs/03-specs/architecture/adr/ADR-003-deployment.md, ADR-004-security.md
- **File dimiliki:** `docs/03-specs/architecture/adr/`
- **Langkah:** Opsi + rekomendasi per OQ → Kontrol keamanan minimum → Kriteria pemilihan penyedia
- **Spesifikasi teknis:** R-23, R-25
- **Kriteria penerimaan:** Setiap kontrol keamanan punya cara verifikasi.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G3 + persetujuan keamanan (HD-16)
- **Serah-terima:** Serahkan 'docs/03-specs/architecture/adr/ADR-003-deployment.md, ADR-004-security.md' ke R2 untuk X-P3-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P3-004 — Rencana eksperimen Cassandra

- **Fase / prioritas / status:** P3 · Must · Belum mulai
- **Tujuan:** Hipotesis, variabel, metrik, protokol, lingkungan untuk eksperimen bucketing (Must) dan replikasi (Should).
- **Alasan:** O-E3; mencegah benchmark tidak valid (R-16).
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D9 (2026-11-27) – D9 (2026-11-27)
- **Input:** Model data, dokumen 07
- **Dependensi:** B-P3-002 (Soft)
- **Output:** docs/03-specs/database/05-experiment-plan.md
- **File dimiliki:** `docs/03-specs/database/05-experiment-plan.md`
- **Langkah:** Hipotesis terukur → Protokol warm-up & repetisi → Lingkungan & versi dicatat
- **Spesifikasi teknis:** Tidak ada hasil sebelum dijalankan
- **Kriteria penerimaan:** Rencana dapat dijalankan orang lain tanpa bertanya.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G3
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### X-P3-901 — Paket G3 + cek konsistensi lintas kontrak

- **Fase / prioritas / status:** P3 · Must · Belum mulai
- **Tujuan:** Memastikan nama field, tipe, dan semantik konsisten dari canonical → CQL → OpenAPI → UI.
- **Alasan:** Kesalahan integrasi paling murah dicegah di sini.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 1 / M 2 / P 3 → PERT 2.0 jam · **Rencana:** D8 (2026-11-26) – D8 (2026-11-26)
- **Input:** Semua spesifikasi Fase 3
- **Dependensi:** GATE-G2 (Human approval); A-P3-001 (Hard); A-P3-002 (Hard); B-P3-002 (Hard); B-P3-003 (Hard); C-P3-001 (Hard); C-P3-002 (Hard); D-P3-001 (Hard); B-P3-004 (Soft); C-P3-003 (Soft)
- **Output:** Laporan konsistensi + keputusan G3
- **File dimiliki:** `docs/03-specs/README.md, docs/STATUS.md`
- **Langkah:** Tabel jejak field lintas lapisan → Catat ketidakcocokan sebagai CR → Kumpulkan persetujuan
- **Spesifikasi teknis:** 06-interface-contracts.md
- **Kriteria penerimaan:** 0 ketidakcocokan terbuka saat G3 disetujui.
- **Verifikasi otomatis:** Skrip cek nama field openapi vs CQL vs canonical (opsional)
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tim (G3)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Agen menyusun, manusia memutuskan

## P4 — Development Harness

| ID | Judul | Pemilik | Prio | O/M/P → PERT (j) | Dependensi | Rencana | Status |
|---|---|---|---|---|---|---|---|
| **C-P4-001** | Kerangka repo + CODEOWNERS + template PR | C (R3) | Must | 2/2.5/3.5 → 2.58 | GATE-EP·HA | D3–D4 | Belum mulai |
| **D-P4-003** | AGENTS.md & CLAUDE.md lengkap | D (R4) | Must | 2/3/4 → 3.0 | GATE-EP·HA | D6–D7 | Belum mulai |
| **A-P4-002** | Tooling Python bersama (lint, format, test, pre-commit) | A (R1) | Must | 1.5/2/3 → 2.08 | C-P4-001·H | D6–D7 | Belum mulai |
| **C-P4-004** | Docker Compose dasar + validasi environment | C (R3) | Must | 2/3/4 → 3.0 | C-P4-001·H, B-P4-001·I | D7–D7 | Belum mulai |
| **C-P4-005** | CI: lint + unit test per komponen | C (R3) | Must | 1.5/2/3 → 2.08 | A-P4-002·H, D-P4-001·S | D7–D8 | Belum mulai |
| **B-P4-001** ⚑ | Konfigurasi Cassandra single-node untuk dev | B (R2) | Must | 1.5/2.5/4 → 2.58 | GATE-EP·HA | D6–D7 | Belum mulai |
| **B-P4-002** | Smoke test 3 node di laptop (dokumen 07 §4) | B (R2) | Should | 2/3/4 → 3.0 | B-P4-001·H | D20–D21 | Belum mulai |
| **A-P4-001** | Skeleton paket pipeline + fixtures uji dari data nyata | A (R1) | Must | 1.5/2/3 → 2.08 | C-P4-001·H, A-P1-004·S | D7–D7 | Belum mulai |
| **D-P4-001** | Scaffold React + Leaflet + lint/test | D (R4) | Must | 1.5/2.5/4 → 2.58 | C-P4-001·H | D5–D6 | Belum mulai |
| **D-P4-002** | Mock API dari contoh OpenAPI | D (R4) | Must | 1.5/2/3 → 2.08 | C-P3-002·I, D-P4-001·H | D7–D7 | Belum mulai |
| **X-P4-901** | Paket G4: uji fresh clone | B (R2) | Must | 0.5/1/1.5 → 1.0 | D-P4-003·H, C-P4-004·H, C-P4-005·H, B-P4-001·H, A-P4-001·H, D-P4-001·H | D8–D8 | Belum mulai |

⚑ = berada di rantai kritis.

### C-P4-001 — Kerangka repo + CODEOWNERS + template PR

- **Fase / prioritas / status:** P4 · Must · Belum mulai
- **Tujuan:** Membuat struktur direktori sesuai 07-file-ownership-matrix, CODEOWNERS, dan template PR.
- **Alasan:** Kepemilikan file ditegakkan oleh alat, bukan ingatan.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 2.5 / P 3.5 → PERT 2.58 jam · **Rencana:** D3 (2026-11-21) – D4 (2026-11-22)
- **Input:** 07-file-ownership-matrix.md
- **Dependensi:** GATE-EP (Human approval)
- **Output:** Direktori kosong ber-README, .github/CODEOWNERS, .github/pull_request_template.md
- **File dimiliki:** `.github/, README.md`
- **Langkah:** Buat direktori → CODEOWNERS per direktori → Template PR dengan checklist DoD
- **Spesifikasi teknis:** 07-file-ownership-matrix
- **Kriteria penerimaan:** CODEOWNERS mencakup semua direktori di matriks.
- **Verifikasi otomatis:** Skrip cek setiap direktori di matriks ada di CODEOWNERS
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G4
- **Serah-terima:** Serahkan 'Direktori kosong ber-README, .github/CODEOWNERS, .github/pull_request_template.md' ke R1, R4 untuk A-P4-002, A-P4-001, D-P4-001. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P4-003 — AGENTS.md & CLAUDE.md lengkap

- **Fase / prioritas / status:** P4 · Must · Belum mulai
- **Tujuan:** Menulis coding standards, git workflow, DoD, protokol Claude Code/Codex, aturan worktree.
- **Alasan:** OQ-18; mencegah konflik agen (R-13).
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** A, B, C
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D6 (2026-11-24) – D7 (2026-11-25)
- **Input:** Dokumen 07, 08, 11 di rencana ini
- **Dependensi:** GATE-EP (Human approval)
- **Output:** AGENTS.md, CLAUDE.md
- **File dimiliki:** `AGENTS.md, CLAUDE.md`
- **Langkah:** Gabungkan aturan minimum saat ini → Tambah standar per bahasa → Tambah protokol agen & stop conditions
- **Spesifikasi teknis:** Tidak mengubah keputusan Fase 0
- **Kriteria penerimaan:** Setiap prompt peran di 11-role-prompts konsisten dengan AGENTS.md.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G4
- **Serah-terima:** Serahkan 'AGENTS.md, CLAUDE.md' ke R2 untuk X-P4-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P4-002 — Tooling Python bersama (lint, format, test, pre-commit)

- **Fase / prioritas / status:** P4 · Must · Belum mulai
- **Tujuan:** Mengunci versi Python dan konfigurasi ruff/pytest/pre-commit.
- **Alasan:** Lingkungan heterogen (R-12).
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D6 (2026-11-24) – D7 (2026-11-25)
- **Input:** ADR-001 (draf)
- **Dependensi:** C-P4-001 (Hard)
- **Output:** ruff.toml, .pre-commit-config.yaml, panduan venv
- **File dimiliki:** `ruff.toml, .pre-commit-config.yaml`
- **Langkah:** Pilih versi → Konfigurasi lint/format → Hook pre-commit: lint, deteksi secret
- **Spesifikasi teknis:** Tanpa alat yang tidak perlu
- **Kriteria penerimaan:** `pre-commit run --all-files` lulus di repo bersih.
- **Verifikasi otomatis:** pre-commit run --all-files
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G4
- **Serah-terima:** Serahkan 'ruff.toml, .pre-commit-config.yaml, panduan venv' ke R3 untuk C-P4-005. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P4-004 — Docker Compose dasar + validasi environment

- **Fase / prioritas / status:** P4 · Must · Belum mulai
- **Tujuan:** Compose dengan service cassandra (fragmen B), api placeholder, web dev; healthcheck; .env.example; skrip cek env.
- **Alasan:** Kriteria keberhasilan #1.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D7 (2026-11-25) – D7 (2026-11-25)
- **Input:** Fragmen konfigurasi Cassandra dari B
- **Dependensi:** C-P4-001 (Hard); B-P4-001 (Interface)
- **Output:** docker-compose.yml, .env.example, deploy/scripts/check_env.*
- **File dimiliki:** `docker-compose.yml, .env.example, deploy/`
- **Langkah:** Service + healthcheck → Variabel env terdokumentasi → Skrip cek env tanpa mencetak nilai secret
- **Spesifikasi teknis:** Konfigurasi lewat env (A-24)
- **Kriteria penerimaan:** `docker compose up` → semua service healthy di mesin bersih.
- **Verifikasi otomatis:** docker compose ps (healthy) di CI atau mesin anggota
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G4
- **Serah-terima:** Serahkan 'docker-compose.yml, .env.example, deploy/scripts/check_env.*' ke R2 untuk X-P4-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P4-005 — CI: lint + unit test per komponen

- **Fase / prioritas / status:** P4 · Must · Belum mulai
- **Tujuan:** Pipeline CI tanpa secret yang menjalankan lint dan unit test.
- **Alasan:** Gerbang mutu otomatis sebelum merge.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D7 (2026-11-25) – D8 (2026-11-26)
- **Input:** Tooling Python & web
- **Dependensi:** A-P4-002 (Hard); D-P4-001 (Soft)
- **Output:** .github/workflows/ci.yml
- **File dimiliki:** `.github/workflows/`
- **Langkah:** Job per komponen dengan path filter → Cache dependensi → Wajibkan status hijau sebelum merge
- **Spesifikasi teknis:** HD-15 (pemakaian GitHub Actions)
- **Kriteria penerimaan:** PR contoh menunjukkan CI hijau; CI gagal bila test gagal.
- **Verifikasi otomatis:** PR uji dengan test gagal sengaja
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G4
- **Serah-terima:** Serahkan '.github/workflows/ci.yml' ke R2 untuk X-P4-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P4-001 — Konfigurasi Cassandra single-node untuk dev

- **Fase / prioritas / status:** P4 · Must · Belum mulai
- **Tujuan:** Image versi terkunci, heap terbatas, healthcheck, skrip tunggu-siap, keyspace dev (tanpa skema produksi).
- **Alasan:** Dasar semua pekerjaan DB.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2.5 / P 4 → PERT 2.58 jam · **Rencana:** D6 (2026-11-24) – D7 (2026-11-25)
- **Input:** ADR-001 (draf), dokumen 07
- **Dependensi:** GATE-EP (Human approval)
- **Output:** db/docker/, db/scripts/, db/README.md
- **File dimiliki:** `db/`
- **Langkah:** Pilih versi (ADR) → Fragmen Compose untuk C → Skrip readiness
- **Spesifikasi teknis:** Heap ±1 GB
- **Kriteria penerimaan:** Cassandra siap < N menit dan lolos `cqlsh -e 'describe keyspaces'`.
- **Verifikasi otomatis:** Skrip readiness exit 0
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'db/docker/, db/scripts/, db/README.md' ke R3 untuk C-P4-004. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P4-002 — Smoke test 3 node di laptop (dokumen 07 §4)

- **Fase / prioritas / status:** P4 · Should · Belum mulai
- **Tujuan:** Membuktikan laptop memenuhi spesifikasi 3 node untuk eksperimen replikasi.
- **Alasan:** Validasi A-25 sebelum B-P7-003.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D20 (2026-12-08) – D21 (2026-12-09)
- **Input:** Dokumen 07
- **Dependensi:** B-P4-001 (Hard)
- **Output:** experiments/env-3node/SMOKE.md
- **File dimiliki:** `experiments/env-3node/`
- **Langkah:** Jalankan 3 node → nodetool status → Catat hardware & waktu
- **Spesifikasi teknis:** Dokumen 07 §4
- **Kriteria penerimaan:** 3 node UN atau laporan kegagalan dengan bukti.
- **Verifikasi otomatis:** Output nodetool status
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P4-001 — Skeleton paket pipeline + fixtures uji dari data nyata

- **Fase / prioritas / status:** P4 · Must · Belum mulai
- **Tujuan:** pyproject, struktur modul, dan fixtures kecil (CSV nyata + golden output).
- **Alasan:** Test deterministik tanpa memanggil API.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D7 (2026-11-25) – D7 (2026-11-25)
- **Input:** Data mentah Fase 1
- **Dependensi:** C-P4-001 (Hard); A-P1-004 (Soft)
- **Output:** pipeline/pyproject.toml, pipeline/src/, pipeline/tests/fixtures/
- **File dimiliki:** `pipeline/`
- **Langkah:** Struktur modul per tahap ETL → Pilih subset fixtures (≤1 MB) mencakup kasus tepi → Test contoh lulus
- **Spesifikasi teknis:** Fixtures data FIRMS publik + atribusi
- **Kriteria penerimaan:** `pytest pipeline` lulus; fixtures mencakup malam lintas tanggal, luar provinsi, NRT & SP.
- **Verifikasi otomatis:** pytest pipeline
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'pipeline/pyproject.toml, pipeline/src/, pipeline/tests/fixtures/' ke R2 untuk X-P4-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P4-001 — Scaffold React + Leaflet + lint/test

- **Fase / prioritas / status:** P4 · Must · Belum mulai
- **Tujuan:** Proyek web (Vite), lint/format, test runner, peta dasar statis dengan atribusi.
- **Alasan:** Frontend dapat mulai tanpa backend.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2.5 / P 4 → PERT 2.58 jam · **Rencana:** D5 (2026-11-23) – D6 (2026-11-24)
- **Input:** ADR-001 (draf), HD-14
- **Dependensi:** C-P4-001 (Hard)
- **Output:** web/
- **File dimiliki:** `web/`
- **Langkah:** Scaffold → Lint & test runner → Halaman peta dasar
- **Spesifikasi teknis:** HD-14 (TypeScript, library chart)
- **Kriteria penerimaan:** `npm run lint && npm test && npm run build` lulus.
- **Verifikasi otomatis:** Perintah tersebut di CI
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'web/' ke R2, R3 untuk C-P4-005, X-P4-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P4-002 — Mock API dari contoh OpenAPI

- **Fase / prioritas / status:** P4 · Must · Belum mulai
- **Tujuan:** Mock layer (mis. MSW) yang mengembalikan contoh openapi.yaml + toggle mock/real.
- **Alasan:** Frontend paralel dengan backend (OQ-27 opsi A).
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D7 (2026-11-25) – D7 (2026-11-25)
- **Input:** openapi.yaml v1
- **Dependensi:** C-P3-002 (Interface); D-P4-001 (Hard)
- **Output:** web/src/mocks/
- **File dimiliki:** `web/src/mocks/`
- **Langkah:** Muat contoh dari openapi.yaml → Handler per endpoint → Flag env untuk mock/real
- **Spesifikasi teknis:** Tidak menambah field di luar kontrak
- **Kriteria penerimaan:** Setiap endpoint di kontrak punya handler; flag mematikan mock.
- **Verifikasi otomatis:** Test: respons mock lolos validasi skema OpenAPI
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### X-P4-901 — Paket G4: uji fresh clone

- **Fase / prioritas / status:** P4 · Must · Belum mulai
- **Tujuan:** Anggota yang bukan pemilik harness meng-clone ulang dan menjalankan semua cek.
- **Alasan:** Bukti reproduksibilitas sejak awal (O-E4).
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 0.5 / M 1 / P 1.5 → PERT 1.0 jam · **Rencana:** D8 (2026-11-26) – D8 (2026-11-26)
- **Input:** Repo
- **Dependensi:** D-P4-003 (Hard); C-P4-004 (Hard); C-P4-005 (Hard); B-P4-001 (Hard); A-P4-001 (Hard); D-P4-001 (Hard)
- **Output:** Catatan uji fresh clone + keputusan G4
- **File dimiliki:** `docs/STATUS.md`
- **Langkah:** Clone bersih → compose up + lint + test → Catat hambatan
- **Spesifikasi teknis:** Checklist G4
- **Kriteria penerimaan:** Semua cek lulus tanpa bantuan pemilik.
- **Verifikasi otomatis:** Log perintah
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tim (G4)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Manusia

## P5 — ETL & Cassandra Implementation

| ID | Judul | Pemilik | Prio | O/M/P → PERT (j) | Dependensi | Rencana | Status |
|---|---|---|---|---|---|---|---|
| **A-P5-001** ⚑ | Source adapter + extractor FIRMS (kuota, retry, raw zone) | A (R1) | Must | 2/3/5 → 3.17 | GATE-G3·HA, GATE-G4·HA, A-P4-001·H | D9–D9 | Belum mulai |
| **A-P5-002** ⚑ | Parsing & validasi + rejected records | A (R1) | Must | 2/3/5 → 3.17 | A-P5-001·S, A-P3-002·H, GATE-G3·HA, GATE-G4·HA | D9–D10 | Belum mulai |
| **A-P5-003** ⚑ | Normalisasi waktu & atribut | A (R1) | Must | 1.5/2.5/4 → 2.58 | A-P5-002·H | D10–D11 | Belum mulai |
| **A-P5-004** ⚑ | Pengayaan spasial (provinsi, status luar provinsi) | A (R1) | Must | 2/3/5 → 3.17 | A-P5-002·S, GATE-G3·HA, GATE-G4·HA | D10–D10 | Belum mulai |
| **A-P5-005** ⚑ | Deduplikasi & identitas deteksi | A (R1) | Must | 2/3/5 → 3.17 | A-P5-003·H, A-P5-004·H | D11–D12 | Belum mulai |
| **A-P5-006** ⚑ | Mode backfill (checkpoint, resume, run log) | A (R1) | Must | 2/3/4 → 3.0 | A-P5-005·H, B-P5-002·I, B-P5-004·I | D12–D12 | Belum mulai |
| **A-P5-007** ⚑ | Mode incremental NRT (polling) | A (R1) | Must | 2/3/5 → 3.17 | A-P5-006·H | D12–D13 | Belum mulai |
| **A-P5-008** ⚑ | Test ETL + harness idempotensi | A (R1) | Must | 2/3/4 → 3.0 | A-P5-005·H | D13–D14 | Belum mulai |
| **A-P5-009** ⚑ | Publikasi batas provinsi tersederhanakan untuk web | A (R1) | Must | 0.5/1/2 → 1.08 | A-P5-004·H | D12–D12 | Belum mulai |
| **A-P5-010** | Dokumentasi pipeline | A (R1) | Must | 0.5/1/1.5 → 1.0 | A-P5-007·H | D14–D14 | Belum mulai |
| **B-P5-001** | Implementasi skema CQL v1 + migrasi | B (R2) | Must | 1.5/2/3 → 2.08 | GATE-G3·HA, GATE-G4·HA, B-P4-001·H | D9–D10 | Belum mulai |
| **B-P5-002** | Writer adapter Cassandra (idempoten) | B (R2) | Must | 2/3/5 → 3.17 | B-P5-001·H, A-P3-001·I | D10–D10 | Belum mulai |
| **B-P5-003** | Builder read model/agregat | B (R2) | Must | 2/3/5 → 3.17 | B-P5-002·H, B-P3-003·H | D11–D12 | Belum mulai |
| **B-P5-004** | Tabel run log & checkpoint + writer | B (R2) | Must | 1.5/2/3 → 2.08 | B-P5-001·H | D10–D11 | Belum mulai |
| **B-P5-005** | Test database per access pattern | B (R2) | Must | 1.5/2.5/4 → 2.58 | B-P5-003·H | D12–D12 | Belum mulai |
| **B-P5-006** | Load backfill penuh + inspeksi ukuran partisi | B (R2) | Must | 1.5/2.5/4 → 2.58 | A-P5-006·H, B-P5-003·H | D12–D13 | Belum mulai |
| **B-P5-007** | Dokumentasi database | B (R2) | Must | 0.5/1/1.5 → 1.0 | B-P5-005·H | D13–D13 | Belum mulai |
| **X-P5-901** ⚑ | Checkpoint D10 (R-14) + paket G5 | B (R2) | Must | 0.5/1/1.5 → 1.0 | A-P5-007·H, A-P5-008·H, B-P5-005·H, B-P5-006·H | D14–D14 | Belum mulai |

⚑ = berada di rantai kritis.

### A-P5-001 — Source adapter + extractor FIRMS (kuota, retry, raw zone)

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** Antarmuka source adapter dan implementasi Area API dengan penjaga kuota, retry, manifest SHA-256.
- **Alasan:** OQ-28; raw zone (R-04).
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 5 → PERT 3.17 jam · **Rencana:** D9 (2026-11-27) – D9 (2026-11-27)
- **Input:** ETL spec, inventaris sumber
- **Dependensi:** GATE-G3 (Human approval); GATE-G4 (Human approval); A-P4-001 (Hard)
- **Output:** pipeline/src/.../extract/
- **File dimiliki:** `pipeline/`
- **Langkah:** Interface adapter → Extractor + manifest → Test dengan respons tiruan (tanpa API)
- **Spesifikasi teknis:** 03-etl-spec.md
- **Kriteria penerimaan:** Test unit lulus tanpa jaringan; MAP_KEY tidak pernah muncul di log (test).
- **Verifikasi otomatis:** pytest + test redaksi log
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P5-002 — Parsing & validasi + rejected records

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** Parser per sumber dan aturan DQ dengan reason code.
- **Alasan:** Kualitas data terukur (O-E1).
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 5 → PERT 3.17 jam · **Rencana:** D9 (2026-11-27) – D10 (2026-11-28)
- **Input:** Aturan DQ, fixtures
- **Dependensi:** A-P5-001 (Soft); A-P3-002 (Hard); GATE-G3 (Human approval); GATE-G4 (Human approval)
- **Output:** pipeline/src/.../validate/
- **File dimiliki:** `pipeline/`
- **Langkah:** Parser per header → Aturan DQ-xx → Simpan rejected + alasan
- **Spesifikasi teknis:** 06-data-quality-rules.md
- **Kriteria penerimaan:** Setiap aturan DQ punya test positif & negatif.
- **Verifikasi otomatis:** pytest
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P5-003 — Normalisasi waktu & atribut

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** UTC timestamp, padding acq_time, tanggal lokal per provinsi, normalisasi confidence & processing level.
- **Alasan:** R-07; OQ-08.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2.5 / P 4 → PERT 2.58 jam · **Rencana:** D10 (2026-11-28) – D11 (2026-11-29)
- **Input:** Kontrak canonical, semantik data
- **Dependensi:** A-P5-002 (Hard)
- **Output:** pipeline/src/.../normalize/
- **File dimiliki:** `pipeline/`
- **Langkah:** Konversi waktu → Tanggal lokal butuh provinsi → setelah enrichment → Test kasus malam lintas tanggal
- **Spesifikasi teknis:** SEM-xx
- **Kriteria penerimaan:** Test malam lintas tanggal WIB/WITA/WIT lulus.
- **Verifikasi otomatis:** pytest
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P5-004 — Pengayaan spasial (provinsi, status luar provinsi)

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** Assign provinsi (dan kab/kota bila Could disetujui) dari snapshot batas ber-checksum.
- **Alasan:** OQ-06, OQ-11.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 5 → PERT 3.17 jam · **Rencana:** D10 (2026-11-28) – D10 (2026-11-28)
- **Input:** Snapshot batas (HD-08)
- **Dependensi:** A-P5-002 (Soft); GATE-G3 (Human approval); GATE-G4 (Human approval)
- **Output:** pipeline/src/.../enrich/
- **File dimiliki:** `pipeline/`
- **Langkah:** Loader snapshot + checksum → Point-in-polygon → Status wilayah khusus
- **Spesifikasi teknis:** 05-boundary-sources.md
- **Kriteria penerimaan:** Hasil cocok dengan coord_assign Fase 1 pada fixtures (selisih 0 kecuali tepi yang terdokumentasi).
- **Verifikasi otomatis:** pytest golden
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P5-005 — Deduplikasi & identitas deteksi

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** detection_id deterministik dan aturan presedensi SP>NRT.
- **Alasan:** R-06 (skor 9).
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** B
- **Estimasi:** O 2 / M 3 / P 5 → PERT 3.17 jam · **Rencana:** D11 (2026-11-29) – D12 (2026-11-30)
- **Input:** Kontrak canonical, hasil A-P1-007
- **Dependensi:** A-P5-003 (Hard); A-P5-004 (Hard)
- **Output:** pipeline/src/.../dedup/
- **File dimiliki:** `pipeline/`
- **Langkah:** Implementasi kunci → Presedensi sumber → Property test: urutan input tidak mengubah hasil
- **Spesifikasi teknis:** 02-canonical-event-contract.md
- **Kriteria penerimaan:** Dua run dengan urutan input berbeda → set detection_id identik.
- **Verifikasi otomatis:** pytest (property test)
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P5-006 — Mode backfill (checkpoint, resume, run log)

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** CLI backfill rentang tanggal dengan checkpoint dan run log memakai writer B.
- **Alasan:** MVP kapabilitas 1.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D12 (2026-11-30) – D12 (2026-11-30)
- **Input:** Writer & run-log API dari B
- **Dependensi:** A-P5-005 (Hard); B-P5-002 (Interface); B-P5-004 (Interface)
- **Output:** pipeline/src/.../modes/backfill.py
- **File dimiliki:** `pipeline/`
- **Langkah:** CLI → Checkpoint per chunk tanggal → Run log
- **Spesifikasi teknis:** 03-etl-spec.md
- **Kriteria penerimaan:** Backfill terputus dapat dilanjutkan tanpa duplikat.
- **Verifikasi otomatis:** Test integrasi dengan Cassandra container
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'pipeline/src/.../modes/backfill.py' ke R2 untuk B-P5-006. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P5-007 — Mode incremental NRT (polling)

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** Poller berkala dengan jendela overlap, checkpoint waktu, dan pencatatan kegagalan.
- **Alasan:** Fitur #12 Must; target berjalan ±D10.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 5 → PERT 3.17 jam · **Rencana:** D12 (2026-11-30) – D13 (2026-12-01)
- **Input:** NFR interval polling
- **Dependensi:** A-P5-006 (Hard)
- **Output:** pipeline/src/.../modes/incremental.py
- **File dimiliki:** `pipeline/`
- **Langkah:** Loop poll → Overlap window → Catat sukses/gagal ke run log
- **Spesifikasi teknis:** 03-etl-spec.md, NFR
- **Kriteria penerimaan:** Poll berulang pada jendela sama tidak menambah baris.
- **Verifikasi otomatis:** Test integrasi: 2 poll tumpang tindih → jumlah sama
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'pipeline/src/.../modes/incremental.py' ke R2, R3 untuk X-P5-901, C-P7-003. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P5-008 — Test ETL + harness idempotensi

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** Test unit kasus tepi dan harness yang membandingkan dua run.
- **Alasan:** Kriteria keberhasilan #2.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D13 (2026-12-01) – D14 (2026-12-02)
- **Input:** Fixtures
- **Dependensi:** A-P5-005 (Hard)
- **Output:** pipeline/tests/
- **File dimiliki:** `pipeline/tests/`
- **Langkah:** Edge cases waktu/dedup → Harness: run 2× → bandingkan jumlah & checksum → Masuk CI
- **Spesifikasi teknis:** O-E1
- **Kriteria penerimaan:** Harness gagal bila ada perbedaan; lulus pada kode saat ini.
- **Verifikasi otomatis:** pytest di CI
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'pipeline/tests/' ke R2 untuk X-P5-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P5-009 — Publikasi batas provinsi tersederhanakan untuk web

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** GeoJSON tersederhanakan kecil + atribusi untuk lapisan peta.
- **Alasan:** Dibutuhkan D-P6-004.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 0.5 / M 1 / P 2 → PERT 1.08 jam · **Rencana:** D12 (2026-11-30) – D12 (2026-11-30)
- **Input:** Snapshot batas
- **Dependensi:** A-P5-004 (Hard)
- **Output:** pipeline/resources/boundaries/provinces-simplified.geojson
- **File dimiliki:** `pipeline/resources/`
- **Langkah:** Simplify → Ukur ukuran file → Serahkan ke D
- **Spesifikasi teknis:** HD-08 (lisensi sebelum commit)
- **Kriteria penerimaan:** Ukuran ≤ batas NFR; 38 provinsi.
- **Verifikasi otomatis:** Skrip hitung fitur & ukuran
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** HD-08
- **Serah-terima:** Serahkan 'pipeline/resources/boundaries/provinces-simplified.geojson' ke R4 untuk D-P6-004. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P5-010 — Dokumentasi pipeline

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** pipeline/README: instalasi, mode, konfigurasi, run log, rejected records.
- **Alasan:** O-E4.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 0.5 / M 1 / P 1.5 → PERT 1.0 jam · **Rencana:** D14 (2026-12-02) – D14 (2026-12-02)
- **Input:** Kode pipeline
- **Dependensi:** A-P5-007 (Hard)
- **Output:** pipeline/README.md
- **File dimiliki:** `pipeline/README.md`
- **Langkah:** Cara jalan per mode → Variabel env → Troubleshooting
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** Anggota lain menjalankan backfill kecil hanya dari README.
- **Verifikasi otomatis:** Uji oleh manusia
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P5-001 — Implementasi skema CQL v1 + migrasi

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** File migrasi bernomor dan skrip apply idempoten sesuai skema yang disetujui G3.
- **Alasan:** Skema versi terkontrol.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D9 (2026-11-27) – D10 (2026-11-28)
- **Input:** schema-v1.cql (G3)
- **Dependensi:** GATE-G3 (Human approval); GATE-G4 (Human approval); B-P4-001 (Hard)
- **Output:** db/migrations/0001_*.cql, db/scripts/migrate.*
- **File dimiliki:** `db/`
- **Langkah:** Salin skema disetujui ke migrasi → Skrip apply (IF NOT EXISTS) → Test apply 2×
- **Spesifikasi teknis:** Tanpa drop/truncate otomatis
- **Kriteria penerimaan:** Apply 2× tanpa error; skema identik dengan spesifikasi.
- **Verifikasi otomatis:** Test: describe schema vs spesifikasi
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Operasi destruktif butuh persetujuan manusia
- **Serah-terima:** Serahkan 'db/migrations/0001_*.cql, db/scripts/migrate.*' ke R3 untuk C-P6-007. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P5-002 — Writer adapter Cassandra (idempoten)

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** Library penulis dengan prepared statements, upsert idempoten, batch per partisi, consistency level terdokumentasi.
- **Alasan:** Antarmuka ETL→Cassandra.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** A
- **Estimasi:** O 2 / M 3 / P 5 → PERT 3.17 jam · **Rencana:** D10 (2026-11-28) – D10 (2026-11-28)
- **Input:** Kontrak canonical, skema
- **Dependensi:** B-P5-001 (Hard); A-P3-001 (Interface)
- **Output:** db/src/.../writer.py
- **File dimiliki:** `db/`
- **Langkah:** API write_events(events) → Prepared statements → Test tulis 2× → jumlah sama
- **Spesifikasi teknis:** 06 kontrak B
- **Kriteria penerimaan:** Menulis ulang event yang sama tidak menambah baris.
- **Verifikasi otomatis:** Test integrasi container
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'db/src/.../writer.py' ke R1 untuk A-P5-006. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P5-003 — Builder read model/agregat

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** Hitung ulang agregat provinsi-hari/bulan secara absolut setelah load.
- **Alasan:** Ranking & timeline (fitur #1, #3, #4).
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 5 → PERT 3.17 jam · **Rencana:** D11 (2026-11-29) – D12 (2026-11-30)
- **Input:** 04-aggregates.md
- **Dependensi:** B-P5-002 (Hard); B-P3-003 (Hard)
- **Output:** db/src/.../aggregates.py
- **File dimiliki:** `db/`
- **Langkah:** Hitung per partisi terdampak → Tulis nilai absolut → Rebuild penuh
- **Spesifikasi teknis:** Tanpa counter
- **Kriteria penerimaan:** Agregat = jumlah dari tabel detail untuk sampel provinsi/hari.
- **Verifikasi otomatis:** Test konsistensi agregat vs detail
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'db/src/.../aggregates.py' ke R3 untuk C-P6-007. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P5-004 — Tabel run log & checkpoint + writer

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** Tabel dan API untuk run log, checkpoint, status poll.
- **Alasan:** Monitoring (fitur #9) dan resume ETL.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D10 (2026-11-28) – D11 (2026-11-29)
- **Input:** ETL spec
- **Dependensi:** B-P5-001 (Hard)
- **Output:** db/src/.../runlog.py
- **File dimiliki:** `db/`
- **Langkah:** Tabel → API tulis/baca → Test
- **Spesifikasi teknis:** 06 kontrak B/C
- **Kriteria penerimaan:** Endpoint status (C) dapat membaca run terakhir dengan 1 query partisi.
- **Verifikasi otomatis:** Test integrasi
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'db/src/.../runlog.py' ke R1, R3 untuk A-P5-006, C-P6-006. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P5-005 — Test database per access pattern

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** Smoke test setiap Q-xx dan pemeriksaan bahwa tidak ada ALLOW FILTERING.
- **Alasan:** O-E2.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2.5 / P 4 → PERT 2.58 jam · **Rencana:** D12 (2026-11-30) – D12 (2026-11-30)
- **Input:** Access patterns
- **Dependensi:** B-P5-003 (Hard)
- **Output:** db/tests/
- **File dimiliki:** `db/tests/`
- **Langkah:** Satu test per Q-xx → Grep ALLOW FILTERING di repo → 0 → Masuk CI (job dengan Cassandra)
- **Spesifikasi teknis:** 02-access-patterns.md
- **Kriteria penerimaan:** Semua Q-xx lulus; 0 ALLOW FILTERING.
- **Verifikasi otomatis:** pytest db + grep
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P5-006 — Load backfill penuh + inspeksi ukuran partisi

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** Memuat periode final dan membandingkan ukuran partisi nyata dengan estimasi.
- **Alasan:** Validasi model (R-05) dan data untuk G5.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** A
- **Estimasi:** O 1.5 / M 2.5 / P 4 → PERT 2.58 jam · **Rencana:** D12 (2026-11-30) – D13 (2026-12-01)
- **Input:** Pipeline backfill, data mentah
- **Dependensi:** A-P5-006 (Hard); B-P5-003 (Hard)
- **Output:** Catatan load + tabel ukuran partisi di db/README.md
- **File dimiliki:** `db/README.md`
- **Langkah:** Jalankan backfill → nodetool tablestats/tablehistograms → Bandingkan dengan 00-volume-estimates
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** Jumlah baris di Cassandra = jumlah event lolos ETL; ukuran partisi maks tercatat.
- **Verifikasi otomatis:** Query hitung vs run log
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P5-007 — Dokumentasi database

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** db/README: setup, skema, contoh query, migrasi.
- **Alasan:** O-E4.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 0.5 / M 1 / P 1.5 → PERT 1.0 jam · **Rencana:** D13 (2026-12-01) – D13 (2026-12-01)
- **Input:** Kode db
- **Dependensi:** B-P5-005 (Hard)
- **Output:** db/README.md
- **File dimiliki:** `db/README.md`
- **Langkah:** Setup → Contoh query per Q-xx → Prosedur rebuild agregat
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** Anggota lain menjalankan contoh query dari README.
- **Verifikasi otomatis:** Uji oleh manusia
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### X-P5-901 — Checkpoint D10 (R-14) + paket G5

- **Fase / prioritas / status:** P5 · Must · Belum mulai
- **Tujuan:** Memastikan data nyata ada di Cassandra dan poller berjalan; aktifkan kontingensi bila tidak.
- **Alasan:** Titik kritis charter §10.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 0.5 / M 1 / P 1.5 → PERT 1.0 jam · **Rencana:** D14 (2026-12-02) – D14 (2026-12-02)
- **Input:** Hasil Fase 5
- **Dependensi:** A-P5-007 (Hard); A-P5-008 (Hard); B-P5-005 (Hard); B-P5-006 (Hard)
- **Output:** Keputusan G5
- **File dimiliki:** `docs/STATUS.md`
- **Langkah:** Cek kriteria → Putuskan kontingensi → Catat
- **Spesifikasi teknis:** Checklist G5
- **Kriteria penerimaan:** Checklist G5 lengkap.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tim (G5)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Manusia + agen pencatat

## P6 — Backend & Frontend Implementation

| ID | Judul | Pemilik | Prio | O/M/P → PERT (j) | Dependensi | Rencana | Status |
|---|---|---|---|---|---|---|---|
| **C-P6-001** | Skeleton FastAPI (config, health, logging, error, CORS) | C (R3) | Must | 1.5/2.5/3.5 → 2.5 | GATE-G3·HA, GATE-G4·HA | D9–D9 | Belum mulai |
| **C-P6-002** | Interface repository + fake dari contoh kontrak | C (R3) | Must | 1.5/2/3 → 2.08 | C-P6-001·H, C-P3-002·I | D9–D10 | Belum mulai |
| **C-P6-003** | Endpoint ringkasan + timeline | C (R3) | Must | 2/3/4 → 3.0 | C-P6-002·H | D10–D10 | Belum mulai |
| **C-P6-004** | Endpoint ranking + detail provinsi | C (R3) | Must | 1.5/2.5/4 → 2.58 | C-P6-002·H | D11–D12 | Belum mulai |
| **C-P6-005** | Endpoint titik peta (terbatas) | C (R3) | Must | 2/3/4 → 3.0 | C-P6-002·H | D10–D11 | Belum mulai |
| **C-P6-006** | Endpoint status pipeline & kesegaran data | C (R3) | Must | 1/1.5/2 → 1.5 | C-P6-002·H, B-P5-004·I | D12–D12 | Belum mulai |
| **C-P6-007** | Repository Cassandra nyata | C (R3) | Must | 2/3.5/5 → 3.5 | C-P6-003·H, C-P6-004·H, C-P6-005·H, C-P6-006·H, B-P5-001·H, B-P5-003·I | D12–D13 | Belum mulai |
| **C-P6-008** | Test API (unit, kontrak, integrasi) | C (R3) | Must | 2/3/4 → 3.0 | C-P6-007·H | D13–D13 | Belum mulai |
| **C-P6-009** | Dokumentasi API | C (R3) | Must | 0.5/1/1.5 → 1.0 | C-P6-008·H | D13–D13 | Belum mulai |
| **C-P6-010** | Endpoint distribusi FRP (Should) | C (R3) | Should | 2/3/4 → 3.0 | C-P6-007·H | D13–D14 | Belum mulai |
| **D-P6-001** | Layout, routing, state filter, klien API | D (R4) | Must | 2/3/4 → 3.0 | GATE-G3·HA, GATE-G4·HA, D-P4-002·H | D9–D9 | Belum mulai |
| **D-P6-002** | Kartu KPI + timeline | D (R4) | Must | 2/3/5 → 3.17 | D-P6-001·H | D10–D11 | Belum mulai |
| **D-P6-003** | Ranking + drill-down provinsi | D (R4) | Must | 2/3/5 → 3.17 | D-P6-001·H | D11–D12 | Belum mulai |
| **D-P6-004** | Peta Leaflet (titik, batas, popup, notice batas) | D (R4) | Must | 3/4/6 → 4.17 | D-P6-001·H, A-P5-009·S | D9–D10 | Belum mulai |
| **D-P6-005** | Status pipeline + kesegaran + disclaimer + atribusi | D (R4) | Must | 1.5/2/3 → 2.08 | D-P6-001·H | D14–D14 | Belum mulai |
| **D-P6-006** | State loading/empty/error + aksesibilitas dasar | D (R4) | Must | 1.5/2/3 → 2.08 | D-P6-002·H, D-P6-003·H, D-P6-004·H | D12–D12 | Belum mulai |
| **D-P6-007** | Ganti mock → API nyata (lokal) | D (R4) | Must | 1/2/3 → 2.0 | D-P6-006·H, C-P6-007·H | D13–D13 | Belum mulai |
| **D-P6-008** | Histogram FRP + perbandingan periode (Should) | D (R4) | Should | 3/4/6 → 4.17 | D-P6-007·H, C-P6-010·I | D17–D18 | Belum mulai |
| **D-P6-009** | Test frontend (unit/komponen) | D (R4) | Must | 1.5/2.5/4 → 2.58 | D-P6-006·H | D13–D14 | Belum mulai |
| **X-P6-901** ⚑ | Integrasi E2E lokal pertama (D13) + paket G6 | B (R2) | Must | 0.5/1/1.5 → 1.0 | D-P6-007·H, C-P6-008·H, X-P5-901·H | D14–D14 | Belum mulai |

⚑ = berada di rantai kritis.

### C-P6-001 — Skeleton FastAPI (config, health, logging, error, CORS)

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Aplikasi dasar dengan readiness yang memeriksa Cassandra, skema error seragam.
- **Alasan:** Dasar semua endpoint.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2.5 / P 3.5 → PERT 2.5 jam · **Rencana:** D9 (2026-11-27) – D9 (2026-11-27)
- **Input:** openapi.yaml, ADR-004
- **Dependensi:** GATE-G3 (Human approval); GATE-G4 (Human approval)
- **Output:** api/
- **File dimiliki:** `api/`
- **Langkah:** Struktur app → Health/readiness → Error handler sesuai skema
- **Spesifikasi teknis:** openapi.yaml
- **Kriteria penerimaan:** GET /health 200; error mengikuti skema kontrak.
- **Verifikasi otomatis:** pytest api
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P6-002 — Interface repository + fake dari contoh kontrak

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Protokol repository per Q-xx dan implementasi fake in-memory.
- **Alasan:** Backend tidak menunggu Cassandra.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D9 (2026-11-27) – D10 (2026-11-28)
- **Input:** Access patterns, contoh OpenAPI
- **Dependensi:** C-P6-001 (Hard); C-P3-002 (Interface)
- **Output:** api/src/.../repositories/
- **File dimiliki:** `api/`
- **Langkah:** Interface → Fake dari sampel canonical → Dependency injection
- **Spesifikasi teknis:** 06 kontrak C
- **Kriteria penerimaan:** Semua endpoint dapat diuji dengan fake.
- **Verifikasi otomatis:** pytest
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P6-003 — Endpoint ringkasan + timeline

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Endpoint fitur #1 & #3.
- **Alasan:** Must.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D10 (2026-11-28) – D10 (2026-11-28)
- **Input:** Kontrak
- **Dependensi:** C-P6-002 (Hard)
- **Output:** api/ endpoint
- **File dimiliki:** `api/`
- **Langkah:** Validasi parameter → Service → Test
- **Spesifikasi teknis:** openapi.yaml
- **Kriteria penerimaan:** Respons lolos validasi skema; tanggal memakai aturan SEM.
- **Verifikasi otomatis:** pytest + contract test
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P6-004 — Endpoint ranking + detail provinsi

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Endpoint fitur #4 & #8.
- **Alasan:** Must.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2.5 / P 4 → PERT 2.58 jam · **Rencana:** D11 (2026-11-29) – D12 (2026-11-30)
- **Input:** Kontrak
- **Dependensi:** C-P6-002 (Hard)
- **Output:** api/ endpoint
- **File dimiliki:** `api/`
- **Langkah:** Validasi → Service (luar provinsi dikecualikan) → Test
- **Spesifikasi teknis:** OQ-11
- **Kriteria penerimaan:** Wilayah khusus tidak masuk ranking; lolos skema.
- **Verifikasi otomatis:** pytest + contract test
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P6-005 — Endpoint titik peta (terbatas)

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Endpoint fitur #2 dengan batas jumlah titik.
- **Alasan:** C-10.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D10 (2026-11-28) – D11 (2026-11-29)
- **Input:** Kontrak, NFR batas titik
- **Dependensi:** C-P6-002 (Hard)
- **Output:** api/ endpoint
- **File dimiliki:** `api/`
- **Langkah:** Validasi rentang → Batas + flag truncated → Test
- **Spesifikasi teknis:** NFR
- **Kriteria penerimaan:** Respons tidak pernah melebihi batas; flag truncated benar.
- **Verifikasi otomatis:** pytest
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P6-006 — Endpoint status pipeline & kesegaran data

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Fitur #9 dan waktu pembaruan terakhir.
- **Alasan:** R-27.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 1 / M 1.5 / P 2 → PERT 1.5 jam · **Rencana:** D12 (2026-11-30) – D12 (2026-11-30)
- **Input:** Kontrak run log
- **Dependensi:** C-P6-002 (Hard); B-P5-004 (Interface)
- **Output:** api/ endpoint
- **File dimiliki:** `api/`
- **Langkah:** Baca run terakhir → Hitung umur data → Test
- **Spesifikasi teknis:** OQ-22
- **Kriteria penerimaan:** Poll gagal terakhir terlihat di respons.
- **Verifikasi otomatis:** pytest
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P6-007 — Repository Cassandra nyata

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Implementasi repository dengan prepared statements sesuai access patterns.
- **Alasan:** Mengganti fake dengan data nyata.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3.5 / P 5 → PERT 3.5 jam · **Rencana:** D12 (2026-11-30) – D13 (2026-12-01)
- **Input:** Skema, access patterns
- **Dependensi:** C-P6-003 (Hard); C-P6-004 (Hard); C-P6-005 (Hard); C-P6-006 (Hard); B-P5-001 (Hard); B-P5-003 (Interface)
- **Output:** api/src/.../repositories/cassandra.py
- **File dimiliki:** `api/`
- **Langkah:** Satu metode per Q-xx → Prepared statements → Test integrasi
- **Spesifikasi teknis:** 06 kontrak C
- **Kriteria penerimaan:** Hasil fake vs Cassandra konsisten untuk fixture yang sama.
- **Verifikasi otomatis:** Test integrasi container
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'api/src/.../repositories/cassandra.py' ke R4 untuk D-P6-007. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P6-008 — Test API (unit, kontrak, integrasi)

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Suite test API di CI.
- **Alasan:** Kriteria mutu.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D13 (2026-12-01) – D13 (2026-12-01)
- **Input:** openapi.yaml
- **Dependensi:** C-P6-007 (Hard)
- **Output:** api/tests/
- **File dimiliki:** `api/tests/`
- **Langkah:** Contract test vs openapi.yaml → Integrasi Cassandra → CI
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** Setiap endpoint punya test sukses + error.
- **Verifikasi otomatis:** pytest di CI
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'api/tests/' ke R2 untuk X-P6-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P6-009 — Dokumentasi API

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** api/README + contoh curl.
- **Alasan:** O-E4.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 0.5 / M 1 / P 1.5 → PERT 1.0 jam · **Rencana:** D13 (2026-12-01) – D13 (2026-12-01)
- **Input:** Kode API
- **Dependensi:** C-P6-008 (Hard)
- **Output:** api/README.md
- **File dimiliki:** `api/README.md`
- **Langkah:** Cara jalan → Contoh request → Kode error
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** Anggota lain menjalankan contoh.
- **Verifikasi otomatis:** Uji oleh manusia
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P6-010 — Endpoint distribusi FRP (Should)

- **Fase / prioritas / status:** P6 · Should · Belum mulai
- **Tujuan:** Fitur #7.
- **Alasan:** Should.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D13 (2026-12-01) – D14 (2026-12-02)
- **Input:** Kontrak (bila disetujui)
- **Dependensi:** C-P6-007 (Hard)
- **Output:** api/ endpoint
- **File dimiliki:** `api/`
- **Langkah:** Bin FRP → Test
- **Spesifikasi teknis:** Butuh CR bila belum ada di kontrak v1
- **Kriteria penerimaan:** Lolos skema.
- **Verifikasi otomatis:** pytest
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** CR bila mengubah kontrak
- **Serah-terima:** Serahkan 'api/ endpoint' ke R4 untuk D-P6-008. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P6-001 — Layout, routing, state filter, klien API

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Kerangka aplikasi, filter global (tanggal, provinsi, confidence, satelit), klien API dari kontrak.
- **Alasan:** Dasar semua halaman.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D9 (2026-11-27) – D9 (2026-11-27)
- **Input:** UI spec, openapi.yaml
- **Dependensi:** GATE-G3 (Human approval); GATE-G4 (Human approval); D-P4-002 (Hard)
- **Output:** web/src/
- **File dimiliki:** `web/`
- **Langkah:** Routing → State filter + sinkron URL → Klien API bertipe
- **Spesifikasi teknis:** 01-ui-spec.md
- **Kriteria penerimaan:** Filter tercermin di URL; klien hanya memakai field kontrak.
- **Verifikasi otomatis:** npm test
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P6-002 — Kartu KPI + timeline

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Fitur #1 & #3.
- **Alasan:** Must.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 5 → PERT 3.17 jam · **Rencana:** D10 (2026-11-28) – D11 (2026-11-29)
- **Input:** Mock API
- **Dependensi:** D-P6-001 (Hard)
- **Output:** web/src/features/summary/
- **File dimiliki:** `web/`
- **Langkah:** Komponen → Format tanggal lokal → Test
- **Spesifikasi teknis:** UI spec
- **Kriteria penerimaan:** Sesuai wireframe; label 'deteksi hotspot'.
- **Verifikasi otomatis:** npm test
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P6-003 — Ranking + drill-down provinsi

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Fitur #4 & #8.
- **Alasan:** Must.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 5 → PERT 3.17 jam · **Rencana:** D11 (2026-11-29) – D12 (2026-11-30)
- **Input:** Mock API
- **Dependensi:** D-P6-001 (Hard)
- **Output:** web/src/features/ranking/
- **File dimiliki:** `web/`
- **Langkah:** Tabel ranking → Drill-down → Test
- **Spesifikasi teknis:** UI spec
- **Kriteria penerimaan:** Klik provinsi memfilter semua tampilan.
- **Verifikasi otomatis:** npm test
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P6-004 — Peta Leaflet (titik, batas, popup, notice batas)

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Fitur #2.
- **Alasan:** Must.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 3 / M 4 / P 6 → PERT 4.17 jam · **Rencana:** D9 (2026-11-27) – D10 (2026-11-28)
- **Input:** Mock API, GeoJSON batas
- **Dependensi:** D-P6-001 (Hard); A-P5-009 (Soft)
- **Output:** web/src/features/map/
- **File dimiliki:** `web/`
- **Langkah:** Lapisan titik → Lapisan batas → Notice truncated
- **Spesifikasi teknis:** UI spec
- **Kriteria penerimaan:** Peta tetap responsif pada jumlah titik maksimum NFR.
- **Verifikasi otomatis:** npm test + uji manual terukur
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P6-005 — Status pipeline + kesegaran + disclaimer + atribusi

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Fitur #9, disclaimer, atribusi FIRMS & BIG.
- **Alasan:** Kriteria keberhasilan #5, #7.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D14 (2026-12-02) – D14 (2026-12-02)
- **Input:** Mock API
- **Dependensi:** D-P6-001 (Hard)
- **Output:** web/src/features/status/
- **File dimiliki:** `web/`
- **Langkah:** Halaman status → Indikator kesegaran global → Footer disclaimer & atribusi
- **Spesifikasi teknis:** Charter §3
- **Kriteria penerimaan:** Disclaimer & waktu pembaruan terlihat di semua halaman.
- **Verifikasi otomatis:** npm test
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Teks disclaimer final: tim
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P6-006 — State loading/empty/error + aksesibilitas dasar

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Perilaku konsisten untuk semua state.
- **Alasan:** Kontrak E (frontend→pengguna).
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D12 (2026-11-30) – D12 (2026-11-30)
- **Input:** UI spec
- **Dependensi:** D-P6-002 (Hard); D-P6-003 (Hard); D-P6-004 (Hard)
- **Output:** web/src/components/
- **File dimiliki:** `web/`
- **Langkah:** Komponen state → Skenario error mock → Cek kontras & keyboard
- **Spesifikasi teknis:** 06 kontrak E
- **Kriteria penerimaan:** Setiap halaman menangani 3 state.
- **Verifikasi otomatis:** npm test dengan mock error
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P6-007 — Ganti mock → API nyata (lokal)

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Menjalankan dashboard pada API nyata dan menyelesaikan checklist mock-to-real.
- **Alasan:** Milestone integrasi D13.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** C
- **Estimasi:** O 1 / M 2 / P 3 → PERT 2.0 jam · **Rencana:** D13 (2026-12-01) – D13 (2026-12-01)
- **Input:** API nyata lokal
- **Dependensi:** D-P6-006 (Hard); C-P6-007 (Hard)
- **Output:** Checklist mock-to-real terisi
- **File dimiliki:** `web/`
- **Langkah:** Matikan flag mock → Bandingkan tiap halaman → Laporkan ketidakcocokan sebagai CR
- **Spesifikasi teknis:** 06 §mock-to-real
- **Kriteria penerimaan:** Semua halaman Must berjalan di data nyata tanpa error konsol.
- **Verifikasi otomatis:** Smoke manual + E2E lokal
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'Checklist mock-to-real terisi' ke R2 untuk X-P6-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P6-008 — Histogram FRP + perbandingan periode (Should)

- **Fase / prioritas / status:** P6 · Should · Belum mulai
- **Tujuan:** Fitur #5 & #7.
- **Alasan:** Should; hanya setelah semua Must berjalan.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 3 / M 4 / P 6 → PERT 4.17 jam · **Rencana:** D17 (2026-12-05) – D18 (2026-12-06)
- **Input:** Endpoint FRP
- **Dependensi:** D-P6-007 (Hard); C-P6-010 (Interface)
- **Output:** web/src/features/frp/
- **File dimiliki:** `web/`
- **Langkah:** Komponen → Catatan metodologi → Test
- **Spesifikasi teknis:** C-05
- **Kriteria penerimaan:** Perbandingan hanya untuk produk/satelit sama.
- **Verifikasi otomatis:** npm test
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P6-009 — Test frontend (unit/komponen)

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Test filter, format tanggal lokal, state.
- **Alasan:** Mutu.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2.5 / P 4 → PERT 2.58 jam · **Rencana:** D13 (2026-12-01) – D14 (2026-12-02)
- **Input:** Komponen
- **Dependensi:** D-P6-006 (Hard)
- **Output:** web/src/**/*.test.*
- **File dimiliki:** `web/`
- **Langkah:** Test filter → Test format waktu → CI
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** Coverage komponen inti tercatat.
- **Verifikasi otomatis:** npm test di CI
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### X-P6-901 — Integrasi E2E lokal pertama (D13) + paket G6

- **Fase / prioritas / status:** P6 · Must · Belum mulai
- **Tujuan:** Demo internal end-to-end lokal; putuskan kontingensi R-14 bila gagal.
- **Alasan:** Titik kritis charter §10.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 0.5 / M 1 / P 1.5 → PERT 1.0 jam · **Rencana:** D14 (2026-12-02) – D14 (2026-12-02)
- **Input:** Stack lokal
- **Dependensi:** D-P6-007 (Hard); C-P6-008 (Hard); X-P5-901 (Hard)
- **Output:** Keputusan G6
- **File dimiliki:** `docs/STATUS.md`
- **Langkah:** compose up → ingest → dashboard
- **Spesifikasi teknis:** Checklist G6
- **Kriteria penerimaan:** Checklist G6 lengkap.
- **Verifikasi otomatis:** Log demo
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tim (G6)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Manusia

## P7 — Integration, Testing & Experiments

| ID | Judul | Pemilik | Prio | O/M/P → PERT (j) | Dependensi | Rencana | Status |
|---|---|---|---|---|---|---|---|
| **C-P7-001** ⚑ | Skrip smoke E2E stack penuh | C (R3) | Must | 1.5/2/3 → 2.08 | GATE-G6·HA | D16–D17 | Belum mulai |
| **A-P7-001** | Uji idempotensi pada data nyata | A (R1) | Must | 1.5/2.5/4 → 2.58 | GATE-G5·HA, A-P5-008·H | D15–D15 | Belum mulai |
| **A-P7-002** | Laporan kualitas data per run | A (R1) | Must | 1/1.5/2 → 1.5 | A-P7-001·H | D15–D15 | Belum mulai |
| **A-P7-003** | Rekonsiliasi NRT→SP manual (Should) | A (R1) | Should | 2/3/4 → 3.0 | A-P7-001·H | D17–D18 | Belum mulai |
| **B-P7-001** | Eksekusi eksperimen bucketing (Must) | B (R2) | Must | 2/3.5/5 → 3.5 | GATE-G5·HA, B-P3-004·H | D15–D15 | Belum mulai |
| **B-P7-002** | Laporan eksperimen | B (R2) | Must | 1.5/2.5/3.5 → 2.5 | B-P7-001·H | D15–D16 | Belum mulai |
| **B-P7-003** | Eksperimen replikasi/konsistensi/failure 3 node (Should) | B (R2) | Should | 3/4/6 → 4.17 | B-P4-002·H, B-P7-002·S, GATE-G5·HA | D21–D22 | Belum mulai |
| **C-P7-002** ⚑ | Provisioning cloud + deploy pertama | C (R3) | Must | 3/4/6 → 4.17 | GATE-G6·HA, C-P3-003·H | D15–D15 | Belum mulai |
| **C-P7-003** ⚑ | Poller di cloud + monitoring + restart | C (R3) | Must | 1.5/2.5/4 → 2.58 | C-P7-002·H, A-P5-007·H | D16–D16 | Belum mulai |
| **C-P7-004** ⚑ | Checklist keamanan + verifikasi | C (R3) | Must | 1.5/2/3 → 2.08 | C-P7-002·H | D15–D16 | Belum mulai |
| **D-P7-001** | E2E smoke test UI | D (R4) | Must | 2/3/4 → 3.0 | GATE-G6·HA | D15–D15 | Belum mulai |
| **D-P7-002** | Review terminologi ilmiah, disclaimer, aksesibilitas | D (R4) | Must | 1/1.5/2 → 1.5 | GATE-G6·HA | D15–D16 | Belum mulai |
| **A-P7-004** | Hardening & perbaikan bug data (time-box) | A (R1) | Must | 2/3/4 → 3.0 | A-P7-001·S, GATE-G6·HA | D17–D17 | Belum mulai |
| **B-P7-004** | Hardening & perbaikan bug DB (time-box) | B (R2) | Must | 2/3/4 → 3.0 | B-P7-002·S, GATE-G6·HA | D17–D17 | Belum mulai |
| **C-P7-005** ⚑ | Hardening & perbaikan bug API/deploy (time-box) | C (R3) | Must | 2/3/4 → 3.0 | C-P7-004·S, GATE-G6·HA | D17–D18 | Belum mulai |
| **D-P7-003** | Hardening & perbaikan bug UI (time-box) | D (R4) | Must | 2/3/4 → 3.0 | D-P7-001·S, GATE-G6·HA | D17–D17 | Belum mulai |
| **X-P7-901** | Feature freeze D17 | B (R2) | Must | 0.5/1/1.5 → 1.0 | C-P7-002·H, C-P7-003·H, D-P7-001·H, A-P7-001·H, B-P7-002·H, C-P7-001·H | D17–D17 | Belum mulai |
| **X-P7-902** ⚑ | Paket gerbang G7 | B (R2) | Must | 0.5/1/1.5 → 1.0 | X-P7-901·H, A-P7-004·H, B-P7-004·H, C-P7-005·H, D-P7-003·H, D-P7-002·H, A-P7-002·S | D18–D18 | Belum mulai |

⚑ = berada di rantai kritis.

### C-P7-001 — Skrip smoke E2E stack penuh

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** Satu perintah: up → ingest fixture → cek API → cek UI.
- **Alasan:** Regresi integrasi.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D16 (2026-12-04) – D17 (2026-12-05)
- **Input:** Stack
- **Dependensi:** GATE-G6 (Human approval)
- **Output:** deploy/scripts/smoke_e2e.*
- **File dimiliki:** `deploy/`
- **Langkah:** Skrip → Asersi jumlah → Dokumentasi
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** Skrip exit 0 di stack sehat dan ≠0 bila komponen mati.
- **Verifikasi otomatis:** Jalankan dengan service dimatikan sengaja
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'deploy/scripts/smoke_e2e.*' ke R2 untuk X-P7-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P7-001 — Uji idempotensi pada data nyata

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** Re-run backfill & poll tumpang tindih → jumlah & agregat identik.
- **Alasan:** Kriteria keberhasilan #2.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2.5 / P 4 → PERT 2.58 jam · **Rencana:** D15 (2026-12-03) – D15 (2026-12-03)
- **Input:** Cassandra berisi data
- **Dependensi:** GATE-G5 (Human approval); A-P5-008 (Hard)
- **Output:** Laporan idempotensi di pipeline/README.md
- **File dimiliki:** `pipeline/`
- **Langkah:** Snapshot jumlah → Re-run → Bandingkan
- **Spesifikasi teknis:** O-E1
- **Kriteria penerimaan:** Selisih 0 baris & 0 agregat.
- **Verifikasi otomatis:** Harness idempotensi
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'Laporan idempotensi di pipeline/README.md' ke R2 untuk X-P7-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P7-002 — Laporan kualitas data per run

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** Laporan DQ otomatis dari run log & rejected records.
- **Alasan:** Bukti engineering.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 1 / M 1.5 / P 2 → PERT 1.5 jam · **Rencana:** D15 (2026-12-03) – D15 (2026-12-03)
- **Input:** Run log
- **Dependensi:** A-P7-001 (Hard)
- **Output:** pipeline/src/.../reports/
- **File dimiliki:** `pipeline/`
- **Langkah:** Ringkasan per reason code → Ekspor markdown → Test
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** Laporan dihasilkan untuk run terakhir.
- **Verifikasi otomatis:** pytest
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'pipeline/src/.../reports/' ke R2 untuk X-P7-902. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P7-003 — Rekonsiliasi NRT→SP manual (Should)

- **Fase / prioritas / status:** P7 · Should · Belum mulai
- **Tujuan:** Perintah manual mengganti NRT dengan SP saat SP tersedia.
- **Alasan:** OQ-10 Should.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D17 (2026-12-05) – D18 (2026-12-06)
- **Input:** Aturan presedensi
- **Dependensi:** A-P7-001 (Hard)
- **Output:** pipeline/src/.../modes/reconcile.py
- **File dimiliki:** `pipeline/`
- **Langkah:** CLI → Uji pada tanggal tumpang tindih → Dokumentasi
- **Spesifikasi teknis:** A-P1-007
- **Kriteria penerimaan:** Jumlah per tanggal setelah rekonsiliasi = jumlah SP.
- **Verifikasi otomatis:** Test integrasi
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Operasi penghapusan NRT butuh persetujuan
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P7-001 — Eksekusi eksperimen bucketing (Must)

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** Menjalankan eksperimen sesuai rencana dan menyimpan data mentah hasil.
- **Alasan:** O-E3.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3.5 / P 5 → PERT 3.5 jam · **Rencana:** D15 (2026-12-03) – D15 (2026-12-03)
- **Input:** Rencana eksperimen
- **Dependensi:** GATE-G5 (Human approval); B-P3-004 (Hard)
- **Output:** experiments/bucketing/
- **File dimiliki:** `experiments/`
- **Langkah:** Siapkan varian skema di keyspace eksperimen → Jalankan dengan repetisi → Simpan hasil mentah
- **Spesifikasi teknis:** 05-experiment-plan.md
- **Kriteria penerimaan:** Hasil mentah + konfigurasi tersimpan dan dapat dijalankan ulang.
- **Verifikasi otomatis:** Skrip eksperimen exit 0; hasil ber-timestamp
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P7-002 — Laporan eksperimen

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** Hipotesis → hasil aktual → interpretasi → keterbatasan.
- **Alasan:** O-E3.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2.5 / P 3.5 → PERT 2.5 jam · **Rencana:** D15 (2026-12-03) – D16 (2026-12-04)
- **Input:** Hasil mentah
- **Dependensi:** B-P7-001 (Hard)
- **Output:** experiments/bucketing/REPORT.md
- **File dimiliki:** `experiments/`
- **Langkah:** Tabel/grafik dari hasil → Interpretasi → Keterbatasan
- **Spesifikasi teknis:** Tidak mengarang angka
- **Kriteria penerimaan:** Setiap angka dapat ditelusuri ke file hasil.
- **Verifikasi otomatis:** Review silang
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Kesimpulan analitis: tim
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P7-003 — Eksperimen replikasi/konsistensi/failure 3 node (Should)

- **Fase / prioritas / status:** P7 · Should · Belum mulai
- **Tujuan:** Mengamati perilaku RF/CL saat node mati.
- **Alasan:** OQ-14 Should.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 3 / M 4 / P 6 → PERT 4.17 jam · **Rencana:** D21 (2026-12-09) – D22 (2026-12-10)
- **Input:** Lingkungan 3 node
- **Dependensi:** B-P4-002 (Hard); B-P7-002 (Soft); GATE-G5 (Human approval)
- **Output:** experiments/replication/
- **File dimiliki:** `experiments/`
- **Langkah:** Skenario → Jalankan → Laporan
- **Spesifikasi teknis:** Dokumen 07
- **Kriteria penerimaan:** Laporan dengan hasil aktual atau alasan dibatalkan.
- **Verifikasi otomatis:** Log eksperimen
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P7-002 — Provisioning cloud + deploy pertama

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** VM tunggal, image yang sama dengan lokal, HTTPS, Cassandra di jaringan privat.
- **Alasan:** Fitur #11 Must.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 3 / M 4 / P 6 → PERT 4.17 jam · **Rencana:** D15 (2026-12-03) – D15 (2026-12-03)
- **Input:** Keputusan penyedia (HD-16)
- **Dependensi:** GATE-G6 (Human approval); C-P3-003 (Hard)
- **Output:** deploy/cloud/
- **File dimiliki:** `deploy/`
- **Langkah:** Provision → Deploy compose → HTTPS + firewall
- **Spesifikasi teknis:** ADR-003/004
- **Kriteria penerimaan:** Aplikasi dapat diakses via HTTPS; port Cassandra tertutup dari internet.
- **Verifikasi otomatis:** Port scan dari luar + curl HTTPS
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Persetujuan keamanan & biaya (tim)
- **Serah-terima:** Serahkan 'deploy/cloud/' ke R2 untuk X-P7-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P7-003 — Poller di cloud + monitoring + restart

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** Poller berjalan terus, status terlihat, restart otomatis.
- **Alasan:** Kriteria keberhasilan #7.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2.5 / P 4 → PERT 2.58 jam · **Rencana:** D16 (2026-12-04) – D16 (2026-12-04)
- **Input:** Mode incremental
- **Dependensi:** C-P7-002 (Hard); A-P5-007 (Hard)
- **Output:** deploy/cloud/ (service poller)
- **File dimiliki:** `deploy/`
- **Langkah:** Service poller → Restart policy → Alarm sederhana via halaman status
- **Spesifikasi teknis:** R-27
- **Kriteria penerimaan:** Poll baru tercatat ≥3× berturut-turut di cloud.
- **Verifikasi otomatis:** Endpoint status
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'deploy/cloud/ (service poller)' ke R2 untuk X-P7-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P7-004 — Checklist keamanan + verifikasi

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** Port, secret, CORS, rate limit, header.
- **Alasan:** R-25, OQ-26.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D15 (2026-12-03) – D16 (2026-12-04)
- **Input:** ADR-004
- **Dependensi:** C-P7-002 (Hard)
- **Output:** deploy/SECURITY-CHECKLIST.md
- **File dimiliki:** `deploy/`
- **Langkah:** Cek tiap kontrol → Bukti → Perbaikan
- **Spesifikasi teknis:** ADR-004
- **Kriteria penerimaan:** Semua kontrol Must lulus dengan bukti.
- **Verifikasi otomatis:** Port scan, cek header
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tim (keamanan)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P7-001 — E2E smoke test UI

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** Test otomatis alur utama di browser.
- **Alasan:** Regresi UI.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D15 (2026-12-03) – D15 (2026-12-03)
- **Input:** Stack lokal
- **Dependensi:** GATE-G6 (Human approval)
- **Output:** web/e2e/
- **File dimiliki:** `web/e2e/`
- **Langkah:** Alur ringkasan→ranking→peta → Filter → CI opsional
- **Spesifikasi teknis:** HD-14 (alat E2E)
- **Kriteria penerimaan:** Alur utama lulus pada stack lokal.
- **Verifikasi otomatis:** Runner E2E
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'web/e2e/' ke R2 untuk X-P7-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P7-002 — Review terminologi ilmiah, disclaimer, aksesibilitas

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** Memastikan tidak ada kata 'kebakaran' untuk deteksi; atribusi lengkap.
- **Alasan:** R-15.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 1 / M 1.5 / P 2 → PERT 1.5 jam · **Rencana:** D15 (2026-12-03) – D16 (2026-12-04)
- **Input:** UI
- **Dependensi:** GATE-G6 (Human approval)
- **Output:** Daftar perbaikan + perbaikan
- **File dimiliki:** `web/`
- **Langkah:** Grep teks UI → Cek atribusi → Perbaiki
- **Spesifikasi teknis:** Charter §3
- **Kriteria penerimaan:** 0 temuan terminologi terbuka.
- **Verifikasi otomatis:** Grep string UI
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Teks final: tim
- **Serah-terima:** Serahkan 'Daftar perbaikan + perbaikan' ke R2 untuk X-P7-902. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P7-004 — Hardening & perbaikan bug data (time-box)

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** Perbaikan bug setelah feature freeze.
- **Alasan:** Buffer terencana.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D17 (2026-12-05) – D17 (2026-12-05)
- **Input:** Daftar bug
- **Dependensi:** A-P7-001 (Soft); GATE-G6 (Human approval)
- **Output:** PR perbaikan
- **File dimiliki:** `pipeline/`
- **Langkah:** Triage → Perbaiki → Test regresi
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** 0 bug kritis terbuka di area data.
- **Verifikasi otomatis:** CI
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'PR perbaikan' ke R2 untuk X-P7-902. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P7-004 — Hardening & perbaikan bug DB (time-box)

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** Perbaikan bug setelah feature freeze.
- **Alasan:** Buffer terencana.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D17 (2026-12-05) – D17 (2026-12-05)
- **Input:** Daftar bug
- **Dependensi:** B-P7-002 (Soft); GATE-G6 (Human approval)
- **Output:** PR perbaikan
- **File dimiliki:** `db/`
- **Langkah:** Triage → Perbaiki → Test regresi
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** 0 bug kritis terbuka di area DB.
- **Verifikasi otomatis:** CI
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P7-005 — Hardening & perbaikan bug API/deploy (time-box)

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** Perbaikan bug setelah feature freeze.
- **Alasan:** Buffer terencana.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D17 (2026-12-05) – D18 (2026-12-06)
- **Input:** Daftar bug
- **Dependensi:** C-P7-004 (Soft); GATE-G6 (Human approval)
- **Output:** PR perbaikan
- **File dimiliki:** `api/, deploy/`
- **Langkah:** Triage → Perbaiki → Test regresi
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** 0 bug kritis terbuka di API/deploy.
- **Verifikasi otomatis:** CI
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'PR perbaikan' ke R2 untuk X-P7-902. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P7-003 — Hardening & perbaikan bug UI (time-box)

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** Perbaikan bug setelah feature freeze.
- **Alasan:** Buffer terencana.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D17 (2026-12-05) – D17 (2026-12-05)
- **Input:** Daftar bug
- **Dependensi:** D-P7-001 (Soft); GATE-G6 (Human approval)
- **Output:** PR perbaikan
- **File dimiliki:** `web/`
- **Langkah:** Triage → Perbaiki → Test regresi
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** 0 bug kritis terbuka di UI.
- **Verifikasi otomatis:** CI
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tidak
- **Serah-terima:** Serahkan 'PR perbaikan' ke R2 untuk X-P7-902. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### X-P7-901 — Feature freeze D17

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** Memastikan semua Must berjalan di cloud; setelah ini hanya perbaikan bug.
- **Alasan:** Charter §10; kontingensi R-23.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 0.5 / M 1 / P 1.5 → PERT 1.0 jam · **Rencana:** D17 (2026-12-05) – D17 (2026-12-05)
- **Input:** Status Fase 7
- **Dependensi:** C-P7-002 (Hard); C-P7-003 (Hard); D-P7-001 (Hard); A-P7-001 (Hard); B-P7-002 (Hard); C-P7-001 (Hard)
- **Output:** Keputusan freeze
- **File dimiliki:** `docs/STATUS.md`
- **Langkah:** Cek Must di cloud → Putuskan kontingensi → Umumkan freeze
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** Daftar Must di cloud: semua berjalan atau keputusan kontingensi tercatat.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tim
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Manusia

### X-P7-902 — Paket gerbang G7

- **Fase / prioritas / status:** P7 · Must · Belum mulai
- **Tujuan:** Mengumpulkan bukti test, eksperimen, deploy.
- **Alasan:** Gerbang ke Fase 8.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 0.5 / M 1 / P 1.5 → PERT 1.0 jam · **Rencana:** D18 (2026-12-06) – D18 (2026-12-06)
- **Input:** Bukti Fase 7
- **Dependensi:** X-P7-901 (Hard); A-P7-004 (Hard); B-P7-004 (Hard); C-P7-005 (Hard); D-P7-003 (Hard); D-P7-002 (Hard); A-P7-002 (Soft)
- **Output:** Keputusan G7
- **File dimiliki:** `docs/STATUS.md`
- **Langkah:** Kumpulkan bukti → Persetujuan
- **Spesifikasi teknis:** Checklist G7
- **Kriteria penerimaan:** Checklist G7 lengkap.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tim (G7)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Manusia + agen pencatat

## P8 — Documentation & Final Delivery

| ID | Judul | Pemilik | Prio | O/M/P → PERT (j) | Dependensi | Rencana | Status |
|---|---|---|---|---|---|---|---|
| **C-P8-001** | Panduan instalasi & reproduksibilitas + uji fresh clone | C (R3) | Must | 1.5/2/3 → 2.08 | GATE-G7·HA | D19–D19 | Belum mulai |
| **A-P8-001** | Dokumentasi teknis data (pipeline, DQ, keterbatasan) | A (R1) | Must | 1/1.5/2 → 1.5 | GATE-G7·HA | D19–D19 | Belum mulai |
| **B-P8-001** | Dokumentasi database + hasil eksperimen | B (R2) | Must | 1/1.5/2 → 1.5 | GATE-G7·HA | D19–D19 | Belum mulai |
| **C-P8-002** | Dokumentasi API, deployment, ADR final | C (R3) | Must | 1/1.5/2 → 1.5 | GATE-G7·HA | D19–D19 | Belum mulai |
| **D-P8-001** ⚑ | Dokumentasi UI + skrip demo + screenshot | D (R4) | Must | 1.5/2/3 → 2.08 | GATE-G7·HA | D19–D19 | Belum mulai |
| **D-P8-002** ⚑ | Checklist penerimaan final + indeks dokumentasi | D (R4) | Must | 1/1.5/2 → 1.5 | C-P8-001·H, A-P8-001·H, B-P8-001·H, C-P8-002·H, D-P8-001·H | D20–D20 | Belum mulai |
| **X-P8-901** | Perakitan laporan proyek (manusia) | B (R2) | Must | 2/3/4 → 3.0 | A-P8-001·S, B-P8-001·S, C-P8-002·S, D-P8-001·S, GATE-G7·HA | D19–D20 | Belum mulai |
| **A-P8-002** | Perakitan presentasi ≤20 menit (manusia) | A (R1) | Must | 2/3/4 → 3.0 | D-P8-001·S, GATE-G6·HA | D15–D16 | Belum mulai |
| **D-P8-003** ⚑ | Rekam video demo (manusia) | D (R4) | Must | 1.5/2.5/3.5 → 2.5 | D-P8-001·H | D19–D20 | Belum mulai |
| **X-P8-902** ⚑ | Gerbang G8 — penerimaan akhir | B (R2) | Must | 0.5/1/1.5 → 1.0 | D-P8-002·H, X-P8-901·S, A-P8-002·S, D-P8-003·S | D20–D20 | Belum mulai |

⚑ = berada di rantai kritis.

### C-P8-001 — Panduan instalasi & reproduksibilitas + uji fresh clone

- **Fase / prioritas / status:** P8 · Must · Belum mulai
- **Tujuan:** README root lengkap; anggota lain menjalankan dari nol.
- **Alasan:** O-E4, kriteria #8.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D19 (2026-12-07) – D19 (2026-12-07)
- **Input:** Seluruh repo
- **Dependensi:** GATE-G7 (Human approval)
- **Output:** README.md, docs/08-delivery/api-deploy.md
- **File dimiliki:** `README.md`
- **Langkah:** Tulis panduan → Anggota lain menjalankan dari clone bersih → Perbaiki
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** Fresh clone → dashboard berjalan tanpa bantuan.
- **Verifikasi otomatis:** Log fresh clone oleh anggota lain
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G8
- **Serah-terima:** Serahkan 'README.md, docs/08-delivery/api-deploy.md' ke R4 untuk D-P8-002. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### A-P8-001 — Dokumentasi teknis data (pipeline, DQ, keterbatasan)

- **Fase / prioritas / status:** P8 · Must · Belum mulai
- **Tujuan:** Bab data untuk laporan tim.
- **Alasan:** Kriteria #8.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 1 / M 1.5 / P 2 → PERT 1.5 jam · **Rencana:** D19 (2026-12-07) – D19 (2026-12-07)
- **Input:** docs/01-dataset, 03-specs/data, pipeline/
- **Dependensi:** GATE-G7 (Human approval)
- **Output:** docs/08-delivery/data.md
- **File dimiliki:** `docs/08-delivery/data.md`
- **Langkah:** Ringkas → Diagram → Keterbatasan
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** Setiap klaim tertaut ke bukti.
- **Verifikasi otomatis:** Cek tautan
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G8
- **Serah-terima:** Serahkan 'docs/08-delivery/data.md' ke R2, R4 untuk D-P8-002, X-P8-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### B-P8-001 — Dokumentasi database + hasil eksperimen

- **Fase / prioritas / status:** P8 · Must · Belum mulai
- **Tujuan:** Bab database & eksperimen.
- **Alasan:** Kriteria #8.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 1 / M 1.5 / P 2 → PERT 1.5 jam · **Rencana:** D19 (2026-12-07) – D19 (2026-12-07)
- **Input:** db/, experiments/
- **Dependensi:** GATE-G7 (Human approval)
- **Output:** docs/08-delivery/database.md
- **File dimiliki:** `docs/08-delivery/database.md`
- **Langkah:** Model → Eksperimen → Keterbatasan
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** Angka eksperimen = file hasil.
- **Verifikasi otomatis:** Cek tautan
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G8
- **Serah-terima:** Serahkan 'docs/08-delivery/database.md' ke R4 untuk D-P8-002. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### C-P8-002 — Dokumentasi API, deployment, ADR final

- **Fase / prioritas / status:** P8 · Must · Belum mulai
- **Tujuan:** Bab API & deployment.
- **Alasan:** Kriteria #8.
- **Pemilik (A) & pelaksana (R):** Role C (R3) · **Kolaborator (C):** —
- **Estimasi:** O 1 / M 1.5 / P 2 → PERT 1.5 jam · **Rencana:** D19 (2026-12-07) – D19 (2026-12-07)
- **Input:** api/, deploy/, ADR
- **Dependensi:** GATE-G7 (Human approval)
- **Output:** docs/08-delivery/api-deploy.md
- **File dimiliki:** `docs/08-delivery/api-deploy.md`
- **Langkah:** API → Deploy → Keamanan
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** Tidak ada secret di dokumen.
- **Verifikasi otomatis:** Grep pola secret
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G8
- **Serah-terima:** Serahkan 'docs/08-delivery/api-deploy.md' ke R2, R4 untuk D-P8-002, X-P8-901. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P8-001 — Dokumentasi UI + skrip demo + screenshot

- **Fase / prioritas / status:** P8 · Must · Belum mulai
- **Tujuan:** Bab UI dan skrip demo untuk video.
- **Alasan:** Bahan video & presentasi.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2 / P 3 → PERT 2.08 jam · **Rencana:** D19 (2026-12-07) – D19 (2026-12-07)
- **Input:** Aplikasi di cloud
- **Dependensi:** GATE-G7 (Human approval)
- **Output:** docs/08-delivery/ui.md, docs/08-delivery/demo-script.md
- **File dimiliki:** `docs/08-delivery/`
- **Langkah:** Screenshot → Skrip demo per fitur → Catatan disclaimer
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** Skrip demo ≤ durasi video yang disepakati.
- **Verifikasi otomatis:** Uji baca skrip
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G8
- **Serah-terima:** Serahkan 'docs/08-delivery/ui.md, docs/08-delivery/demo-script.md' ke R1, R2 untuk X-P8-901, A-P8-002. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### D-P8-002 — Checklist penerimaan final + indeks dokumentasi

- **Fase / prioritas / status:** P8 · Must · Belum mulai
- **Tujuan:** Mencentang 8 kriteria keberhasilan dengan bukti dan menyusun indeks dokumentasi.
- **Alasan:** G8.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 1 / M 1.5 / P 2 → PERT 1.5 jam · **Rencana:** D20 (2026-12-08) – D20 (2026-12-08)
- **Input:** Semua dokumen Fase 8
- **Dependensi:** C-P8-001 (Hard); A-P8-001 (Hard); B-P8-001 (Hard); C-P8-002 (Hard); D-P8-001 (Hard)
- **Output:** docs/08-delivery/index.md, docs/08-delivery/acceptance-checklist.md
- **File dimiliki:** `docs/08-delivery/`
- **Langkah:** Checklist → Indeks → Daftar keterbatasan
- **Spesifikasi teknis:** Charter §7
- **Kriteria penerimaan:** Setiap kriteria punya bukti tertaut.
- **Verifikasi otomatis:** Cek tautan
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** G8
- **Serah-terima:** Serahkan 'docs/08-delivery/index.md, docs/08-delivery/acceptance-checklist.md' ke R2 untuk X-P8-902. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Claude Code implementasi; Codex review

### X-P8-901 — Perakitan laporan proyek (manusia)

- **Fase / prioritas / status:** P8 · Must · Belum mulai
- **Tujuan:** Merakit laporan dari bab tiap peran.
- **Alasan:** Deliverable 1; ditangani tim (OQ-01, A-23).
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D19 (2026-12-07) – D20 (2026-12-08)
- **Input:** docs/08-delivery/
- **Dependensi:** A-P8-001 (Soft); B-P8-001 (Soft); C-P8-002 (Soft); D-P8-001 (Soft); GATE-G7 (Human approval)
- **Output:** Laporan (di luar repo atau sesuai tim)
- **File dimiliki:** `— (di luar ruang agen)`
- **Langkah:** Kerangka laporan → Tempel & sunting bab → Proofread
- **Spesifikasi teknis:** Format dari dosen (UNKNOWN)
- **Kriteria penerimaan:** Disetujui tim.
- **Verifikasi otomatis:** Review tim
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tim
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Manusia saja

### A-P8-002 — Perakitan presentasi ≤20 menit (manusia)

- **Fase / prioritas / status:** P8 · Must · Belum mulai
- **Tujuan:** Slide; tiap peran menyumbang 1–2 slide.
- **Alasan:** Deliverable 2.
- **Pemilik (A) & pelaksana (R):** Role A (R1) · **Kolaborator (C):** —
- **Estimasi:** O 2 / M 3 / P 4 → PERT 3.0 jam · **Rencana:** D15 (2026-12-03) – D16 (2026-12-04)
- **Input:** Bab teknis, skrip demo
- **Dependensi:** D-P8-001 (Soft); GATE-G6 (Human approval)
- **Output:** Presentasi
- **File dimiliki:** `— (di luar ruang agen)`
- **Langkah:** Alur cerita → Slide per peran → Latihan berwaktu
- **Spesifikasi teknis:** ≤20 menit
- **Kriteria penerimaan:** Latihan berwaktu ≤20 menit.
- **Verifikasi otomatis:** Latihan
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tim
- **Serah-terima:** Serahkan 'Presentasi' ke R2 untuk X-P8-902. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Manusia saja

### D-P8-003 — Rekam video demo (manusia)

- **Fase / prioritas / status:** P8 · Must · Belum mulai
- **Tujuan:** Merekam demo mengikuti skrip.
- **Alasan:** Deliverable 4.
- **Pemilik (A) & pelaksana (R):** Role D (R4) · **Kolaborator (C):** —
- **Estimasi:** O 1.5 / M 2.5 / P 3.5 → PERT 2.5 jam · **Rencana:** D19 (2026-12-07) – D20 (2026-12-08)
- **Input:** Skrip demo, aplikasi cloud
- **Dependensi:** D-P8-001 (Hard)
- **Output:** Video demo
- **File dimiliki:** `— (di luar ruang agen)`
- **Langkah:** Rekam → Sunting → Cek disclaimer tampil
- **Spesifikasi teknis:** —
- **Kriteria penerimaan:** Semua fitur Must terlihat; disclaimer terlihat.
- **Verifikasi otomatis:** Tonton ulang tim
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tim
- **Serah-terima:** Serahkan 'Video demo' ke R2 untuk X-P8-902. Diterima saat seorang manusia mengisi `disetujui:` di 13-progress-tracker.md (review peran lain tidak wajib).
- **Mode agen:** Manusia saja

### X-P8-902 — Gerbang G8 — penerimaan akhir

- **Fase / prioritas / status:** P8 · Must · Belum mulai
- **Tujuan:** Persetujuan akhir.
- **Alasan:** Penutupan proyek.
- **Pemilik (A) & pelaksana (R):** Role B (R2) · **Kolaborator (C):** —
- **Estimasi:** O 0.5 / M 1 / P 1.5 → PERT 1.0 jam · **Rencana:** D20 (2026-12-08) – D20 (2026-12-08)
- **Input:** Checklist
- **Dependensi:** D-P8-002 (Hard); X-P8-901 (Soft); A-P8-002 (Soft); D-P8-003 (Soft)
- **Output:** Keputusan G8; STATUS final
- **File dimiliki:** `docs/STATUS.md`
- **Langkah:** Review checklist → Persetujuan
- **Spesifikasi teknis:** Checklist G8
- **Kriteria penerimaan:** Checklist G8 lengkap.
- **Verifikasi otomatis:** Review manual
- **Bukti test:** Output verifikasi di PR
- **Persetujuan manusia:** Tim (G8)
- **Serah-terima:** Tidak ada serah-terima lintas peran (konsumen internal peran sendiri).
- **Mode agen:** Manusia
