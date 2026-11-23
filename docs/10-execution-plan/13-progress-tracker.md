# 13 — Progress Tracker

> Catatan progres **hidup** untuk setiap task ID di [WBS](02-work-breakdown-structure.md) dan setiap gerbang.
> Kolom `status` di WBS adalah potret saat rencana disusun (D1); untuk progres, file ini yang berlaku.
> Struktur dibuat oleh `tools/build_plan.py`. Setiap run hanya memperbarui blok **Ringkasan** dan memeriksa
> konsistensi; centang dan isian di baris tugas tidak pernah ditimpa.

## Cara memakai

| Tanda | Arti | Siapa yang mengisi |
|---|---|---|
| `- [x]` | Pekerjaan implementer selesai: kriteria penerimaan terpenuhi, bukti ada, PR dibuka (DoD 1–4) | Implementer (agen atau manusia), **di PR tugas itu sendiri** |
| `bukti: …` | Link PR / hash commit / path artefak + tanggal, mis. `PR #12, 2026-11-21` | Implementer |
| `disetujui: …` | Seorang manusia menyetujui → tugas **Done** (DoD lengkap), mis. `Lanang, 2026-11-22`. Review/persetujuan peran lain tidak wajib. | **Hanya manusia** (anggota tim mana pun) |

Aturan:
1. Ubah **hanya baris tugasmu sendiri**. Jangan mengubah teks judul, ID, urutan, atau baris peran lain.
2. Agen **tidak pernah** menyetujui sendiri dan tidak mencentang tugas *manusia saja*. Agen hanya boleh mengisi `disetujui:` untuk mencatat persetujuan yang dinyatakan langsung oleh manusia, dengan menyebut siapa, kapan, dan di mana.
3. Baris gerbang: `[x]` = paket gerbang siap (koordinator); `disetujui:` = keputusan tim + tautan ke STATUS.md.
4. Bila PR ditolak dan pekerjaan dibuka kembali, hapus centang dan tulis alasannya di `bukti:`.
5. Konflik merge di file ini: pertahankan kedua perubahan (setiap baris milik satu tugas).
6. Setelah mengubah file ini, jalankan `python -I docs/10-execution-plan/tools/build_plan.py` (harus `ISSUES: 0`).

## Ringkasan

<!-- progress:summary:start -->
Format sel: **disetujui (Done) / dicentang / total**. Diperbarui otomatis oleh `tools/build_plan.py`.

| Bagian | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | Semua |
|---|---|---|---|---|---|---|---|---|---|
| Role A (R1) | 10 / 10 / 10 | 1 / 1 / 1 | 0 / 0 / 2 | 0 / 0 / 2 | 0 / 0 / 10 | · | 0 / 0 / 4 | 0 / 0 / 2 | **11 / 11 / 31** |
| Role B (R2) | 1 / 1 / 1 | 0 / 0 / 1 | 0 / 0 / 4 | 0 / 0 / 2 | 0 / 0 / 7 | · | 0 / 0 / 4 | 0 / 0 / 1 | **1 / 1 / 20** |
| Role C (R3) | 0 / 0 / 1 | 0 / 0 / 1 | 0 / 0 / 3 | 0 / 0 / 3 | · | 0 / 0 / 10 | 0 / 0 / 5 | 0 / 0 / 2 | **0 / 0 / 25** |
| Role D (R4) | 0 / 1 / 1 | 0 / 0 / 3 | 0 / 0 / 1 | 0 / 0 / 3 | · | 0 / 0 / 9 | 0 / 0 / 3 | 0 / 0 / 3 | **0 / 1 / 23** |
| Koordinator integrasi (tugas X-) | 2 / 2 / 2 | 0 / 0 / 1 | 0 / 0 / 1 | 0 / 0 / 1 | 0 / 0 / 1 | 0 / 0 / 1 | 0 / 0 / 2 | 0 / 0 / 2 | **2 / 2 / 11** |
| **Tim** | 13 / 14 / 15 | 1 / 1 / 7 | 0 / 0 / 11 | 0 / 0 / 11 | 0 / 0 / 18 | 0 / 0 / 20 | 0 / 0 / 18 | 0 / 0 / 10 | **14 / 15 / 110** |

Gerbang disetujui: GATE-EP, GATE-G1.
Menunggu persetujuan manusia: D-P1-001.
<!-- progress:summary:end -->

## Gerbang

- [x] **GATE-EP** Persetujuan rencana eksekusi (dokumen ini) + penetapan anggota/peran · bukti: rencana `docs/10-execution-plan/` + keputusan [12](12-human-decision-register.md), 2026-11-19 · disetujui: tim (semua rekomendasi HD-01–07, HD-22–24), 2026-11-19, disampaikan di sesi Claude Code; dicatat di STATUS.md §8
- [x] **GATE-G1** G1 — dataset, periode (OQ-05), batas provinsi (OQ-07), aturan NRT/SP, aturan DQ · bukti: paket G1 docs/01-dataset/07-dataset-recommendation.md; keputusan di 12 (HD-08…HD-11) + STATUS §3/§8; CR-03 diterapkan · disetujui: tim 4/4 (Lanang, Abi Funn, Zita, Abigail), 2026-11-22; suara Zita & Abigail disampaikan Lanang di sesi Claude Code
- [ ] **GATE-G2** G2 — requirements, NFR, semantik data, MVP terkunci · bukti: — · disetujui: —
- [ ] **GATE-G3** G3 — kontrak canonical event, access patterns, model data, OpenAPI, UI spec, ADR · bukti: — · disetujui: —
- [ ] **GATE-G4** G4 — harness: repo, AGENTS.md, Compose, CI hijau · bukti: — · disetujui: —
- [ ] **GATE-G5** G5 — ETL dua mode + Cassandra berisi data nyata, test DB & ETL lulus · bukti: — · disetujui: —
- [ ] **GATE-G6** G6 — API + dashboard berjalan di data nyata secara lokal (integrasi lokal pertama) · bukti: — · disetujui: —
- [ ] **GATE-G7** G7 — test, idempotensi, eksperimen, deploy cloud, feature freeze dipatuhi · bukti: — · disetujui: —
- [ ] **GATE-G8** G8 — dokumentasi teknis final, checklist penerimaan · bukti: — · disetujui: —

## Role A (R1)

### P1 — Dataset Feasibility

- [x] **A-P1-001** Review inventaris sumber FIRMS · R1 · bukti: review R1 (Lanang) 2026-11-21: klaim API dicoba ulang lewat Postman; dokumen docs/01-dataset/01-source-inventory.md · disetujui: Lanang (R1), 2026-11-21, sesi Claude Code
- [x] **A-P1-002** Unduh sampel nyata + checksum · R1 · bukti: skrip di main 9214337; 629/629 file cocok SHA-256 manifest, semua HTTP 200, 0 MAP_KEY di log (2026-11-19) · disetujui: Lanang (R1), 2026-11-21, sesi Claude Code
- [x] **A-P1-003** Data dictionary dari header & nilai nyata · R1 · bukti: draf agen, PR #1 (2026-11-19): docs/01-dataset/02-data-dictionary.md; menunggu review · disetujui: Lanang (R1), 2026-11-21, sesi Claude Code
- [x] **A-P1-004** Laporan profiling dataset · R1 · bukti: draf agen, PR #1 (2026-11-19): docs/01-dataset/03-profiling-report.md + scratch/phase1/extra_checks.py; menunggu review · disetujui: Lanang (R1), 2026-11-21, sesi Claude Code
- [x] **A-P1-005** Verifikasi asumsi AI-PRIOR A-06–A-09 · R1 · bukti: draf agen, PR #1 (2026-11-19): 02-data-dictionary §5 + docs/change-requests/CR-03.md; menunggu review · disetujui: Lanang (R1), 2026-11-21, sesi Claude Code
- [x] **A-P1-006** Review evaluasi sumber batas provinsi · R1 · bukti: review R1 (Lanang) 2026-11-21: docs/01-dataset/05-boundary-sources.md; cadangan lisensi diubah ke B5 · disetujui: Lanang (R1), 2026-11-21, sesi Claude Code; dengan perubahan: cadangan lisensi → B5 (38 provinsi)
- [x] **A-P1-007** Perbandingan NRT vs SP + aturan tumpang tindih · R1 · bukti: draf agen, PR #1 (2026-11-19): docs/01-dataset/04-nrt-vs-sp-and-latency.md §1–§2; menunggu review · disetujui: Lanang (R1), 2026-11-21, sesi Claude Code
- [x] **A-P1-008** Pengamatan latensi NRT · R1 · bukti: PR #1 (2026-11-20): poller 2026-11-19 09:09 … 2026-11-20 08:42 UTC, 106 request HTTP 200; hasil final di docs/01-dataset/04-nrt-vs-sp-and-latency.md §3; menunggu review · disetujui: Lanang (R1), 2026-11-21, sesi Claude Code; dengan perubahan: polling 15 menit
- [x] **A-P1-009** Aturan kualitas data awal · R1 · bukti: draf agen, PR #1 (2026-11-19): docs/01-dataset/06-data-quality-rules.md; menunggu review · disetujui: Lanang (R1), 2026-11-21, sesi Claude Code
- [x] **A-P1-010** Rekomendasi dataset + laporan Fase 1 (12 bagian) · R1 · bukti: draf agen, PR #1 (2026-11-19, latensi final 2026-11-20): docs/01-dataset/07-dataset-recommendation.md + README.md; menunggu review · disetujui: Lanang (R1), 2026-11-21, sesi Claude Code; dengan perubahan HD-08 → B5 dan polling 15 menit

### P2 — Requirements Engineering

- [x] **A-P2-001** Semantik data & aturan perhitungan · R1 · bukti: PR #3 (2026-11-22, diperbarui 2026-11-23): docs/03-specs/data/01-data-semantics.md (SEM-00…SEM-13, KEP-01…05); putusan review Lanang atas KEP-01…05 tercatat di §3 dokumen; KEP-01/04/05 masih perlu dikonfirmasi Abigail sebelum G2 · disetujui: Lanang, 2026-11-23, dinyatakan langsung di sesi Claude Code

### P3 — Architecture & Technical Specs

- [ ] **A-P3-001** Kontrak canonical event v1 + sampel record · R1 · bukti: — · disetujui: —
- [ ] **A-P3-002** Spesifikasi ETL (dua mode) · R1 · bukti: — · disetujui: —

### P4 — Development Harness

- [ ] **A-P4-002** Tooling Python bersama (lint, format, test, pre-commit) · R1 · bukti: — · disetujui: —
- [ ] **A-P4-001** Skeleton paket pipeline + fixtures uji dari data nyata · R1 · bukti: — · disetujui: —

### P5 — ETL & Cassandra Implementation

- [ ] **A-P5-001** Source adapter + extractor FIRMS (kuota, retry, raw zone) · R1 · bukti: — · disetujui: —
- [ ] **A-P5-002** Parsing & validasi + rejected records · R1 · bukti: — · disetujui: —
- [ ] **A-P5-003** Normalisasi waktu & atribut · R1 · bukti: — · disetujui: —
- [ ] **A-P5-004** Pengayaan spasial (provinsi, status luar provinsi) · R1 · bukti: — · disetujui: —
- [ ] **A-P5-005** Deduplikasi & identitas deteksi · R1 · bukti: — · disetujui: —
- [ ] **A-P5-006** Mode backfill (checkpoint, resume, run log) · R1 · bukti: — · disetujui: —
- [ ] **A-P5-007** Mode incremental NRT (polling) · R1 · bukti: — · disetujui: —
- [ ] **A-P5-008** Test ETL + harness idempotensi · R1 · bukti: — · disetujui: —
- [ ] **A-P5-009** Publikasi batas provinsi tersederhanakan untuk web · R1 · bukti: — · disetujui: —
- [ ] **A-P5-010** Dokumentasi pipeline · R1 · bukti: — · disetujui: —

### P7 — Integration, Testing & Experiments

- [ ] **A-P7-001** Uji idempotensi pada data nyata · R1 · bukti: — · disetujui: —
- [ ] **A-P7-002** Laporan kualitas data per run · R1 · bukti: — · disetujui: —
- [ ] **A-P7-003** Rekonsiliasi NRT→SP manual (Should) (Should) · R1 · bukti: — · disetujui: —
- [ ] **A-P7-004** Hardening & perbaikan bug data (time-box) · R1 · bukti: — · disetujui: —

### P8 — Documentation & Final Delivery

- [ ] **A-P8-001** Dokumentasi teknis data (pipeline, DQ, keterbatasan) · R1 · bukti: — · disetujui: —
- [ ] **A-P8-002** Perakitan presentasi ≤20 menit (manusia) · *manusia saja* · R1 · bukti: — · disetujui: —

## Role B (R2)

### P1 — Dataset Feasibility

- [x] **B-P1-001** Estimasi volume per provinsi per hari/bulan · R2 · bukti: draf agen, PR #1 (2026-11-19): docs/03-specs/database/00-volume-estimates.md; menunggu review · disetujui: Lanang (R1), 2026-11-22, sesi Claude Code (persetujuan saat mencatat G1)

### P2 — Requirements Engineering

- [ ] **B-P2-001** Kebutuhan query aplikasi (Q-xx) · R2 · bukti: — · disetujui: —

### P3 — Architecture & Technical Specs

- [ ] **B-P3-001** Access pattern matrix · R2 · bukti: — · disetujui: —
- [ ] **B-P3-002** Model data logis & fisik + spesifikasi CQL · R2 · bukti: — · disetujui: —
- [ ] **B-P3-003** Strategi read model/agregat & rebuild · R2 · bukti: — · disetujui: —
- [ ] **B-P3-004** Rencana eksperimen Cassandra · R2 · bukti: — · disetujui: —

### P4 — Development Harness

- [ ] **B-P4-001** Konfigurasi Cassandra single-node untuk dev · R2 · bukti: — · disetujui: —
- [ ] **B-P4-002** Smoke test 3 node di laptop (dokumen 07 §4) (Should) · R2 · bukti: — · disetujui: —

### P5 — ETL & Cassandra Implementation

- [ ] **B-P5-001** Implementasi skema CQL v1 + migrasi · R2 · bukti: — · disetujui: —
- [ ] **B-P5-002** Writer adapter Cassandra (idempoten) · R2 · bukti: — · disetujui: —
- [ ] **B-P5-003** Builder read model/agregat · R2 · bukti: — · disetujui: —
- [ ] **B-P5-004** Tabel run log & checkpoint + writer · R2 · bukti: — · disetujui: —
- [ ] **B-P5-005** Test database per access pattern · R2 · bukti: — · disetujui: —
- [ ] **B-P5-006** Load backfill penuh + inspeksi ukuran partisi · R2 · bukti: — · disetujui: —
- [ ] **B-P5-007** Dokumentasi database · R2 · bukti: — · disetujui: —

### P7 — Integration, Testing & Experiments

- [ ] **B-P7-001** Eksekusi eksperimen bucketing (Must) · R2 · bukti: — · disetujui: —
- [ ] **B-P7-002** Laporan eksperimen · R2 · bukti: — · disetujui: —
- [ ] **B-P7-003** Eksperimen replikasi/konsistensi/failure 3 node (Should) (Should) · R2 · bukti: — · disetujui: —
- [ ] **B-P7-004** Hardening & perbaikan bug DB (time-box) · R2 · bukti: — · disetujui: —

### P8 — Documentation & Final Delivery

- [ ] **B-P8-001** Dokumentasi database + hasil eksperimen · R2 · bukti: — · disetujui: —

## Role C (R3)

### P1 — Dataset Feasibility

- [ ] **C-P1-001** Inventaris toolchain & opsi cloud (NA-07) · R3 · bukti: — · disetujui: —

### P2 — Requirements Engineering

- [ ] **C-P2-001** Non-functional requirements kuantitatif · R3 · bukti: — · disetujui: —

### P3 — Architecture & Technical Specs

- [ ] **C-P3-001** Arsitektur end-to-end + ADR stack · R3 · bukti: — · disetujui: —
- [ ] **C-P3-002** Kontrak API v1 (OpenAPI) · R3 · bukti: — · disetujui: —
- [ ] **C-P3-003** ADR deployment & keamanan (OQ-24–OQ-26) · R3 · bukti: — · disetujui: —

### P4 — Development Harness

- [ ] **C-P4-001** Kerangka repo + CODEOWNERS + template PR · R3 · bukti: — · disetujui: —
- [ ] **C-P4-004** Docker Compose dasar + validasi environment · R3 · bukti: — · disetujui: —
- [ ] **C-P4-005** CI: lint + unit test per komponen · R3 · bukti: — · disetujui: —

### P6 — Backend & Frontend Implementation

- [ ] **C-P6-001** Skeleton FastAPI (config, health, logging, error, CORS) · R3 · bukti: — · disetujui: —
- [ ] **C-P6-002** Interface repository + fake dari contoh kontrak · R3 · bukti: — · disetujui: —
- [ ] **C-P6-003** Endpoint ringkasan + timeline · R3 · bukti: — · disetujui: —
- [ ] **C-P6-004** Endpoint ranking + detail provinsi · R3 · bukti: — · disetujui: —
- [ ] **C-P6-005** Endpoint titik peta (terbatas) · R3 · bukti: — · disetujui: —
- [ ] **C-P6-006** Endpoint status pipeline & kesegaran data · R3 · bukti: — · disetujui: —
- [ ] **C-P6-007** Repository Cassandra nyata · R3 · bukti: — · disetujui: —
- [ ] **C-P6-008** Test API (unit, kontrak, integrasi) · R3 · bukti: — · disetujui: —
- [ ] **C-P6-009** Dokumentasi API · R3 · bukti: — · disetujui: —
- [ ] **C-P6-010** Endpoint distribusi FRP (Should) (Should) · R3 · bukti: — · disetujui: —

### P7 — Integration, Testing & Experiments

- [ ] **C-P7-001** Skrip smoke E2E stack penuh · R3 · bukti: — · disetujui: —
- [ ] **C-P7-002** Provisioning cloud + deploy pertama · R3 · bukti: — · disetujui: —
- [ ] **C-P7-003** Poller di cloud + monitoring + restart · R3 · bukti: — · disetujui: —
- [ ] **C-P7-004** Checklist keamanan + verifikasi · R3 · bukti: — · disetujui: —
- [ ] **C-P7-005** Hardening & perbaikan bug API/deploy (time-box) · R3 · bukti: — · disetujui: —

### P8 — Documentation & Final Delivery

- [ ] **C-P8-001** Panduan instalasi & reproduksibilitas + uji fresh clone · R3 · bukti: — · disetujui: —
- [ ] **C-P8-002** Dokumentasi API, deployment, ADR final · R3 · bukti: — · disetujui: —

## Role D (R4)

### P1 — Dataset Feasibility

- [x] **D-P1-001** Draf user stories & FR dari charter · R4 · bukti: draf agen, PR #1 (2026-11-19): docs/02-requirements/00-draft-user-stories.md; menunggu review · disetujui: —

### P2 — Requirements Engineering

- [ ] **D-P2-001** Functional requirements final · R4 · bukti: — · disetujui: —
- [ ] **D-P2-002** Acceptance criteria per FR · R4 · bukti: — · disetujui: —
- [ ] **D-P2-003** Kunci MVP + urutan pemotongan cakupan · R4 · bukti: — · disetujui: —

### P3 — Architecture & Technical Specs

- [ ] **D-P3-001** Spesifikasi UI + wireframe low-fi · R4 · bukti: — · disetujui: —

### P4 — Development Harness

- [ ] **D-P4-003** AGENTS.md & CLAUDE.md lengkap · R4 · bukti: — · disetujui: —
- [ ] **D-P4-001** Scaffold React + Leaflet + lint/test · R4 · bukti: — · disetujui: —
- [ ] **D-P4-002** Mock API dari contoh OpenAPI · R4 · bukti: — · disetujui: —

### P6 — Backend & Frontend Implementation

- [ ] **D-P6-001** Layout, routing, state filter, klien API · R4 · bukti: — · disetujui: —
- [ ] **D-P6-002** Kartu KPI + timeline · R4 · bukti: — · disetujui: —
- [ ] **D-P6-003** Ranking + drill-down provinsi · R4 · bukti: — · disetujui: —
- [ ] **D-P6-004** Peta Leaflet (titik, batas, popup, notice batas) · R4 · bukti: — · disetujui: —
- [ ] **D-P6-005** Status pipeline + kesegaran + disclaimer + atribusi · R4 · bukti: — · disetujui: —
- [ ] **D-P6-006** State loading/empty/error + aksesibilitas dasar · R4 · bukti: — · disetujui: —
- [ ] **D-P6-007** Ganti mock → API nyata (lokal) · R4 · bukti: — · disetujui: —
- [ ] **D-P6-008** Histogram FRP + perbandingan periode (Should) (Should) · R4 · bukti: — · disetujui: —
- [ ] **D-P6-009** Test frontend (unit/komponen) · R4 · bukti: — · disetujui: —

### P7 — Integration, Testing & Experiments

- [ ] **D-P7-001** E2E smoke test UI · R4 · bukti: — · disetujui: —
- [ ] **D-P7-002** Review terminologi ilmiah, disclaimer, aksesibilitas · R4 · bukti: — · disetujui: —
- [ ] **D-P7-003** Hardening & perbaikan bug UI (time-box) · R4 · bukti: — · disetujui: —

### P8 — Documentation & Final Delivery

- [ ] **D-P8-001** Dokumentasi UI + skrip demo + screenshot · R4 · bukti: — · disetujui: —
- [ ] **D-P8-002** Checklist penerimaan final + indeks dokumentasi · R4 · bukti: — · disetujui: —
- [ ] **D-P8-003** Rekam video demo (manusia) · *manusia saja* · R4 · bukti: — · disetujui: —

## Koordinator integrasi (tugas X-)

### P1 — Dataset Feasibility

- [x] **X-P1-901** Tetapkan anggota↔peran, koordinator, ketersediaan; setujui rencana eksekusi · Koordinator (R2) · bukti: anggota↔peran, koordinator R2, ketersediaan dicatat di [12](12-human-decision-register.md) + [01 §0](01-role-charters.md#0-penugasan-anggota-hd-01), 2026-11-19 · disetujui: tim, 2026-11-19 (GATE-EP)
- [x] **X-P1-902** Paket gerbang G1 + catat keputusan + perbarui STATUS · Koordinator (R2) · bukti: G1 dicatat 2026-11-22: docs/STATUS.md §1/§3/§6/§8, 12 (HD-08…HD-11), CR-03 diterapkan ke 00-discovery/03-assumptions-register.md; didelegasikan Abi Funn ke Lanang (disampaikan Lanang 2026-11-22) · disetujui: tim, 2026-11-22 (G1)

### P2 — Requirements Engineering

- [ ] **X-P2-901** Paket gerbang G2 · Koordinator (R2) · bukti: — · disetujui: —

### P3 — Architecture & Technical Specs

- [ ] **X-P3-901** Paket G3 + cek konsistensi lintas kontrak · Koordinator (R2) · bukti: — · disetujui: —

### P4 — Development Harness

- [ ] **X-P4-901** Paket G4: uji fresh clone · Koordinator (R2) · bukti: — · disetujui: —

### P5 — ETL & Cassandra Implementation

- [ ] **X-P5-901** Checkpoint D10 (R-14) + paket G5 · Koordinator (R2) · bukti: — · disetujui: —

### P6 — Backend & Frontend Implementation

- [ ] **X-P6-901** Integrasi E2E lokal pertama (D13) + paket G6 · Koordinator (R2) · bukti: — · disetujui: —

### P7 — Integration, Testing & Experiments

- [ ] **X-P7-901** Feature freeze D17 · Koordinator (R2) · bukti: — · disetujui: —
- [ ] **X-P7-902** Paket gerbang G7 · Koordinator (R2) · bukti: — · disetujui: —

### P8 — Documentation & Final Delivery

- [ ] **X-P8-901** Perakitan laporan proyek (manusia) · *manusia saja* · Koordinator (R2) · bukti: — · disetujui: —
- [ ] **X-P8-902** Gerbang G8 — penerimaan akhir · Koordinator (R2) · bukti: — · disetujui: —
