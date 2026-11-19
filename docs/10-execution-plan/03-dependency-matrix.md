# 03 — Dependency Matrix

> **File hasil generator** — jangan diedit manual. Sumber: `tools/build_plan.py`. Koordinator integrasi yang dipakai: Role B (R2) (HD-02, disetujui GATE-EP 2026-11-19). Kapasitas: HD-03 + HD-07(b).

Jenis: **Hard** (tidak bisa jalan), **Soft** (boleh jalan dengan asumsi/mock), **Interface** (boleh jalan setelah kontrak disetujui), **Review** (boleh jalan, tidak boleh diterima sebelum review), **Human approval** (berhenti sampai tim memutuskan).

Aturan umum *dependency satisfied*: tugas prasyarat memenuhi DoD (PR di-merge setelah review) — untuk Interface: kontrak versi tersebut disetujui di gerbang; untuk gerbang: keputusan tim tercatat di STATUS.md.

## 1. Gerbang fase

| Gerbang | Deskripsi | Prasyarat |
|---|---|---|
| GATE-EP | Persetujuan rencana eksekusi (dokumen ini) + penetapan anggota/peran | X-P1-901 |
| GATE-G1 | G1 — dataset, periode (OQ-05), batas provinsi (OQ-07), aturan NRT/SP, aturan DQ | X-P1-902 |
| GATE-G2 | G2 — requirements, NFR, semantik data, MVP terkunci | X-P2-901 |
| GATE-G3 | G3 — kontrak canonical event, access patterns, model data, OpenAPI, UI spec, ADR | X-P3-901 |
| GATE-G4 | G4 — harness: repo, AGENTS.md, Compose, CI hijau | X-P4-901 |
| GATE-G5 | G5 — ETL dua mode + Cassandra berisi data nyata, test DB & ETL lulus | X-P5-901 |
| GATE-G6 | G6 — API + dashboard berjalan di data nyata secara lokal (integrasi lokal pertama) | X-P6-901 |
| GATE-G7 | G7 — test, idempotensi, eksperimen, deploy cloud, feature freeze dipatuhi | X-P7-902 |
| GATE-G8 | G8 — dokumentasi teknis final, checklist penerimaan | X-P8-902 |

## 2. Dependensi lintas peran (handoff)

| Dari (prasyarat) | Pemilik | Ke (dependen) | Pemilik | Jenis | Artefak yang diserahkan | Validator | Jika terlambat |
|---|---|---|---|---|---|---|---|
| B-P1-001 | B | A-P1-010 | A | Soft | docs/03-specs/database/00-volume-estimates.md | Role A (konsumen) + reviewer A | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |
| A-P1-004 | A | B-P1-001 | B | Hard | docs/01-dataset/03-profiling-report.md, data/firms/profile/* | Role B (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P1-010 | A | X-P1-902 | B | Hard | docs/01-dataset/07-dataset-recommendation.md, docs/01-dataset/README.md | Role B (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| B-P1-001 | B | C-P2-001 | C | Hard | docs/03-specs/database/00-volume-estimates.md | Role C (konsumen) + reviewer A | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P1-008 | A | C-P2-001 | C | Soft | docs/01-dataset/04-nrt-vs-sp-and-latency.md (bagian latensi) | Role C (konsumen) + reviewer B | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |
| D-P2-001 | D | B-P2-001 | B | Hard | docs/02-requirements/01-functional-requirements.md | Role B (konsumen) + reviewer C | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P2-001 | A | B-P2-001 | B | Soft | docs/03-specs/data/01-data-semantics.md | Role B (konsumen) + reviewer D | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |
| C-P2-001 | C | D-P2-003 | D | Hard | docs/02-requirements/02-non-functional-requirements.md | Role D (konsumen) + reviewer D | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| B-P2-001 | B | D-P2-003 | D | Soft | docs/03-specs/database/01-query-requirements.md | Role D (konsumen) + reviewer C | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |
| D-P2-003 | D | X-P2-901 | B | Hard | docs/02-requirements/03-mvp-lock.md | Role B (konsumen) + reviewer C | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P2-001 | A | X-P2-901 | B | Hard | docs/03-specs/data/01-data-semantics.md | Role B (konsumen) + reviewer D | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P3-001 | A | B-P3-002 | B | Interface | docs/03-specs/data/02-canonical-event-contract.md, docs/03-specs/data/samples/canonical-events.sample.jsonl | Role B (konsumen) + reviewer B | Lanjut memakai versi kontrak terakhir yang disetujui + mock; perubahan kontrak hanya lewat change request. |
| B-P3-001 | B | C-P3-002 | C | Interface | docs/03-specs/database/02-access-patterns.md | Role C (konsumen) + reviewer C | Lanjut memakai versi kontrak terakhir yang disetujui + mock; perubahan kontrak hanya lewat change request. |
| D-P3-001 | D | C-P3-002 | C | Soft | docs/03-specs/ui/01-ui-spec.md, docs/03-specs/ui/wireframes/ | Role C (konsumen) + reviewer C | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |
| A-P3-001 | A | X-P3-901 | B | Hard | docs/03-specs/data/02-canonical-event-contract.md, docs/03-specs/data/samples/canonical-events.sample.jsonl | Role B (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P3-002 | A | X-P3-901 | B | Hard | docs/03-specs/data/03-etl-spec.md | Role B (konsumen) + reviewer C | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| C-P3-001 | C | X-P3-901 | B | Hard | docs/03-specs/architecture/01-architecture.md, docs/03-specs/architecture/adr/ADR-001..002 | Role B (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| C-P3-002 | C | X-P3-901 | B | Hard | docs/03-specs/api/openapi.yaml, docs/03-specs/api/01-api-notes.md | Role B (konsumen) + reviewer D | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| D-P3-001 | D | X-P3-901 | B | Hard | docs/03-specs/ui/01-ui-spec.md, docs/03-specs/ui/wireframes/ | Role B (konsumen) + reviewer C | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| C-P3-003 | C | X-P3-901 | B | Soft | docs/03-specs/architecture/adr/ADR-003-deployment.md, ADR-004-security.md | Role B (konsumen) + reviewer B | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |
| C-P4-001 | C | A-P4-002 | A | Hard | Direktori kosong ber-README, .github/CODEOWNERS, .github/pull_request_template.md | Role A (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| B-P4-001 | B | C-P4-004 | C | Interface | db/docker/, db/scripts/, db/README.md | Role C (konsumen) + reviewer C | Lanjut memakai versi kontrak terakhir yang disetujui + mock; perubahan kontrak hanya lewat change request. |
| A-P4-002 | A | C-P4-005 | C | Hard | ruff.toml, .pre-commit-config.yaml, panduan venv | Role C (konsumen) + reviewer C | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| D-P4-001 | D | C-P4-005 | C | Soft | web/ | Role C (konsumen) + reviewer C | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |
| C-P4-001 | C | A-P4-001 | A | Hard | Direktori kosong ber-README, .github/CODEOWNERS, .github/pull_request_template.md | Role A (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| C-P4-001 | C | D-P4-001 | D | Hard | Direktori kosong ber-README, .github/CODEOWNERS, .github/pull_request_template.md | Role D (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| C-P3-002 | C | D-P4-002 | D | Interface | docs/03-specs/api/openapi.yaml, docs/03-specs/api/01-api-notes.md | Role D (konsumen) + reviewer D | Lanjut memakai versi kontrak terakhir yang disetujui + mock; perubahan kontrak hanya lewat change request. |
| D-P4-003 | D | X-P4-901 | B | Hard | AGENTS.md, CLAUDE.md | Role B (konsumen) + reviewer C | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| C-P4-004 | C | X-P4-901 | B | Hard | docker-compose.yml, .env.example, deploy/scripts/check_env.* | Role B (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| C-P4-005 | C | X-P4-901 | B | Hard | .github/workflows/ci.yml | Role B (konsumen) + reviewer D | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P4-001 | A | X-P4-901 | B | Hard | pipeline/pyproject.toml, pipeline/src/, pipeline/tests/fixtures/ | Role B (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| D-P4-001 | D | X-P4-901 | B | Hard | web/ | Role B (konsumen) + reviewer C | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| B-P5-002 | B | A-P5-006 | A | Interface | db/src/.../writer.py | Role A (konsumen) + reviewer A | Lanjut memakai versi kontrak terakhir yang disetujui + mock; perubahan kontrak hanya lewat change request. |
| B-P5-004 | B | A-P5-006 | A | Interface | db/src/.../runlog.py | Role A (konsumen) + reviewer C | Lanjut memakai versi kontrak terakhir yang disetujui + mock; perubahan kontrak hanya lewat change request. |
| A-P3-001 | A | B-P5-002 | B | Interface | docs/03-specs/data/02-canonical-event-contract.md, docs/03-specs/data/samples/canonical-events.sample.jsonl | Role B (konsumen) + reviewer B | Lanjut memakai versi kontrak terakhir yang disetujui + mock; perubahan kontrak hanya lewat change request. |
| A-P5-006 | A | B-P5-006 | B | Hard | pipeline/src/.../modes/backfill.py | Role B (konsumen) + reviewer C | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P5-007 | A | X-P5-901 | B | Hard | pipeline/src/.../modes/incremental.py | Role B (konsumen) + reviewer C | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P5-008 | A | X-P5-901 | B | Hard | pipeline/tests/ | Role B (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| B-P5-004 | B | C-P6-006 | C | Interface | db/src/.../runlog.py | Role C (konsumen) + reviewer C | Lanjut memakai versi kontrak terakhir yang disetujui + mock; perubahan kontrak hanya lewat change request. |
| B-P5-001 | B | C-P6-007 | C | Hard | db/migrations/0001_*.cql, db/scripts/migrate.* | Role C (konsumen) + reviewer A | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| B-P5-003 | B | C-P6-007 | C | Interface | db/src/.../aggregates.py | Role C (konsumen) + reviewer A | Lanjut memakai versi kontrak terakhir yang disetujui + mock; perubahan kontrak hanya lewat change request. |
| A-P5-009 | A | D-P6-004 | D | Soft | pipeline/resources/boundaries/provinces-simplified.geojson | Role D (konsumen) + reviewer D | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |
| C-P6-007 | C | D-P6-007 | D | Hard | api/src/.../repositories/cassandra.py | Role D (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| C-P6-010 | C | D-P6-008 | D | Interface | api/ endpoint | Role D (konsumen) + reviewer D | Lanjut memakai versi kontrak terakhir yang disetujui + mock; perubahan kontrak hanya lewat change request. |
| D-P6-007 | D | X-P6-901 | B | Hard | Checklist mock-to-real terisi | Role B (konsumen) + reviewer C | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| C-P6-008 | C | X-P6-901 | B | Hard | api/tests/ | Role B (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P5-007 | A | C-P7-003 | C | Hard | pipeline/src/.../modes/incremental.py | Role C (konsumen) + reviewer C | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| C-P7-002 | C | X-P7-901 | B | Hard | deploy/cloud/ | Role B (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| C-P7-003 | C | X-P7-901 | B | Hard | deploy/cloud/ (service poller) | Role B (konsumen) + reviewer A | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| D-P7-001 | D | X-P7-901 | B | Hard | web/e2e/ | Role B (konsumen) + reviewer C | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P7-001 | A | X-P7-901 | B | Hard | Laporan idempotensi di pipeline/README.md | Role B (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| C-P7-001 | C | X-P7-901 | B | Hard | deploy/scripts/smoke_e2e.* | Role B (konsumen) + reviewer A | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P7-004 | A | X-P7-902 | B | Hard | PR perbaikan | Role B (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| C-P7-005 | C | X-P7-902 | B | Hard | PR perbaikan | Role B (konsumen) + reviewer D | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| D-P7-003 | D | X-P7-902 | B | Hard | PR perbaikan | Role B (konsumen) + reviewer C | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| D-P7-002 | D | X-P7-902 | B | Hard | Daftar perbaikan + perbaikan | Role B (konsumen) + reviewer A | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P7-002 | A | X-P7-902 | B | Soft | pipeline/src/.../reports/ | Role B (konsumen) + reviewer B | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |
| C-P8-001 | C | D-P8-002 | D | Hard | README.md, docs/08-delivery/api-deploy.md | Role D (konsumen) + reviewer A | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P8-001 | A | D-P8-002 | D | Hard | docs/08-delivery/data.md | Role D (konsumen) + reviewer B | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| B-P8-001 | B | D-P8-002 | D | Hard | docs/08-delivery/database.md | Role D (konsumen) + reviewer A | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| C-P8-002 | C | D-P8-002 | D | Hard | docs/08-delivery/api-deploy.md | Role D (konsumen) + reviewer D | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P8-001 | A | X-P8-901 | B | Soft | docs/08-delivery/data.md | Role B (konsumen) + reviewer B | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |
| C-P8-002 | C | X-P8-901 | B | Soft | docs/08-delivery/api-deploy.md | Role B (konsumen) + reviewer D | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |
| D-P8-001 | D | X-P8-901 | B | Soft | docs/08-delivery/ui.md, docs/08-delivery/demo-script.md | Role B (konsumen) + reviewer C | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |
| D-P8-001 | D | A-P8-002 | A | Soft | docs/08-delivery/ui.md, docs/08-delivery/demo-script.md | Role A (konsumen) + reviewer C | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |
| D-P8-002 | D | X-P8-902 | B | Hard | docs/08-delivery/index.md, docs/08-delivery/acceptance-checklist.md | Role B (konsumen) + reviewer C | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| A-P8-002 | A | X-P8-902 | B | Soft | Presentasi | Role B (konsumen) + reviewer B | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |
| D-P8-003 | D | X-P8-902 | B | Soft | Video demo | Role B (konsumen) + reviewer A | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |

## 3. Dependensi dalam peran yang sama

| Dari | Ke | Peran | Jenis |
|---|---|---|---|
| A-P1-002 | A-P1-003 | A | Hard |
| A-P1-002 | A-P1-004 | A | Hard |
| A-P1-006 | A-P1-004 | A | Soft |
| A-P1-003 | A-P1-005 | A | Hard |
| A-P1-002 | A-P1-007 | A | Hard |
| A-P1-002 | A-P1-008 | A | Soft |
| A-P1-004 | A-P1-009 | A | Hard |
| A-P1-004 | A-P1-010 | A | Hard |
| A-P1-005 | A-P1-010 | A | Hard |
| A-P1-007 | A-P1-010 | A | Hard |
| A-P1-009 | A-P1-010 | A | Hard |
| D-P1-001 | D-P2-001 | D | Hard |
| D-P2-001 | D-P2-002 | D | Hard |
| D-P2-002 | D-P2-003 | D | Hard |
| B-P2-001 | X-P2-901 | B | Hard |
| B-P2-001 | B-P3-001 | B | Hard |
| A-P1-003 | A-P3-001 | A | Hard |
| A-P2-001 | A-P3-001 | A | Soft |
| A-P3-001 | A-P3-002 | A | Soft |
| A-P1-009 | A-P3-002 | A | Hard |
| B-P3-001 | B-P3-002 | B | Hard |
| B-P3-002 | B-P3-003 | B | Hard |
| C-P1-001 | C-P3-001 | C | Soft |
| C-P2-001 | C-P3-001 | C | Soft |
| D-P2-001 | D-P3-001 | D | Hard |
| D-P2-002 | D-P3-001 | D | Soft |
| C-P2-001 | C-P3-002 | C | Hard |
| C-P3-001 | C-P3-003 | C | Hard |
| B-P3-002 | B-P3-004 | B | Soft |
| B-P3-002 | X-P3-901 | B | Hard |
| B-P3-003 | X-P3-901 | B | Hard |
| B-P3-004 | X-P3-901 | B | Soft |
| C-P4-001 | C-P4-004 | C | Hard |
| B-P4-001 | B-P4-002 | B | Hard |
| A-P1-004 | A-P4-001 | A | Soft |
| D-P4-001 | D-P4-002 | D | Hard |
| B-P4-001 | X-P4-901 | B | Hard |
| A-P4-001 | A-P5-001 | A | Hard |
| A-P5-001 | A-P5-002 | A | Soft |
| A-P3-002 | A-P5-002 | A | Hard |
| A-P5-002 | A-P5-003 | A | Hard |
| A-P5-002 | A-P5-004 | A | Soft |
| A-P5-003 | A-P5-005 | A | Hard |
| A-P5-004 | A-P5-005 | A | Hard |
| A-P5-005 | A-P5-006 | A | Hard |
| A-P5-006 | A-P5-007 | A | Hard |
| A-P5-005 | A-P5-008 | A | Hard |
| A-P5-004 | A-P5-009 | A | Hard |
| A-P5-007 | A-P5-010 | A | Hard |
| B-P4-001 | B-P5-001 | B | Hard |
| B-P5-001 | B-P5-002 | B | Hard |
| B-P5-002 | B-P5-003 | B | Hard |
| B-P3-003 | B-P5-003 | B | Hard |
| B-P5-001 | B-P5-004 | B | Hard |
| B-P5-003 | B-P5-005 | B | Hard |
| B-P5-003 | B-P5-006 | B | Hard |
| B-P5-005 | B-P5-007 | B | Hard |
| B-P5-005 | X-P5-901 | B | Hard |
| B-P5-006 | X-P5-901 | B | Hard |
| C-P6-001 | C-P6-002 | C | Hard |
| C-P3-002 | C-P6-002 | C | Interface |
| C-P6-002 | C-P6-003 | C | Hard |
| C-P6-002 | C-P6-004 | C | Hard |
| C-P6-002 | C-P6-005 | C | Hard |
| C-P6-002 | C-P6-006 | C | Hard |
| C-P6-003 | C-P6-007 | C | Hard |
| C-P6-004 | C-P6-007 | C | Hard |
| C-P6-005 | C-P6-007 | C | Hard |
| C-P6-006 | C-P6-007 | C | Hard |
| C-P6-007 | C-P6-008 | C | Hard |
| C-P6-008 | C-P6-009 | C | Hard |
| C-P6-007 | C-P6-010 | C | Hard |
| D-P4-002 | D-P6-001 | D | Hard |
| D-P6-001 | D-P6-002 | D | Hard |
| D-P6-001 | D-P6-003 | D | Hard |
| D-P6-001 | D-P6-004 | D | Hard |
| D-P6-001 | D-P6-005 | D | Hard |
| D-P6-002 | D-P6-006 | D | Hard |
| D-P6-003 | D-P6-006 | D | Hard |
| D-P6-004 | D-P6-006 | D | Hard |
| D-P6-006 | D-P6-007 | D | Hard |
| D-P6-007 | D-P6-008 | D | Hard |
| D-P6-006 | D-P6-009 | D | Hard |
| X-P5-901 | X-P6-901 | B | Hard |
| A-P5-008 | A-P7-001 | A | Hard |
| A-P7-001 | A-P7-002 | A | Hard |
| A-P7-001 | A-P7-003 | A | Hard |
| B-P3-004 | B-P7-001 | B | Hard |
| B-P7-001 | B-P7-002 | B | Hard |
| B-P4-002 | B-P7-003 | B | Hard |
| B-P7-002 | B-P7-003 | B | Soft |
| C-P3-003 | C-P7-002 | C | Hard |
| C-P7-002 | C-P7-003 | C | Hard |
| C-P7-002 | C-P7-004 | C | Hard |
| A-P7-001 | A-P7-004 | A | Soft |
| B-P7-002 | B-P7-004 | B | Soft |
| C-P7-004 | C-P7-005 | C | Soft |
| D-P7-001 | D-P7-003 | D | Soft |
| B-P7-002 | X-P7-901 | B | Hard |
| X-P7-901 | X-P7-902 | B | Hard |
| B-P7-004 | X-P7-902 | B | Hard |
| D-P8-001 | D-P8-002 | D | Hard |
| B-P8-001 | X-P8-901 | B | Soft |
| D-P8-001 | D-P8-003 | D | Hard |
| X-P8-901 | X-P8-902 | B | Soft |

## 4. Dependensi ke gerbang (blocking)

| Gerbang | Tugas yang menunggu |
|---|---|
| GATE-EP | C-P4-001, D-P4-003, B-P4-001 |
| GATE-G1 | D-P2-001, A-P2-001 |
| GATE-G2 | X-P3-901 |
| GATE-G3 | A-P5-001, A-P5-002, A-P5-004, B-P5-001, C-P6-001, D-P6-001 |
| GATE-G4 | A-P5-001, A-P5-002, A-P5-004, B-P5-001, C-P6-001, D-P6-001 |
| GATE-G5 | A-P7-001, B-P7-001, B-P7-003 |
| GATE-G6 | C-P7-001, C-P7-002, D-P7-001, D-P7-002, A-P7-004, B-P7-004, C-P7-005, D-P7-003, A-P8-002 |
| GATE-G7 | C-P8-001, A-P8-001, B-P8-001, C-P8-002, D-P8-001, X-P8-901 |
| GATE-G8 | — |

## 5. Perlakuan bila dependensi terlambat (default per jenis)

| Jenis | Tindakan |
|---|---|
| Hard | Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai. |
| Soft | Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai. |
| Interface | Lanjut memakai versi kontrak terakhir yang disetujui + mock; perubahan kontrak hanya lewat change request. |
| Review | Pekerjaan boleh lanjut, tetapi tidak boleh di-merge/diterima sebelum review. |
| Human approval | STOP. Tunggu keputusan tim; koordinator menagih keputusan paling lambat akhir hari. |
