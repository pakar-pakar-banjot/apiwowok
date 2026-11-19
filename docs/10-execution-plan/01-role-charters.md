# 01 — Role Charters

> Status: `RECOMMENDATION` — menunggu GATE-EP. Peran R1–R4 berasal dari [charter §9](../00-discovery/01-project-charter.md#9-tim-dan-peran), yang sudah disetujui di G0. Dokumen ini merinci peran tersebut, bukan menggantinya.

## 0. Penugasan anggota (HD-01)

Ditetapkan tim pada **2026-11-19** (GATE-EP). Peran dibagikan langsung oleh tim; matriks skill tidak dipakai.

| Peran | Anggota | Kapasitas |
|---|---|---|
| A — R1 Data Engineering / ETL | **Lanang** | 4 jam/hari; **±5 jam/hari pada D9–D15** (HD-07b) |
| B — R2 Cassandra & Data Platform **+ koordinator integrasi** (HD-02) | **Abi Funn** | 4 jam/hari |
| C — R3 Backend, Integration & DevOps | **Zita** | 4 jam/hari; **±5 jam/hari pada D9–D15** (HD-07b) |
| D — R4 Frontend, Visualization & Delivery | **Abigail** | 4 jam/hari |

Aturan penugasan:
1. Tidak ada reviewer wajib antar peran (keputusan 2026-11-19, menggantikan HD-06). Tugas selesai saat seorang manusia, anggota tim mana pun, mengisi `disetujui:`.
2. Koordinator integrasi adalah tanggung jawab tambahan, bukan peran kelima ([09 §2](09-risk-capacity-plan.md#2-pemilihan-koordinator-integrasi)).
3. Di WBS, prompt agen, dan tracker, tugas tetap ditulis dengan kode peran (A–D / R1–R4), bukan nama. Bila penugasan berubah, cukup tabel ini yang diubah.

---

## A — R1 Data Engineering / ETL

**Tujuan:** setiap deteksi FIRMS yang masuk sistem dapat dilacak ke file sumbernya, divalidasi, diperkaya provinsi, punya identitas deterministik, dan dimuat secara idempoten, dalam dua mode (backfill dan incremental).

| Aspek | Isi |
|---|---|
| Tanggung jawab | Inspeksi sumber & profiling (P1); semantik data (P2); kontrak canonical event & spesifikasi ETL (P3); tooling Python & skeleton pipeline (P4); extractor, validasi, normalisasi, pengayaan spasial, dedup, backfill, incremental, test ETL (P5); idempotensi & laporan DQ (P7); dokumentasi data & perakitan presentasi (P8). |
| Kepemilikan eksklusif | `pipeline/`, `docs/01-dataset/`, `docs/03-specs/data/`, `docs/08-delivery/data.md`, `ruff.toml`, `.pre-commit-config.yaml`, `scratch/phase1/`, `data/` (lokal) |
| Bukan tanggung jawab | Definisi tabel CQL, writer Cassandra (B); kontrak API (C); UI (D). **Tidak boleh** mengubah file di `db/` atau `api/`. |
| Output utama | Data dictionary, laporan profil, aturan DQ, canonical event contract v1 + sampel, ETL spec, paket `pipeline` dua mode, test ETL & harness idempotensi, GeoJSON batas untuk web, dokumentasi pipeline |
| Skill inti | Python/Pandas, data spasial, desain idempoten, pengujian berbasis data |
| Ukuran sukses | (1) Dua run dengan input sama → jumlah baris & checksum identik. (2) Setiap baris yang ditolak punya reason code. (3) Poller incremental berjalan tanpa duplikat. (4) 0 MAP_KEY di log. |
| Beban rencana | 63,4 jam PERT dari kapasitas 87 jam (73%). **Pemilik rantai kritis D9–D14** (ETL). |

## B — R2 Cassandra & Data Platform (+ koordinator integrasi)

**Tujuan:** model data Cassandra yang sepenuhnya query-driven, dengan setiap tabel melayani query aplikasi yang terdokumentasi, plus bukti eksperimen yang dapat direproduksi.

| Aspek | Isi |
|---|---|
| Tanggung jawab | Estimasi volume (P1); kebutuhan query (P2); access patterns, model data, strategi agregat, rencana eksperimen (P3); Cassandra dev & smoke 3 node (P4); migrasi skema, writer idempoten, builder agregat, run log, test DB, load penuh (P5); eksperimen & laporan (P7); dokumentasi DB (P8). |
| Kepemilikan eksklusif | `db/`, `experiments/`, `docs/03-specs/database/`, `docs/08-delivery/database.md` |
| Bukan tanggung jawab | Semantik field sumber (A); query endpoint/repository baca (C); konfigurasi `docker-compose.yml` (C, dari fragmen B). |
| Output utama | Access pattern matrix, logical/physical model, `schema-v1.cql`, migrasi bernomor, library writer & agregat, test per access pattern, rencana & laporan eksperimen |
| Skill inti | CQL, pemodelan partisi, Docker, metodologi benchmark |
| Ukuran sukses | (1) Setiap tabel ↔ ≥1 Q-xx. (2) 0 `ALLOW FILTERING` dan 0 counter table untuk agregat. (3) Agregat = jumlah detail. (4) Eksperimen dapat dijalankan ulang dari README. |
| Beban rencana | 52,6 jam teknis + ±14,6 jam koordinasi = 67,2 jam dari 80 jam (84%) |

**Tanggung jawab koordinator (dirangkap B, HD-02 disetujui):** tugas `X-Pn-9xx`, yaitu paket gerbang, pencatatan keputusan, pembaruan `docs/STATUS.md`, checkpoint D10/D13/D17, dan perakitan laporan. Koordinator **tidak** mengerjakan integrasi teknis milik peran lain. Integrasi dilakukan pemilik masing-masing (C-P6-007, D-P6-007, C-P7-001). Koordinator juga memelihara `docs/10-execution-plan/`, `docs/03-specs/README.md`, dan `docs/change-requests/`.

## C — R3 Backend, Integration & DevOps

**Tujuan:** API yang hanya mengekspos query yang disetujui, dengan kontrak OpenAPI sebagai satu-satunya sumber bentuk data untuk frontend; ditambah lingkungan lokal dan cloud yang dapat direproduksi.

| Aspek | Isi |
|---|---|
| Tanggung jawab | Inventaris toolchain & opsi cloud (P1); NFR (P2); arsitektur, ADR, OpenAPI, ADR deployment/keamanan (P3); kerangka repo, CODEOWNERS, Compose, CI (P4); FastAPI, repository fake & Cassandra, endpoint, test API (P6); smoke E2E, deploy cloud, poller cloud, keamanan (P7); panduan instalasi & dokumentasi API/deploy (P8). |
| Kepemilikan eksklusif | `api/`, `deploy/`, `docker-compose*.yml`, `.github/`, `.env.example`, `.gitignore`, `README.md` (root), `docs/03-specs/api/`, `docs/03-specs/architecture/`, `docs/02-requirements/02-non-functional-requirements.md`, `docs/08-delivery/api-deploy.md` |
| Bukan tanggung jawab | Skema Cassandra (B): repository memakai query B, tidak membuat tabel. Komponen UI (D). Isi AGENTS.md (D). |
| Output utama | `openapi.yaml` v1, ADR-001…004, Compose sehat, CI, layanan FastAPI, test kontrak, deployment HTTPS dengan Cassandra privat |
| Skill inti | FastAPI, OpenAPI, Docker, Linux/cloud, keamanan dasar |
| Ukuran sukses | (1) Semua respons lolos validasi terhadap `openapi.yaml`. (2) `docker compose up` sehat di mesin bersih. (3) Port Cassandra tertutup dari internet (bukti port scan). (4) Poller cloud tercatat ≥3 poll berturut-turut. |
| Beban rencana | 64,6 jam dari 87 jam (74%). **Pemilik rantai kritis D15–D18** (deploy cloud). |

## D — R4 Frontend, Visualization & Delivery

**Tujuan:** dashboard berbahasa Indonesia yang hanya memakai field dari kontrak API, menampilkan disclaimer ilmiah dan kesegaran data, dan menangani state loading, kosong, dan error.

| Aspek | Isi |
|---|---|
| Tanggung jawab | Draf user stories (P1); FR, acceptance criteria, kunci MVP (P2); UI spec + wireframe (P3); AGENTS.md/CLAUDE.md, scaffold React, mock API (P4); seluruh dashboard + test (P6); E2E UI & review terminologi (P7); dokumentasi UI, skrip demo, video, checklist final (P8). |
| Kepemilikan eksklusif | `web/`, `AGENTS.md`, `CLAUDE.md`, `docs/02-requirements/` (kecuali file NFR), `docs/03-specs/ui/`, `docs/08-delivery/` (index, ui, acceptance, demo) |
| Bukan tanggung jawab | Bentuk respons API (C). Frontend **tidak boleh** menambah field yang tidak ada di kontrak. Tulisan teknis peran lain di dokumen final: D merakit, bukan menulis semuanya. |
| Output utama | FR + AC, UI spec, mock layer, dashboard (KPI, timeline, ranking, peta, status), test unit & E2E, skrip demo, checklist penerimaan |
| Skill inti | React/TypeScript, Leaflet, UX, penulisan requirements |
| Ukuran sukses | (1) Semua halaman Must berjalan di data nyata tanpa error konsol. (2) Disclaimer & waktu pembaruan tampil di setiap halaman. (3) 0 label "kebakaran" untuk deteksi. (4) Checklist penerimaan G8 lengkap dengan bukti. |
| Beban rencana | 63,0 jam dari 80 jam (79%). Dokumentasi & video di rantai kritis D19–D20; D21 kosong sebagai buffer. |

---

## RACI ringkas per deliverable

R = Responsible, A = Accountable, C = Consulted, I = Informed. Setiap deliverable punya tepat satu **A**. Koordinator = B (HD-02).

| Deliverable | A (R1) | B (R2) | C (R3) | D (R4) |
|---|---|---|---|---|
| Profil dataset & aturan DQ | **A/R** | C | I | I |
| Kebutuhan query (Q-xx) | C | **A/R** | C | C |
| FR, AC, kunci MVP | C | C | C | **A/R** |
| NFR | C | C | **A/R** | C |
| Canonical event contract | **A/R** | C | I | I |
| Access patterns + model data + CQL | C | **A/R** | C | I |
| OpenAPI | I | C | **A/R** | C |
| UI spec | I | I | C | **A/R** |
| Docker Compose, CI, repo skeleton | C | C | **A/R** | C |
| AGENTS.md / CLAUDE.md | C | C | C | **A/R** |
| Pipeline ETL | **A/R** | C | I | I |
| Writer & agregat Cassandra | C | **A/R** | C | I |
| API | I | C | **A/R** | C |
| Dashboard | I | I | C | **A/R** |
| Eksperimen Cassandra | C | **A/R** | I | I |
| Deploy cloud & keamanan | I | C | **A/R** | I |
| Checklist penerimaan final | C | C | C | **A/R** |
| Paket gerbang & STATUS.md | I | **A/R** (koordinator) | I | I |
| Laporan / presentasi / video (manusia) | presentasi **A/R** | laporan **A/R** | C | video **A/R** |
