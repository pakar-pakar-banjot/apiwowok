# 09 — Risk & Capacity Plan

> Status: `RECOMMENDATION`. Semua angka di dokumen ini berasal dari `tools/build_plan.py`, dan dapat dijalankan ulang untuk memverifikasinya. Estimasi adalah **jam kerja manusia**, bukan hasil ukur.

## 1. Revisi rencana hasil self-review

Generator memeriksa beberapa hal secara otomatis: setiap tugas punya satu pemilik, reviewer ≠ pemilik, tidak ada siklus, setiap dependensi ada, tugas Fase 5–8 menunggu gerbangnya, Must tidak bergantung pada Should, file berada di area pemilik, dan semua tugas selesai ≤ D21.

| Run | Hasil | Penyebab | Perubahan |
|---|---|---|---|
| v0 (estimasi awal) | **Selesai D28**; beban 80–87 jam per peran (100–109% kapasitas); 37 masalah | (a) Rantai G1→G2→G3 serial, sehingga G3 baru D12. (b) Review Fase 1 menumpuk di R1. (c) Spesifikasi + harness menumpuk di R3 pada D2–D8. | — |
| v1 | Selesai D22–D24, tergantung koordinator | Bug: dua tugas Fase 5 tidak menunggu G3; tugas Should menyela Must | (1) Estimasi P1 = review/keputusan saja (agen mengerjakan analisis). (2) Spesifikasi Fase 3 mulai dari draf Fase 2 (sesuai charter §10). (3) Estimasi implementasi mengasumsikan agen menulis kode (A-EP-01). (4) Tooling Python R3→R1. (5) Dokumen digabung/diperkecil. |
| **v2 (final)** | **Selesai D21, `ISSUES: 0`**, 2 Should ditandai kandidat dipotong | — | Gate ancestry diperbaiki; Should dijadwalkan di lintasan kedua; AGENTS.md R3→R4; ADR deployment dan rencana eksperimen mulai paling cepat D9 (baru dibutuhkan ≥D12) |

Nilai estimasi v0 tetap tersimpan di pemanggilan `t()` dan nilai v1 di `REV1_EST`, sehingga perubahan dapat diaudit.

## 2. Pemilihan koordinator integrasi

Hasil penjadwalan dengan rencana final (v2), kapasitas dasar 4 jam/hari, seperti saat keputusan diambil. Dengan HD-07(b), R2 tetap satu-satunya opsi tanpa masalah (G6 D14, selesai D20); opsi lain 11–14 masalah.

| Koordinator | Integrasi lokal (G6) | Selesai | Masalah |
|---|---|---|---|
| R1 (A) | D16 | D22 | 5 |
| **R2 (B)** | **D15** | **D21** | **0** |
| R3 (C) | D16 | D22 | 4 |
| R4 (D) | D16 | D23 | 4 |

R1 dan R3 adalah pemilik rantai kritis (ETL D9–D15, deploy D16–D19), sedangkan R4 penuh di P2, P6, dan P8. Karena itu R2 direkomendasikan. **Keputusan HD-02 (2026-11-19): R2 — Abi Funn.**

## 3. Skenario kapasitas

| Skenario | G3/G4 | G5/G6 (integrasi) | G7 | G8 | Buffer akhir |
|---|---|---|---|---|---|
| **4 jam/hari (dasar, OQ-03)** | D8 | **D15** | D19 | **D21** | ±0 hari untuk R2 dan R4 |
| **HD-07 (b) — DISETUJUI:** R1 & R3 ±5 jam/hari D9–D15, lainnya 4 | D8 | **D14** | D18 | **D20** | 1 hari |
| 5 jam/hari (semua peran, semua hari) | D7 | **D13** | D17 | D19 | 2 hari |
| 6 jam/hari | D6 | D11 | D17 | D19 | 2 hari (G7 tertahan freeze D17) |

Cara reproduksi: run default = HD-07(b); `--no-boost` = 4 jam/hari rata; `--hours 5` = 5 jam/hari rata. Run skenario hanya mencetak hasil ke konsol; tidak ada file yang ditulis.

**Keputusan HD-07** (2026-11-19: tim memilih **(b)**, dengan (c) sebagai cadangan):
- **(a)** Terima D15/D18 pada 4 jam/hari, tanpa buffer akhir.
- **(b)** Rekomendasi: naikkan menjadi ±5 jam/hari pada **D9–D15** saja, untuk anggota rantai kritis (R1, lalu R3).
- **(c)** Potong ruang lingkup sesuai urutan descoping (D-P2-003). Yang pertama dipotong adalah semua *Should* (±17 jam tim), lalu fitur kab/kota dan histogram FRP.

## 4. Beban & bottleneck

| Peran | Beban (jam) | Utilisasi | Bottleneck |
|---|---|---|---|
| R1 | 63,4 / 87 | 73% | **26,5 jam ETL berurutan D9–D14**: rantai kritis terpanjang |
| R2 + koordinator | 67,2 / 80 | 84% | P3 (model data) di jalur kritis G2/G3; ±14,6 jam koordinasi |
| R3 | 64,6 / 87 | 74% | D2–D8 (NFR, arsitektur, OpenAPI, harness); D15–D18 deploy cloud |
| R4 | 63,0 / 80 | 79% | P6 terbesar (26,4 jam); dokumentasi & video D19–D20 |
| Tim | 258,1 / 334 | 77% | Buffer ±76 jam, tetapi **tidak merata dan sebagian besar tidak berada di jalur kritis** |

## 5. Risiko baru dari rencana ini

Melengkapi register Fase 0 (R-01…R-27), tidak menggantikannya.

| ID | Risiko | P | D | Pemicu dini | Mitigasi | Kontingensi | Pemilik |
|---|---|---|---|---|---|---|---|
| RC-01 | **Asumsi A-EP-01 salah:** implementasi dengan agen tidak secepat estimasi v1 | 2 | 3 | Tugas P5/P6 pertama melewati estimasi P (pesimis) | Ukur tugas pertama per peran; koordinator membandingkan aktual vs PERT setiap hari | HD-07 opsi (b) atau (c) | Koordinator |
| RC-02 | Rantai kritis R1 (ETL) terlambat | 2 | 3 | A-P5-002 belum merge pada D11 | Pairing B→A di A-P5-005/006 (B longgar D13–D14); fixture siap sejak P4 | C/D tetap di mock; G6 mundur maksimal D16 | R1 |
| RC-03 | Dimensi filter (confidence/satelit) tidak ada di kunci agregat, sehingga filter tidak bisa dilayani tanpa scan | 2 | 3 | Q-xx timeline/ranking punya filter tetapi tabel agregat tidak | Pertanyaan wajib di B-P3-001 ([06 §C](06-interface-contracts.md#c-cassandra--backend)) | Batasi filter di agregat; filter penuh hanya di peta | R2 |
| RC-04 | Kontrak berubah setelah G3 tanpa CR, sehingga mock dan nyata tidak cocok | 2 | 2 | Diff `openapi.yaml` tanpa CR | CODEOWNERS + contract test di CI | Checklist mock-to-real; perbaikan lewat CR | R3 |
| RC-05 | Koordinator kelebihan beban di D4–D8 (P3 + paket gerbang) | 2 | 2 | Paket G2/G3 terlambat >½ hari | Paket gerbang disiapkan agen; persetujuan asinkron | Pindahkan X-P3-901 ke R1 | Koordinator |
| RC-06 | Lisensi BIG tidak jelas, sehingga batas tidak bisa di-commit/dipublikasikan | 2 | 2 | Belum ada jawaban HD-08 pada D9 | Snapshot lokal + checksum; cadangan HDX 34 provinsi | Pakai HDX + catatan keterbatasan Papua | R1 |
| RC-07 | Agen membuat file di luar area atau dua agen menyentuh file yang sama | 2 | 2 | PR menyentuh path milik peran lain | Worktree per tugas, CODEOWNERS, larangan di prompt | Tolak PR, pisahkan perubahan | R4 (AGENTS.md) |
| RC-08 | Tanggal presentasi/pengumpulan berbeda dari asumsi (HD-23: presentasi 2026-12-10) | 1 | 2 | Informasi dosen | G8 direncanakan D20, sehingga ada 2 hari sebelum presentasi | Hitung ulang dengan `LAST_DAY` | Koordinator |
| RC-09 | Proses background Fase 1 terus memakai kuota FIRMS | 1 | 1 | — | Keputusan HD-22 | Hentikan proses | R1 |

Risiko Fase 0 yang paling terdampak rencana ini: **R-14** (integrasi terlambat) kini direncanakan D14, bukan D13; **R-23** (deploy cloud) sekarang berada di rantai kritis; **R-02** (overhead proses) dimitigasi dengan Fase 2 dan 3 yang tumpang tindih.

## 6. Risiko integrasi & mitigasinya

| Titik integrasi | Risiko | Mitigasi terjadwal |
|---|---|---|
| Canonical event → writer (A↔B) | Tipe/nullability berbeda | Sampel JSONL + validasi skema (A-P3-001); writer diuji dengan sampel yang sama (B-P5-002) |
| Agregat → API (B↔C) | Semantik tanggal lokal berbeda | Aturan SEM-xx (A-P2-001) dirujuk di B-P3-003 dan C-P3-002; test konsistensi agregat vs detail (B-P5-005) |
| API → UI (C↔D) | Field tambahan / hilang | Mock dari contoh OpenAPI (D-P4-002) + contract test kedua sisi |
| Lokal → cloud (C) | Perbedaan konfigurasi | Image yang sama, konfigurasi lewat env (ADR-002), smoke E2E yang sama (C-P7-001) |
| Poller → status UI (A↔C↔D) | Kegagalan poll tidak terlihat | Run log (B-P5-004) → endpoint status (C-P6-006) → indikator (D-P6-005) |
