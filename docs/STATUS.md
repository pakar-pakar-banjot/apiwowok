# NusaFire — Status & Konteks Proyek

> **Titik masuk** untuk anggota tim dan agen AI (Claude Code, Codex). Baca file ini lebih dulu di setiap sesi baru. Kewajiban ini juga tertulis di [`AGENTS.md`](../AGENTS.md) dan [`CLAUDE.md`](../CLAUDE.md).
> File ini adalah **ringkasan dan penunjuk**. Sumber kebenaran tetap dokumen yang dirujuk. Jika ada konflik, dokumen yang dirujuk yang berlaku, dan file ini wajib diperbaiki.
> Diperbarui setiap kali melewati gerbang fase atau ada keputusan baru.

Terakhir diperbarui: **2026-11-22** (setelah G1).

## 1. Posisi saat ini

| Item | Nilai |
|---|---|
| Fase aktif | **Fase 2 — Requirements & semantik data** (mulai 2026-11-22, setelah G1). Syarat masuk G2: D-P2-001…003, C-P2-001, A-P2-001, B-P2-001. Fase 1 ditutup: [laporan Fase 1](01-dataset/README.md). C-P1-001 (toolchain & cloud) belum dikerjakan; bukan syarat G1. |
| Gerbang terakhir | **G1 (dataset feasibility) disetujui 2026-11-22** (4/4); sebelumnya GATE-EP dan G0 disetujui 2026-11-19 |
| Kalender kerja | D1 = 2026-11-19 … D21 = 2026-12-09 (asumsi A-22; presentasi diasumsikan 2026-12-10, HD-23). Jadwal yang berlaku: [05-project-schedule](10-execution-plan/05-project-schedule.md) (CR-04): G1 D3 · G2 D7 · G3/G4 D8 · G5/G6 D14 · freeze D17 · G7 D18 · G8 D20 |
| Tim | R1/A **Lanang** (Data/ETL) · R2/B **Abi Funn** (Cassandra + **koordinator**) · R3/C **Zita** (Backend & DevOps) · R4/D **Abigail** (Frontend & Delivery). 4 jam/hari; R1 & R3 ±5 jam/hari pada D9–D15 ([01-role-charters](10-execution-plan/01-role-charters.md)) |
| Repo | `github.com/pakar-pakar-banjot/apiwowok`; Fase 0 dan awal Fase 1 di `main`; rencana eksekusi + hasil Fase 1 + G1 di PR #1 (`docs/execution-plan`, belum di-merge) |
| Kode aplikasi | Belum ada |

## 1a. Rencana eksekusi & progres

- **Rencana kerja tim:** [docs/10-execution-plan/](10-execution-plan/00-execution-plan-overview.md). Berisi 110 tugas dengan pemilik, dependensi, jadwal, kontrak antarmuka, kepemilikan file, dan prompt agen per peran ([11-role-prompts/](10-execution-plan/11-role-prompts/)).
- **Progres:** [13-progress-tracker.md](10-execution-plan/13-progress-tracker.md). Implementer mencentang task ID-nya dan mengisi `bukti:`; seorang manusia (anggota tim mana pun) mengisi `disetujui:`. Review peran lain tidak wajib.
- **Cek tugas (manusia & agen):** `python -I docs/10-execution-plan/tools/task.py brief --role <A|B|C|D>` (apa yang siap/terblokir), `check <ID>` (kartu tugas + dependensi dari graf), `scope <ID>` (file yang diubah). Status juga tampil sebagai ikon di [graf dependensi](10-execution-plan/04-dependency-graph.mmd). Protokol agen: [AGENTS.md](../AGENTS.md).
- **Keputusan tim:** [12-human-decision-register.md](10-execution-plan/12-human-decision-register.md) · **Change request:** [docs/change-requests/](change-requests/).

## 2. Aturan kerja (wajib)

Diringkas dari brief tim; brief lengkap disimpan tim di luar repo.

1. **Phase-gated.** Kerjakan hanya fase yang diminta. Di akhir setiap fase: STOP dan tunggu persetujuan manusia.
2. **Spec-driven.** Tidak ada implementasi sebelum spesifikasi yang relevan disetujui. Skema Cassandra baru difinalkan setelah access patterns disetujui (Fase 3).
3. **Evidence-based.** Jangan mengarang atribut, statistik, kapabilitas API, atau hasil benchmark/test. Gunakan label `VERIFIED` / `USER` / `AI-PRIOR` / `ASSUMPTION` / `RECOMMENDATION` / `PENDING` / `UNKNOWN` ([legenda](00-discovery/README.md#label-status-informasi)).
4. **Keputusan yang wajib disetujui manusia:** ruang lingkup, cakupan geografis, produk satelit, periode, zona waktu, kebijakan kualitas data, fitur, skema, strategi partisi, perubahan arsitektur, perubahan keamanan, operasi destruktif, kesimpulan analitis.
5. **Cassandra:** query-driven modeling, tanpa `ALLOW FILTERING`/full scan di jalur aplikasi, prepared statements, ingestion idempoten, dan **tanpa counter table untuk agregat**.
6. **Integritas ilmiah:** hotspot ≠ kebakaran terkonfirmasi. Jangan membandingkan jumlah deteksi antar sensor.
7. **Bahasa:** dokumentasi dalam bahasa Indonesia; identifier kode, path API, dan konvensi teknis dalam bahasa Inggris.
8. **Git:** commit/push hanya bila diminta. Jangan pernah commit `.env`.
9. **Format laporan per fase:** 12 bagian (lihat [00-discovery/README.md](00-discovery/README.md#laporan-fase-0-format-12-bagian)).
10. Laporan akhir, presentasi, dan video **ditangani tim**, bukan agen.

## 3. Keputusan yang sudah disetujui (ringkasan)

Sumber kebenaran: [04-open-questions-register.md](00-discovery/04-open-questions-register.md) dan [01-project-charter.md](00-discovery/01-project-charter.md).

| Topik | Keputusan | Ref |
|---|---|---|
| Rubrik | Tidak ada rubrik; Cassandra wajib; fokus produk jadi + implementasi teknis | OQ-01 |
| Sumber data | **NASA FIRMS** (pull). NOAA NODD + SNS (push) = *Could* setelah D13. Pipeline memakai antarmuka *source adapter*. | OQ-28, [08](00-discovery/08-data-source-alternatives.md) |
| Produk satelit | **VIIRS 375 m NOAA-20 (utama) + NOAA-21 (kedua)**. S-NPP sudah berhenti; MODIS tidak dipakai. | OQ-04 |
| Mode ingestion | **Satu pipeline, dua mode, keduanya Must:** backfill (arsip SP) + incremental (polling NRT micro-batch). **Interval polling 15 menit** (Lanang/R1, 2026-11-21; angka NFR final di C-P2-001). Tanpa Kafka/Airflow. Penggantian NRT oleh SP = *Should*. | OQ-10 |
| Periode | **2023-01-01 sampai sekarang**, NOAA-20 + NOAA-21 (NOAA-21 mulai 2023-03-01). SP sampai akhir ketersediaan SP, NRT sesudahnya. | OQ-05, HD-09 (G1) |
| Cakupan | Seluruh Indonesia, tingkat provinsi (kabupaten = *Could*) | OQ-06 |
| Batas wilayah | **BIG `BATAS_KABKOTA_AR` edisi Juni 2026** (38 provinsi), snapshot tergeneralisasi 0,001° + checksum. Lisensi `UNKNOWN`: konfirmasi ke BIG sebelum hosting publik; cadangan **B5** (38 provinsi, dievaluasi dulu) | OQ-07, A-20, HD-08 (G1) |
| Tumpang tindih NRT/SP | Satu produk per (satelit, tanggal UTC): SP bila tersedia, NRT sesudahnya; penggantian NRT→SP per tanggal, bukan per deteksi | HD-10 (G1) |
| Kualitas data | DQ-01 … DQ-15: tolak hanya yang rusak, sisanya diberi flag. Tipe non-vegetasi dihitung semua + filter opsional (periode SP); tanpa snapping titik tepi | HD-11 (G1), [06](01-dataset/06-data-quality-rules.md) |
| Zona waktu | Simpan UTC; tanggal agregasi/tampilan per zona waktu provinsi (WIB/WITA/WIT) | OQ-08 |
| Confidence | Simpan semua; default tampilan diputuskan di Fase 2 | OQ-09 |
| Titik di luar provinsi | Simpan dengan status wilayah khusus; keluarkan dari ranking; laporkan jumlahnya | OQ-11 |
| Sumber statis | Pakai field `type` bila ada; jika tidak ada, nyatakan sebagai keterbatasan | OQ-12 |
| Eksperimen | Bucketing partisi = Must; replikasi/failure 3 node = Should (boleh di laptop sesuai [07](00-discovery/07-three-node-laptop-spec.md)) | OQ-13, OQ-14 |
| Hosting | Lokal dulu, lalu cloud (Must setelah integrasi lokal D13) | OQ-21 |
| MVP | 6 kapabilitas + hosting (#11) + ingestion NRT (#12) | [charter §6](00-discovery/01-project-charter.md#6-ruang-lingkup-awal-dan-mvp) |

## 4. Fakta terverifikasi penting (2026-11-19)

| Fakta | Sumber |
|---|---|
| Suomi NPP berhenti 2026-11-02; arsip historis tetap tersedia. Terra berhenti 2026-12-01. | Earthdata alerts / blog FIRMS |
| Ketersediaan FIRMS: **NOAA-20 SP 2018-04-01..2026-07-31, NRT 2026-08-01..2026-11-18; NOAA-21 SP 2023-03-01..2026-07-31, NRT 2024-01-17..2026-11-19.** NOAA-21 punya periode tumpang tindih NRT/SP. | `data_availability` API (diuji dengan MAP_KEY tim) |
| NRT digantikan SP dengan jeda ±5 bulan | FIRMS Archive Download |
| Area API: `/api/area/csv/{KEY}/{SOURCE}/{W,S,E,N}/{DAY_RANGE 1-5}[/{YYYY-MM-DD}]` | FIRMS API |
| Kuota 5000 transaksi / 10 menit; Country API "currently not available" | FIRMS API |
| WFS FIRMS: region `SouthEast_Asia`, jendela 24 jam/7 hari, output CSV, diperbarui tiap 15 menit | FIRMS WFS info |
| Latensi NRT VIIRS < 3 jam (global); terukur untuk Indonesia: 1,8 sampai ±9 jam (2 hari, Fase 1) | FIRMS FAQ; [04 §3](01-dataset/04-nrt-vs-sp-and-latency.md#3-latensi-nrt-a-p1-008) |

Detail lengkap dan tautan sumber: [08 §7](00-discovery/08-data-source-alternatives.md#7-sumber-yang-dibaca), [03-assumptions-register.md](00-discovery/03-assumptions-register.md).

## 5. Rahasia & lingkungan lokal

- MAP_KEY FIRMS ada di **`.env`** (variabel `FIRMS_MAP_KEY`), sudah diabaikan Git. Template: `.env.example`.
- **Jangan** mencetak, men-commit, atau menyalin key ke dokumen, log, atau URL yang dibagikan.
- Data mentah lokal disimpan di `data/` (diabaikan Git).

## 6. Hal yang masih terbuka

| Item | Kapan |
|---|---|
| Tindak lanjut HD-08: konfirmasi lisensi BIG (siapa yang menghubungi BIG belum ditetapkan); evaluasi B5 bila BIG tidak memadai | Sebelum hosting publik (OQ-21) |
| OQ-23–OQ-27 (cloud: penyedia, Cassandra di cloud, lokasi poller, keamanan, alur kerja tanpa Docker) | Fase 3–4 / ≤ D12 |
| NA-05 repo privat; NA-06 ritme komunikasi; NA-07 opsi cloud | Tim |
| Keputusan G2–G4: HD-12–HD-21 | [12](10-execution-plan/12-human-decision-register.md) |

## 7. Rencana Fase 1 (Dataset Feasibility)

**Status: selesai, G1 disetujui 2026-11-22.**

Rincian tugas: [06-next-actions.md §2](00-discovery/06-next-actions.md#2-persiapan-fase-1-dapat-dimulai-setelah-gerbang-g0) (P1-01…P1-11).

Keluaran wajib (dari brief):
- Source inventory
- Data dictionary (dari data nyata)
- Profiling dataset, analisis missing value, analisis duplikat
- Cakupan geografis & temporal
- Kompatibilitas field (NOAA-20 vs NOAA-21, NRT vs SP)
- Aturan kualitas data awal
- Rekomendasi dataset (periode final, sumber batas provinsi)

Batasan Fase 1:
- Tidak ada kode aplikasi, skema Cassandra, atau Docker Compose.
- Skrip profiling sekali pakai boleh dibuat; data mentah ke `data/` (tidak di-commit).
- Dependensi proyek resmi baru ditetapkan di Fase 4.
- Bounding box ekstraksi harus dipotong ke batas Indonesia (negara tetangga ikut terunduh).

## 8. Riwayat gerbang & keputusan besar

| Tanggal | Peristiwa |
|---|---|
| 2026-11-19 | Fase 0 disusun; jawaban open questions diterima; NRT dinaikkan ke Must (dua mode); kajian sumber data selesai; S-NPP diganti NOAA-20/21; MAP_KEY teruji; **G0 disetujui**. |
| 2026-11-19 | Fase 1 dimulai (inventaris sumber, evaluasi batas, unduhan sampel; di `main` `9214337`). Rencana eksekusi disusun; **GATE-EP disetujui**: semua rekomendasi HD-01–07 dan HD-22–24 diterima, termasuk anggota↔peran, koordinator R2, mekanisme gerbang 3/4 + pemilik area, dan HD-07(b). CR-01, CR-02, CR-04 disetujui. |
| 2026-11-19 | **HD-06 diganti:** tidak ada review wajib antar peran; tugas selesai saat seorang manusia mengisi `disetujui:`, dan dependensi Hard hanya butuh persetujuan itu. Protokol agen wajib di [AGENTS.md](../AGENTS.md) + `tools/task.py` (cek tugas dari graf dependensi). |
| 2026-11-22 | **G1 disetujui** (4/4: Lanang, Abi Funn, Zita, Abigail; suara Zita & Abigail disampaikan Lanang). Keputusan: periode 2023-01-01 sampai sekarang (HD-09); NOAA-20 + NOAA-21, SP lalu NRT; tumpang tindih per (satelit, tanggal UTC) (HD-10); batas BIG Juni 2026, cadangan B5, lisensi masih dikonfirmasi (HD-08); DQ-01 … DQ-15 (HD-11); polling 15 menit (R1); [CR-03](change-requests/CR-03.md) diterapkan ke register asumsi. X-P1-902 didelegasikan Abi Funn ke Lanang. |
