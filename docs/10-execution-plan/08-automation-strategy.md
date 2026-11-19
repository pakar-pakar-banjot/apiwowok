# 08 — Automation Strategy

> Status: `RECOMMENDATION`. Prinsipnya: otomatiskan hal yang deterministik dan berulang, dan jangan menambah alat hanya demi kompleksitas. Alat dipilih final di Fase 4 (ADR-001, HD-14, HD-15). Perintah di bawah adalah **target** yang dibuat oleh tugas yang disebut, dan **belum ada** di repo.

## 1. Kategori

| Kategori | Arti | Contoh |
|---|---|---|
| **Otomatis penuh** | Berjalan tanpa manusia; gagal → memblokir merge atau memberi peringatan | lint, unit test, contract test, validasi OpenAPI, deteksi secret, healthcheck |
| **Dibantu AI** | Agen menyiapkan dan manusia memeriksa | kode modul, test, draf dokumen, analisis profil, review PR (Codex) |
| **Disetujui manusia** | Otomatis setelah ada persetujuan eksplisit | migrasi skema ke DB bersama, deploy cloud, rekonsiliasi NRT→SP, eksperimen 3 node |
| **Manual saja** | Keputusan atau aksi yang tidak didelegasikan | persetujuan gerbang, ruang lingkup, kebijakan data, lisensi, biaya cloud, secret, operasi destruktif, kesimpulan analitis, laporan/presentasi/video |

## 2. Peluang otomasi per area

### Data engineering (pemilik R1)

| Otomasi | Pemicu | Alat/skrip | Input → output | Bila gagal | Persetujuan |
|---|---|---|---|---|---|
| Verifikasi checksum raw zone | sebelum profiling/ETL | skrip sha256 vs `manifest.csv` | raw + manifest → laporan | stop; unduh ulang file terkait | — |
| Profiling (null, rentang, duplikat, cakupan) | file raw baru | `scratch/phase1/profile_firms.py` → modul `pipeline` | raw → `profile.json`, CSV | laporkan; jangan ubah data | — |
| Validasi skema header | setiap run | parser pipeline (A-P5-002) | file → diterima/ditolak + reason | rekaman ditolak tercatat | — |
| Test waktu & dedup | setiap PR | pytest (A-P5-008) | fixtures → lulus/gagal | blok merge | — |
| Harness idempotensi | PR ke `pipeline/`/`db/` + sebelum G5/G7 | pytest + Cassandra container | 2× run → selisih | blok merge | — |
| Laporan DQ per run | setiap run | A-P7-002 | run log → markdown | peringatan di status | — |
| Pemeriksaan checkpoint | setiap run incremental | pipeline | checkpoint → poll berikut | catat gagal, jangan maju | — |

### Cassandra (pemilik R2)

| Otomasi | Pemicu | Alat/skrip | Bila gagal | Persetujuan |
|---|---|---|---|---|
| Readiness check | `compose up`, CI job DB | `db/scripts/wait_for_cassandra` | service unhealthy → CI gagal | — |
| Apply migrasi (idempoten, `IF NOT EXISTS`) | dev lokal, CI | `db/scripts/migrate` | stop; tidak ada auto-drop | **Manusia** untuk DB cloud/bersama |
| Validasi CQL | PR yang mengubah `db/migrations/` | apply ke container kosong | blok merge | — |
| Muat dataset uji | CI job DB | fixtures → writer | blok merge | — |
| Smoke query per Q-xx | PR `db/`/`api/` | `db/tests` (B-P5-005) | blok merge | — |
| Larangan `ALLOW FILTERING` | setiap PR | grep di CI | blok merge | — |
| Inspeksi ukuran partisi | setelah load penuh | `nodetool tablestats/tablehistograms` | laporkan | — |
| Benchmark | manual, terjadwal | `experiments/*/run` | simpan log; tidak ada angka tanpa log | Kesimpulan: tim |

### Backend & DevOps (pemilik R3)

| Otomasi | Pemicu | Alat | Bila gagal | Persetujuan |
|---|---|---|---|---|
| Format + lint + type check | pre-commit, CI | ruff (+ mypy bila disepakati) | blok merge | — |
| Unit & contract test | CI | pytest; respons divalidasi terhadap `openapi.yaml` | blok merge | — |
| Validasi OpenAPI | PR yang mengubah `openapi.yaml` | validator CLI | blok merge | Perubahan kontrak: CR |
| Validasi env | `compose up`, deploy | `deploy/scripts/check_env` (tanpa mencetak nilai) | stop dengan pesan nama variabel | — |
| Smoke E2E | sebelum merge besar, sebelum G6/G7 | `deploy/scripts/smoke_e2e` | blok rilis | — |
| Healthcheck container | runtime | Compose healthcheck | restart / alarm halaman status | — |
| Deploy cloud | manual | skrip `deploy/cloud` | rollback ke image sebelumnya | **Manusia** (keamanan & biaya) |

### Frontend (pemilik R4)

| Otomasi | Pemicu | Alat (HD-14) | Bila gagal |
|---|---|---|---|
| Format, lint, type check | pre-commit, CI | ESLint + Prettier + `tsc` | blok merge |
| Unit/komponen test | CI | Vitest + Testing Library | blok merge |
| Cek kontrak mock | CI | test: setiap respons mock lolos skema `openapi.yaml` | blok merge |
| Grep terminologi | CI | grep kata "kebakaran" di string UI | peringatan → review R1 |
| E2E smoke | sebelum G6/G7 | Playwright (atau setara) | blok rilis |
| Build produksi | CI | `npm run build` | blok merge |

### Lintas proyek (pemilik R3, kecuali disebut)

| Otomasi | Pemicu | Alat | Catatan |
|---|---|---|---|
| Pre-commit hooks | setiap commit | pre-commit (A): lint, end-of-file, deteksi secret, larangan file besar dan `.env` | Hook tidak boleh dilewati (`--no-verify`) tanpa izin |
| CI | setiap PR | GitHub Actions dengan path filter per komponen | Tanpa secret di CI; FIRMS **tidak** dipanggil di CI |
| CODEOWNERS | setiap PR | GitHub | Reviewer otomatis sesuai 07 |
| Regenerasi rencana | perubahan WBS | `tools/build_plan.py` (koordinator) | `ISSUES: 0` wajib |
| Cek tautan dokumen | PR yang mengubah `docs/` | skrip cek tautan relatif | peringatan |
| Checklist rilis | sebelum G7/G8 | `docs/08-delivery/acceptance-checklist.md` | manual dengan bukti |

## 3. Batas tegas (tidak diotomatiskan tanpa persetujuan eksplisit)

- `DROP`, `TRUNCATE`, penghapusan data, rekonsiliasi yang menghapus NRT, dan reset volume Docker berisi data bersama.
- Pembuatan, rotasi, atau penyalinan secret (`FIRMS_MAP_KEY`, kredensial cloud).
- Provisioning atau penghapusan resource cloud berbayar.
- Pemanggilan API FIRMS dari CI atau skrip terjadwal baru. Poller produksi hanya berjalan di lingkungan yang disetujui (C-P7-003).
- Merge ke `main` tanpa approval manusia.
- Menulis angka benchmark atau test ke dokumen tanpa log yang mendasarinya.
