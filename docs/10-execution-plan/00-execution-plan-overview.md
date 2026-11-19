# 00 — Execution Plan Overview

> Rencana eksekusi tim · Disusun 2026-11-19 (D1) · Status: **GATE-EP disetujui tim 2026-11-19**. Semua rekomendasi HD-01–07 dan HD-22–24 diterima ([12](12-human-decision-register.md)).
> Label informasi mengikuti [legenda Fase 0](../00-discovery/README.md#label-status-informasi). Dokumen Fase 0 **tidak diubah**. Perubahan atas dokumen tersebut hanya lewat *change request* ([docs/change-requests/](../change-requests/)).

## 1. Status proyek saat rencana ini dibuat

| Item | Nilai | Sumber |
|---|---|---|
| Fase 0 | Selesai, **G0 disetujui 2026-11-19** | [STATUS.md](../STATUS.md) |
| Fase 1 | **Sedang berjalan.** Agen mengerjakan tugas R1 atas permintaan tim: inventaris sumber dan evaluasi batas sudah berupa draf, unduhan sampel selesai, poller latensi masih berjalan; profiling dan dokumen sisa belum dikerjakan. | `docs/01-dataset/`, `scratch/phase1/` |
| Kalender | D1 = 2026-11-19 … D21 = 2026-12-09 | A-22 (`ASSUMPTION`) |
| Tim | R1/A **Lanang** · R2/B **Abi Funn** (+ koordinator) · R3/C **Zita** · R4/D **Abigail**; 4 jam/hari, R1 & R3 ±5 jam/hari pada D9–D15 | HD-01–03, HD-07 |
| Kode aplikasi | Belum ada | — |

## 2. Struktur peran

Rencana ini **mempertahankan peran R1–R4 yang sudah disetujui** di [charter §9](../00-discovery/01-project-charter.md#9-tim-dan-peran). Huruf A–D dari brief perencanaan dipakai sebagai prefiks ID tugas:

| Kode | Peran | Inti kepemilikan | Fase tersibuk (hasil jadwal) |
|---|---|---|---|
| **A = R1** | Data Engineering / ETL | `pipeline/`, data contract, kualitas data | P1 (review), P5 |
| **B = R2** | Cassandra & Data Platform **+ koordinator integrasi** (HD-02) | `db/`, `experiments/`, access patterns, model data | P3, P5, P7 |
| **C = R3** | Backend, Integration & DevOps | `api/`, Compose, CI, `deploy/`, cloud | P3–P4, P6, P7 |
| **D = R4** | Frontend, Visualization & Delivery | `web/`, requirements, UI spec, AGENTS.md, perakitan dokumen final | P2, P6, P8 |

Penyesuaian terhadap brief perencanaan (disetujui di GATE-EP):
- **DevOps tetap di R3** sesuai charter. Brief memisahkan backend dari infrastruktur, tetapi charter yang sudah disetujui menggabungkannya.
- **AGENTS.md/CLAUDE.md dipegang R4**, bukan koordinator atau R3. Alasannya kapasitas: R3 kelebihan beban di D2–D8 (lihat [09 §1](09-risk-capacity-plan.md#1-revisi-rencana-hasil-self-review)).
- **Tooling Python bersama (ruff, pre-commit) dipegang R1**, karena R1 longgar di D4–D6.
- **Koordinator integrasi = R2.** Dari keempat opsi, hanya R2 yang menghasilkan jadwal tanpa masalah. Detail perbandingan ada di [09 §2](09-risk-capacity-plan.md#2-pemilihan-koordinator-integrasi).

Detail lengkap: [01-role-charters.md](01-role-charters.md).

## 3. Strategi eksekusi

1. **Kontrak dulu, lalu paralel.** Empat kontrak antarmuka ([06](06-interface-contracts.md)) disetujui di G3: canonical event, access patterns + CQL, OpenAPI, dan UI spec. Setelah itu A, B, C, dan D bekerja paralel dengan mock.
2. **Fase 2 dan 3 tumpang tindih per artefak**, sesuai charter §10 ("D3–D5: 2 + 3"). Spesifikasi Fase 3 mulai dari draf Fase 2. G3 tetap mensyaratkan G2.
3. **Fase 4 (harness) paralel dengan Fase 2–3**, segera setelah GATE-EP.
4. **Mock-to-real terjadwal.** Backend memakai fake repository, frontend memakai mock API dari contoh OpenAPI. Penggantian ke integrasi nyata punya tugas sendiri (C-P6-007, D-P6-007) dan checklist di [06 §7](06-interface-contracts.md#7-checklist-mock-to-real).
5. **Satu implementer per tugas.** Claude Code mengimplementasi, Codex me-review, dan manusia menyetujui merge ([11](11-role-prompts/)).
6. **Must dulu.** Tugas *Should* dijadwalkan terakhir dan hanya mengisi celah. Jika tidak muat, tugas itu dipotong lebih dulu.

## 4. Urutan fase & milestone (hasil penjadwalan dengan kapasitas yang disetujui)

| Milestone | Rencana | Target charter | Selisih |
|---|---|---|---|
| GATE-EP: rencana ini + anggota↔peran | D2 (11-20) | — | — |
| G1: dataset final | D3 (11-21) | D2–D3 | sesuai |
| G2: requirements | D7 (11-25) | D3–D5 | **+2 hari** |
| G3: kontrak & model | D8 (11-26) | D5 | **+3 hari** |
| G4: harness | D8 (11-26) | D5 | **+3 hari** |
| G5: ETL + Cassandra berisi data nyata | D14 (12-02) | D10–D12 | **+2 hari** |
| G6: integrasi end-to-end lokal pertama | D14 (12-02) | D13 | **+1 hari** |
| Feature freeze | D17 (12-05) | D17 | sesuai |
| G7: test, eksperimen, cloud | D18 (12-06) | D19 | −1 hari |
| G8: penerimaan akhir | D20 (12-08) | D21 | **buffer 1 hari** |

**Temuan penting:** dengan 4 jam/hari rata (opsi a), integrasi baru D15, freeze D18, dan G8 tepat D21 tanpa sisa waktu. Tim memilih **HD-07 (b)**: R1 dan R3 bekerja ±5 jam/hari pada D9–D15. Hasilnya integrasi **D14** (charter D13, masih +1 hari), freeze **D17**, dan G8 **D20** dengan buffer 1 hari. Tiga tugas *Should* tetap tidak muat sebelum batasnya dan menjadi kandidat pertama dipotong (opsi c). Skenario lain ada di [09 §3](09-risk-capacity-plan.md#3-skenario-kapasitas).

## 5. Rantai kritis

```text
Review Fase 1 (R1) → G1 → semantik data (R1) → canonical event (R1) → model data (R2) → paket G2/G3 (koordinator)
→ G3 → ETL extract → validate → enrich → normalize → dedup → backfill → incremental → test ETL (R1)
→ G5/G6 → deploy cloud → keamanan → poller cloud → smoke E2E → hardening (R3) → G7
→ dokumentasi UI → video → checklist final (R4) → G8
```

**Implementasi ETL oleh R1 (±26,5 jam berurutan, D9–D14) adalah titik terlemah.** Setiap keterlambatan di sana langsung menggeser D21. Rincian per tugas ada di [05 §3](05-project-schedule.md#3-rantai-kritis-resource-constrained), dan grafik dengan rantai kritis berwarna merah ada di [04](04-dependency-graph.mmd).

## 6. Isi folder ini

| File | Isi | Cara dibuat |
|---|---|---|
| [00-execution-plan-overview.md](00-execution-plan-overview.md) | Dokumen ini | manual |
| [01-role-charters.md](01-role-charters.md) | Piagam peran, penugasan anggota, RACI | manual |
| [02-work-breakdown-structure.csv](02-work-breakdown-structure.csv) / [.md](02-work-breakdown-structure.md) | 110 tugas dengan 24+ field | **generator** |
| [03-dependency-matrix.md](03-dependency-matrix.md) | Dependensi, handoff, perlakuan bila terlambat | **generator** |
| [04-dependency-graph.mmd](04-dependency-graph.mmd) | Grafik Mermaid | **generator** |
| [05-project-schedule.md](05-project-schedule.md) | Jadwal harian, Gantt, beban, buffer, kontingensi | **generator** |
| [06-interface-contracts.md](06-interface-contracts.md) | Kontrak antarlapisan A–E + checklist mock-to-real | manual |
| [07-file-ownership-matrix.md](07-file-ownership-matrix.md) | Kepemilikan file, branch, PR, konflik | manual |
| [08-automation-strategy.md](08-automation-strategy.md) | Otomasi dan batas persetujuan | manual |
| [09-risk-capacity-plan.md](09-risk-capacity-plan.md) | Revisi kapasitas, skenario, risiko baru | manual |
| [10-phase-gates.md](10-phase-gates.md) | Entry/exit per gerbang, DoR, DoD, change management | manual |
| [11-role-prompts/](11-role-prompts/) | Prompt siap pakai per peran + reviewer Codex | manual |
| [12-human-decision-register.md](12-human-decision-register.md) | Keputusan yang harus diambil tim | manual |
| [13-progress-tracker.md](13-progress-tracker.md) | **Checklist progres hidup** per task ID dan gerbang (centang implementer, persetujuan reviewer) | struktur oleh **generator** sekali; isi oleh tim/agen; ringkasan diperbarui otomatis |
| [tools/build_plan.py](tools/build_plan.py) | **Sumber kebenaran WBS**, penjadwal, pemeriksaan konsistensi | manual |

**Cara mengubah WBS:** edit `TASKS` di `tools/build_plan.py`, lalu jalankan `python -I docs/10-execution-plan/tools/build_plan.py`. Pastikan output `ISSUES: 0`. File hasil generator jangan diedit manual. Pengecualiannya baris tugas di `13-progress-tracker.md`, yang memang diisi manual dan tidak pernah ditimpa generator. Run skenario (`--hours`, `--coord`) hanya mencetak ke konsol.

## 7. Konflik yang ditemukan saat audit (diterima tim di GATE-EP, 2026-11-19)

| # | Konflik | Perlakuan di rencana ini |
|---|---|---|
| K-01 | Brief perencanaan memperlakukan Fase 1 sebagai "belum mulai", padahal Fase 1 sudah berjalan atas permintaan tim. | Status tugas P1 diisi apa adanya. Estimasi P1 = sisa usaha manusia (review & keputusan). |
| K-02 | Brief melarang memanggil API FIRMS, sementara proses Fase 1 yang sudah berjalan sebelumnya memakai kuota. Unduhan sampel selesai saat rencana ini disusun; **poller latensi masih berjalan** (berhenti sendiri setelah 24 jam). | Tugas perencanaan ini tidak memanggil API. Poller tidak dihentikan tanpa persetujuan: **HD-22**. |
| K-03 | Peran C di brief tanpa DevOps, sedangkan charter R3 = Backend **& DevOps**. | Mengikuti charter. |
| K-04 | Nama direktori di brief (`etl/`, `cassandra/`, `backend/`, `frontend/`) berbeda dari charter (`pipeline/`, `db/`, `api/`, `web/`). | Mengikuti charter (usulan), difinalkan di C-P4-001. |
| K-05 | Brief memasukkan laporan, presentasi, dan video ke Fase 8, padahal Fase 0 memutuskan ketiganya ditangani tim, bukan agen (OQ-01, A-23). | Dijadwalkan sebagai tugas **manusia saja** (X-P8-901, A-P8-002, D-P8-003). Prompt agen melarang mengerjakannya. |
| K-06 | Charter §9: R4 memiliki seluruh `docs/`. | Diperhalus: setiap peran memiliki subfolder dokumennya sendiri. R4 merakit `docs/08-delivery/`. Disetujui (CR-01). |
| K-07 | STATUS.md menyebut dokumen Fase 0 ada di branch `docs/phase-0-discovery`, padahal commit-commit itu sudah ada di `main` (branch aktif). Sebelumnya saya juga salah menyebut repo "di branch `docs/phase-0-discovery`". | Disetujui; STATUS.md diperbaiki (CR-02). |
| K-08 | Brief menyebut *grid assignment*; Fase 0 tidak memasukkannya ke ruang lingkup. | Tidak dijadwalkan; diputuskan di Fase 3 hanya jika access pattern peta membutuhkannya (**HD-21**). |
| K-09 | Target D13/D17 di charter tidak tercapai pada kapasitas 4 jam/hari. | Tim memilih HD-07 (b): G6 D14, G8 D20. |
