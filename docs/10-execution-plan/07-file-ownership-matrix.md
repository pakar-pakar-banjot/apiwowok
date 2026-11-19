# 07 — File Ownership Matrix

> Status: `RECOMMENDATION`. Struktur direktori final dibuat di **C-P4-001** dan ditegakkan dengan `.github/CODEOWNERS`. Nama direktori mengikuti charter §9 (`pipeline/`, `db/`, `api/`, `web/`), tidak mengikuti brief (`etl/`, `cassandra/`, …). Lihat konflik K-04.

## 1. Direktori

| Path | Maintainer | Reviewer default | Catatan |
|---|---|---|---|
| `pipeline/` | A (R1) | B | Termasuk `pipeline/resources/boundaries/`, yang di-commit hanya setelah HD-08 |
| `db/` | B (R2) | A / C | Migrasi, writer, agregat, run log, skrip readiness |
| `experiments/` | B | A | Satu subfolder per eksperimen dengan `REPORT.md` |
| `api/` | C (R3) | D / B | — |
| `deploy/` | C | B | Skrip env, smoke E2E, konfigurasi cloud. **Tanpa secret.** |
| `web/` | D (R4) | C | Termasuk `web/src/mocks/` dan `web/e2e/` |
| `docs/00-discovery/` | Beku | — | Perubahan hanya lewat change request, diterapkan koordinator |
| `docs/01-dataset/` | A | B | — |
| `docs/02-requirements/` | D | C | Pengecualian: `02-non-functional-requirements.md` milik C |
| `docs/03-specs/data/` | A | B | — |
| `docs/03-specs/database/` | B | A / C | Termasuk `00-volume-estimates.md`, `01-query-requirements.md` |
| `docs/03-specs/api/` | C | D | `openapi.yaml` adalah sumber kebenaran kontrak D |
| `docs/03-specs/ui/` | D | C | — |
| `docs/03-specs/architecture/` | C | B | ADR: satu file per ADR, penulis = maintainer file |
| `docs/03-specs/README.md` | Koordinator | — | Indeks + laporan konsistensi G3 |
| `docs/08-delivery/` | D (index, ui, acceptance, demo) | C | Pengecualian per file: `data.md` (A), `database.md` (B), `api-deploy.md` (C) |
| `docs/10-execution-plan/` | Koordinator | semua | File hasil generator hanya diubah lewat `tools/build_plan.py` |
| `docs/10-execution-plan/13-progress-tracker.md` | Koordinator (struktur) | — | **Pengecualian:** setiap implementer mencentang dan mengisi `bukti:` di baris tugasnya sendiri; `disetujui:` hanya diisi reviewer manusia |
| `docs/change-requests/` | Koordinator | pemilik artefak terdampak | `CR-xxx.md` |
| `scratch/phase1/` | A | — | Skrip sekali pakai Fase 1; status commit diputuskan di HD-24 |
| `data/` | A | — | **Tidak pernah di-commit** (`.gitignore`) |

## 2. File bersama di root

| File | Maintainer | Cara peran lain meminta perubahan |
|---|---|---|
| `docker-compose.yml`, `docker-compose.*.yml` | C | B menyerahkan fragmen service Cassandra (`db/docker/`); C menggabungkan |
| `.env.example` | C | Ajukan nama variabel + deskripsi di PR peran sendiri; C menambahkan |
| `.gitignore` | C | Issue/PR kecil ke C |
| `.github/` (CODEOWNERS, workflows, template PR) | C | — |
| `ruff.toml`, `.pre-commit-config.yaml` | A | — |
| `AGENTS.md`, `CLAUDE.md` | D | Usulan aturan lewat PR yang di-review koordinator |
| `README.md` (root) | C | Setiap peran menulis README di direktorinya; root hanya menautkan |
| `docs/STATUS.md` | Koordinator | Diperbarui setiap gerbang/keputusan |
| `.env` | **Tidak dimiliki repo** | Lokal saja; tidak pernah di-commit atau dicetak |

## 3. Aturan pencegahan konflik

1. Satu file hanya punya satu maintainer. Perubahan oleh orang lain harus lewat PR yang di-review maintainer tersebut, sebagai **change request** bila menyentuh kontrak.
2. **Satu tugas = satu branch = satu implementer** (manusia + satu agen). Claude Code dan Codex tidak pernah menulis di working directory yang sama secara bersamaan.
3. Agen bekerja di **git worktree** terpisah per tugas: `git worktree add ../apiwowok-<task-id> -b <branch>`.
4. Kontrak (`openapi.yaml`, canonical event, `schema-v1.cql`, UI spec) hanya berubah lewat CR ([10 §5](10-phase-gates.md#5-change-management)). Konsumen tidak boleh mengadaptasi kontrak secara diam-diam.
5. Breaking change wajib menaikkan versi major dan mencantumkan daftar konsumen terdampak.

## 4. Branch & PR

| Aturan | Nilai |
|---|---|
| Branch utama | `main`, dilindungi: merge hanya lewat PR, CI hijau, ≥1 approval manusia (HD-18) |
| Nama branch | `<peran>/<task-id>-<slug>`, contoh `a/A-P5-003-normalize-time`, `x/X-P3-901-g3-packet` |
| Commit | Kecil dan satu tujuan; pesan bahasa Inggris (`feat:`, `fix:`, `docs:`, `test:`, `chore:`); trailer agen bila dibantu agen |
| Judul PR | `[A-P5-003] Normalize acquisition time` |
| Isi PR (template) | Task ID; ringkasan; file yang diubah, semuanya di area pemilik; kriteria penerimaan + bukti (output perintah); test yang dijalankan; dampak kontrak (ya/tidak + CR); review agen (Codex) ditempel; checklist DoD |
| Reviewer | Reviewer di WBS **wajib**; Codex review opsional tetapi disarankan untuk kode |
| Merge | Squash merge oleh pemilik setelah approval reviewer manusia |
| Rebase | Pemilik me-rebase branch sendiri sebelum merge; tidak force-push ke branch orang lain |

## 5. Prosedur penyelesaian konflik

1. **Konflik Git di file milik sendiri:** pemilik menyelesaikan, lalu menjalankan ulang test.
2. **Butuh mengubah file milik peran lain:** berhenti, buka issue/CR ke maintainer, dan lanjutkan dengan mock atau asumsi bila dependensinya *soft*.
3. **Dua peran tidak sepakat tentang kontrak:** pemilik kontrak mengusulkan; konsumen menyetujui atau menolak dengan alasan. Jika buntu >1 hari kerja, koordinator memutuskan di standup, atau tim memutuskan bila menyangkut ruang lingkup.
4. **Agen mengubah file di luar area:** PR ditolak; perubahan dipisah ke PR milik maintainer yang benar.
