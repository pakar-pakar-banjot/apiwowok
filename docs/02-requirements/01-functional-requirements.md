# 01 — Functional Requirements (D-P2-001)

> Fase 2 · Draf agen 2026-11-25 · Pemilik: R4 (Abigail) · Status: `RECOMMENDATION`, menunggu G2
> Input: [draf user stories D-P1-001](00-draft-user-stories.md) (disetujui Abigail 2026-11-25), keputusan G1 (HD-08 … HD-11, [12](../10-execution-plan/12-human-decision-register.md)), [charter §3–§6](../00-discovery/01-project-charter.md#6-ruang-lingkup-awal-dan-mvp), [data dictionary](../01-dataset/02-data-dictionary.md), [aturan DQ](../01-dataset/06-data-quality-rules.md).
> Serah-terima: R2 (Abi Funn) untuk B-P2-001 (access patterns Q-xx); R3 (Zita) untuk NFR (C-P2-001) dan OpenAPI.
> Label: [legenda](../00-discovery/README.md#label-status-informasi). Angka target (batas titik, latensi, ambang basi) **tidak** ditetapkan di sini; itu wewenang NFR (C-P2-001, HD-13).

## 1. Konvensi

- **ID:** `FR-Gn` = aturan umum lintas halaman; `FR-nn` = requirement per fitur. ID tidak dipakai ulang bila FR dihapus.
- **Format:** setiap FR punya pernyataan ("Sistem harus …"), persona, prioritas MoSCoW, fitur charter §6.1 (#1–#12), dan sumber.
- **Prioritas** mengikuti charter §6.1. FR yang menurunkan prioritas fitur ditandai di kolom catatan.
- **Persona** (OQ-19, dari [D-P1-001](00-draft-user-stories.md#persona-oq-19)): **AL** analis lingkungan (primer), **PN** peneliti (primer), **PD** pemerintah daerah (sekunder), **OP** operator sistem (internal).
- **Penanda:** ⚖️ = butuh keputusan manusia (lihat §5); 📏 = angka ditetapkan di NFR (C-P2-001).

## 2. Aturan umum (berlaku untuk fitur UI #1–#8 dan #12)

| ID | Pernyataan | Persona | MoSCoW | Fitur | Sumber |
|---|---|---|---|---|---|
| FR-G1 | Semua label, judul, dan tooltip harus memakai istilah "deteksi hotspot" / "jumlah deteksi hotspot", tidak pernah "kebakaran". | AL, PN, PD | Must | #1–#8 | Charter §3; US semua |
| FR-G2 | Setiap halaman harus menampilkan disclaimer ilmiah dan waktu pembaruan data terakhir. Teks final disclaimer ⚖️ (HD-25). | AL, PN, PD | Must | #1–#8, #12 | Charter §3, §4 |
| FR-G3 | Seluruh teks UI harus berbahasa Indonesia. | AL, PD | Must | #1–#8 | OQ-20 |
| FR-G4 | Tanggal yang ditampilkan dan dipakai untuk agregasi harian/bulanan harus tanggal lokal provinsi deteksi (WIB/WITA/WIT); penyimpanan tetap UTC. Aturan untuk agregat nasional ⚖️ (Q-4). | AL, PN | Must | #1, #3, #4, #8 | OQ-08 |
| FR-G5 | Setiap halaman harus menampilkan atribusi NASA FIRMS, BIG (batas wilayah), dan penyedia basemap. | PN | Must | #1–#8 | Prompt peran D; HD-08 |
| FR-G6 | Filter global (rentang tanggal, provinsi, confidence, satelit) harus berlaku untuk semua panel di halaman dan tersinkron ke URL sehingga tautan dapat dibagikan. | AL, PD | Must | #1–#4, #6, #8 | US-06a, US-06b, US-08 |
| FR-G7 | Tanggal yang ditandai `INCOMPLETE_DAY` (DQ-12) harus ditampilkan sebagai "data tidak lengkap", bukan "0 deteksi". | AL, PN | Must | #1, #3, #5 | DQ-12, HD-11 |
| FR-G8 | Setiap panel harus punya state memuat, kosong, dan galat yang dapat dibedakan pengguna. | AL, PD | Must | #1–#8 | Prompt peran D |

## 3. Requirement per fitur

### #1 Ringkasan nasional/regional — Must

| ID | Pernyataan | Persona | MoSCoW | Sumber |
|---|---|---|---|---|
| FR-01 | Halaman ringkasan harus menampilkan total deteksi hotspot, jumlah provinsi dengan ≥1 deteksi, dan timeline nasional untuk rentang tanggal terpilih. Periode default ⚖️ (Q-1). | AL | Must | US-01; charter §6.1 #1 |
| FR-02 | Halaman ringkasan harus menampilkan secara terpisah jumlah deteksi berstatus `OUTSIDE` (di luar poligon provinsi) dalam periode terpilih, dengan penjelasan singkat. | AL, PN | Must | OQ-11, DQ-07 |

### #2 Peta hotspot interaktif — Must

| ID | Pernyataan | Persona | MoSCoW | Sumber |
|---|---|---|---|---|
| FR-03 | Peta harus menampilkan titik deteksi untuk satu provinsi dan rentang tanggal terpilih. Jumlah titik dan panjang rentang dibatasi 📏; bila hasil terpotong, peta harus menampilkan notice beserta jumlah total. | AL | Must | US-02; charter C-10; HD-21 (tanpa query viewport di MVP) |
| FR-04 | Klik titik harus menampilkan detail: waktu akuisisi (UTC dan lokal), satelit, confidence, FRP, `daynight`, tingkat pemrosesan (SP/NRT), versi produk, dan versi batas wilayah. | PN | Must | US-13; FR-24 |

### #3 Timeline — Must

| ID | Pernyataan | Persona | MoSCoW | Sumber |
|---|---|---|---|---|
| FR-05 | Sistem harus menampilkan jumlah deteksi per hari dan per bulan, nasional maupun per provinsi, berdasarkan tanggal lokal (FR-G4). Granularitas default ⚖️ (Q-2). | AL, PD | Must | US-03; charter §6.1 #3 |

### #4 Ranking provinsi — Must

| ID | Pernyataan | Persona | MoSCoW | Sumber |
|---|---|---|---|---|
| FR-06 | Sistem harus menampilkan Top-N provinsi (dari 38 provinsi BIG) berdasarkan jumlah deteksi pada periode dan filter terpilih. Deteksi `OUTSIDE` tidak ikut. Ranking per luas wilayah ⚖️ (Q-3). | AL, PD | Must | US-04; OQ-11; HD-08 |

### #5 Perbandingan periode — Should

| ID | Pernyataan | Persona | MoSCoW | Sumber |
|---|---|---|---|---|
| FR-07 | Sistem harus menampilkan dua periode berdampingan dengan satelit/produk dan versi batas wilayah yang sama untuk kedua periode, disertai catatan metodologi. Perbandingan lintas sensor tidak boleh tersedia. | PN | Should | US-05; charter §3 |

### #6 Filter confidence & satelit — Must

| ID | Pernyataan | Persona | MoSCoW | Sumber |
|---|---|---|---|---|
| FR-08 | Sistem harus menyediakan filter confidence `low`/`nominal`/`high` (dari kode `l`/`n`/`h`) yang berlaku untuk semua panel. Nilai default ⚖️ (HD-12, diputuskan di A-P2-001). Bantuan filter menjelaskan bahwa kelas `low` tidak muncul pada malam hari di Indonesia. | AL | Must | US-06a; OQ-09; data dictionary §`confidence` |
| FR-09 | Sistem harus menyediakan filter satelit NOAA-20, NOAA-21, atau keduanya. Panel menjelaskan bahwa jumlah deteksi bergantung pada jumlah lintasan, dan bahwa NOAA-21 baru tersedia sejak 2023-03-01. | PN | Must | US-06b; OQ-04; HD-09 |
| FR-10 | Sistem harus menghitung semua tipe deteksi secara default dan menyediakan filter opsional untuk mengecualikan tipe non-vegetasi (`type` 1, 2, 3). Filter hanya bermakna untuk data SP; untuk NRT (`type` = null) UI harus menyatakannya sebagai keterbatasan. Prioritas ⚖️ (Q-5). | PN, AL | Should | HD-11; DQ-11; OQ-12 |

### #7 Distribusi FRP — Should

| ID | Pernyataan | Persona | MoSCoW | Sumber |
|---|---|---|---|---|
| FR-11 | Sistem harus menampilkan histogram FRP untuk wilayah dan periode terpilih, dengan filter global yang sama. | PN | Should | US-07; charter §6.1 #7 |

### #8 Eksplorasi regional — Must (digabung ke #1–#4)

| ID | Pernyataan | Persona | MoSCoW | Sumber |
|---|---|---|---|---|
| FR-12 | Pemilih provinsi harus memfilter ringkasan, timeline, dan peta ke provinsi terpilih, menyorot provinsi itu di ranking, dan tersinkron ke URL. Tidak ada halaman provinsi terpisah. | PD | Must | US-08; charter §6.1 #8 |

### #9 Monitoring pipeline — Must (minimal)

| ID | Pernyataan | Persona | MoSCoW | Sumber |
|---|---|---|---|---|
| FR-13 | Setiap run ingest (backfill maupun incremental) harus tercatat dengan waktu mulai/selesai, mode, source ID, file/rentang sumber, status, dan jumlah diterima, ditolak (per reason code DQ), duplikat, serta `OUTSIDE`. | OP | Must | US-09; DQ-01 … DQ-15; O-E1 |
| FR-14 | Sistem harus menyediakan endpoint status pipeline dan halaman sederhana yang menampilkan daftar run terbaru, waktu poll terakhir yang berhasil, dan run yang gagal. | OP | Must | US-09; OQ-22; O-E5 |

### #10 Eksperimen engineering Cassandra — Must (partisi) / Should (3 node)

| ID | Pernyataan | Persona | MoSCoW | Sumber |
|---|---|---|---|---|
| FR-15 | Minimal satu eksperimen partisi/bucketing harus terdokumentasi dengan hipotesis, prosedur, hasil aktual, interpretasi, keterbatasan, dan skrip yang dapat dijalankan ulang. | PN, OP | Must | US-10; O-E3; OQ-13 |
| FR-16 | Eksperimen replikasi dan kegagalan node pada klaster 3 node harus terdokumentasi dengan format yang sama seperti FR-15. | PN, OP | Should | US-10; OQ-14 |

### #11 Hosting di cloud — Must (setelah integrasi lokal)

| ID | Pernyataan | Persona | MoSCoW | Sumber |
|---|---|---|---|---|
| FR-17 | Aplikasi harus dapat diakses lewat HTTPS dari image container yang sama dengan lokal, dan Cassandra tidak boleh terekspos ke publik. Deployment hanya dimulai setelah integrasi lokal berjalan. | AL, OP | Must | US-11; OQ-21; charter §6.2; R-23 |
| FR-18 | Seluruh sistem harus dapat dijalankan dari nol mengikuti README (start layanan + perintah ingest terdokumentasi) dan menghasilkan dashboard berisi data. | OP | Must | US-14; O-E4 |

### #12 Ingestion incremental NRT — Must

| ID | Pernyataan | Persona | MoSCoW | Sumber |
|---|---|---|---|---|
| FR-19 | Poller harus memuat data NRT baru secara berkala (interval 15 menit; angka final 📏) dengan checkpoint waktu dan upsert idempoten, sehingga menjalankan ulang input yang sama tidak mengubah hasil. | AL, OP | Must | US-12; OQ-10; O-E1, O-E5 |
| FR-20 | UI harus menampilkan waktu data terakhir dan peringatan bila data basi (ambang 📏). UI tidak boleh mengklaim data real-time. | AL | Must | US-12; charter §4 |
| FR-21 | Pipeline yang sama harus mendukung mode backfill arsip SP untuk periode 2023-01-01 sampai akhir ketersediaan SP, dengan kode transformasi yang sama dengan mode incremental. | OP, PN | Must | OQ-10; HD-09; charter §6.2 butir 1 |
| FR-22 | Sistem harus memilih satu produk per (satelit, tanggal UTC): SP bila tersedia, NRT sesudahnya. Penggantian NRT→SP dilakukan per tanggal, bukan per deteksi. | PN | Must | HD-10 |
| FR-23 | Penggantian NRT→SP harus dapat dijalankan manual untuk tanggal yang SP-nya sudah terbit. Versi terjadwal otomatis = *Could* (charter §6.4). | OP | Should | OQ-10; charter §6.4 |

### Lintas fitur: provenance

| ID | Pernyataan | Persona | MoSCoW | Fitur | Sumber |
|---|---|---|---|---|---|
| FR-24 | Setiap deteksi harus menyimpan source ID, tingkat pemrosesan (SP/NRT), versi produk, checksum file sumber, dan versi batas wilayah. | PN | Must | #2 (detail titik, FR-04), #9, #12 | US-13; O-E1; HD-08 |

## 4. Matriks traceability fitur ↔ FR

| # | Fitur (charter §6.1) | MoSCoW | FR | Story (D-P1-001) |
|---|---|---|---|---|
| 1 | Ringkasan nasional/regional | Must | FR-01, FR-02, FR-G1, FR-G2, FR-G3, FR-G4, FR-G5, FR-G6, FR-G7, FR-G8 | US-01 |
| 2 | Peta hotspot interaktif | Must | FR-03, FR-04, FR-24, FR-G1, FR-G2, FR-G3, FR-G5, FR-G6, FR-G8 | US-02, US-13 |
| 3 | Timeline hotspot | Must | FR-05, FR-G1, FR-G2, FR-G3, FR-G4, FR-G5, FR-G6, FR-G7, FR-G8 | US-03 |
| 4 | Ranking provinsi | Must | FR-06, FR-G1, FR-G2, FR-G3, FR-G4, FR-G5, FR-G6, FR-G8 | US-04 |
| 5 | Perbandingan periode historis | Should | FR-07, FR-G1, FR-G2, FR-G3, FR-G5, FR-G7, FR-G8 | US-05 |
| 6 | Filter confidence & satelit | Must | FR-08, FR-09, FR-10, FR-G1, FR-G2, FR-G3, FR-G5, FR-G6, FR-G8 | US-06a, US-06b |
| 7 | Visualisasi distribusi FRP | Should | FR-11, FR-G1, FR-G2, FR-G3, FR-G5, FR-G8 | US-07 |
| 8 | Eksplorasi regional | Must | FR-12, FR-G1, FR-G2, FR-G3, FR-G4, FR-G5, FR-G6, FR-G8 | US-08 |
| 9 | Monitoring pipeline | Must | FR-13, FR-14, FR-24 | US-09, US-13 |
| 10 | Eksperimen engineering Cassandra | Must | FR-15, FR-16 | US-10 |
| 11 | Hosting di cloud | Must | FR-17, FR-18 | US-11, US-14 |
| 12 | Ingestion incremental NRT | Must | FR-19, FR-20, FR-21, FR-22, FR-23, FR-24, FR-G2 | US-12, US-13 |

**Pemetaan balik story → FR:** US-01 → FR-01 · US-02 → FR-03 · US-03 → FR-05 · US-04 → FR-06 · US-05 → FR-07 · US-06a → FR-08 · US-06b → FR-09 · US-07 → FR-11 · US-08 → FR-12 · US-09 → FR-13, FR-14 · US-10 → FR-15, FR-16 · US-11 → FR-17 · US-12 → FR-19, FR-20 · US-13 → FR-04, FR-24 · US-14 → FR-18. FR tanpa story (berasal dari keputusan G1/charter): FR-02, FR-10, FR-21, FR-22, FR-23, FR-G4 … FR-G8.

**Perubahan dari draf D-P1-001:**
- US-13 (provenance) dan US-14 (reproduksibilitas) kini terikat ke fitur: FR-24 → #2, #9, #12; FR-18 → #11 (image yang sama lokal/cloud).
- Mode backfill (FR-21) tidak punya nomor fitur sendiri di charter §6.1; dipetakan ke #12 karena satu pipeline dua mode (OQ-10). `ASSUMPTION`, lihat Q-6.
- Penanda ⏳ F1 di draf sudah terjawab G1: periode (HD-09), 38 provinsi BIG (HD-08), NOAA-21 sejak 2023-03-01, polling 15 menit, aturan DQ (HD-11). Yang masih terbuka dipindah ke 📏 (NFR) atau ⚖️ (§5).

### Cek kriteria penerimaan

Diperiksa dengan skrip yang mem-parse tabel §2–§4 dokumen ini (hasil ditempel di `bukti:` tracker dan deskripsi PR):
- Setiap fitur Must (#1, #2, #3, #4, #6, #8, #9, #10, #11, #12) punya ≥1 FR non-umum.
- Setiap FR (FR-01 … FR-24, FR-G1 … FR-G8) terpetakan ke ≥1 fitur #1–#12.

## 5. Keputusan yang dibutuhkan (⚖️, G2)

Agen hanya menyusun opsi dan rekomendasi; keputusan di tangan tim (STATUS §2 butir 4).

| ID | Pertanyaan | Opsi | Rekomendasi (`RECOMMENDATION`) | FR |
|---|---|---|---|---|
| Q-1 | Periode default halaman ringkasan | (a) 30 hari terakhir · (b) musim kemarau terakhir · (c) tahun berjalan | (a): selaras dengan data NRT terbaru dan volume query kecil | FR-01 |
| Q-2 | Granularitas default timeline | (a) harian · (b) bulanan · (c) otomatis menurut panjang rentang | (c): harian bila ≤ 90 hari, bulanan bila lebih | FR-05 |
| Q-3 | Ranking per luas wilayah | (a) absolut saja · (b) absolut + per luas (`LUASWH` BIG) | (a) di MVP; (b) = *Could* | FR-06 |
| Q-4 | Agregat nasional: ikut menghitung `OUTSIDE`? Tanggal lokal mana? | (a) nasional = jumlah 38 provinsi (tanpa `OUTSIDE`), tanggal lokal per provinsi · (b) nasional = semua deteksi termasuk `OUTSIDE` | (a): konsisten dengan ranking; `OUTSIDE` tampil terpisah (FR-02) | FR-G4, FR-01 |
| Q-5 | Prioritas filter tipe non-vegetasi | (a) Must · (b) Should | (b): G1 menyebutnya "opsional" dan hanya berlaku untuk periode SP | FR-10 |
| Q-6 | Mode backfill dipetakan ke fitur #12 | (a) setuju · (b) tambah fitur baru lewat CR charter | (a): tidak perlu CR | FR-21 |
| HD-12 | Default tampilan confidence | Diputuskan di A-P2-001 (R1 + R4) | — | FR-08 |
| HD-13 | Batas titik peta, rentang tanggal maks, interval poll final, ambang basi | Diputuskan di C-P2-001 (R3) | — | FR-03, FR-19, FR-20 |
| HD-25 | Teks final disclaimer | Diputuskan tim | — | FR-G2 |

## 6. Untuk serah-terima ke B-P2-001 (R2)

Kebutuhan baca yang diturunkan dari FR di atas (bahan Q-xx, bukan desain tabel):

| Kebutuhan | FR | Kunci filter |
|---|---|---|
| Total & jumlah provinsi aktif per rentang tanggal | FR-01, FR-02 | tanggal lokal, satelit, confidence, (tipe) |
| Jumlah per hari/bulan, nasional & per provinsi | FR-05, FR-G7 | provinsi, tanggal lokal, satelit, confidence |
| Top-N provinsi per rentang | FR-06 | tanggal lokal, satelit, confidence |
| Titik deteksi per provinsi + rentang pendek (dibatasi) | FR-03, FR-04 | provinsi, tanggal lokal, satelit, confidence |
| Histogram FRP | FR-11 | provinsi, rentang, satelit, confidence |
| Daftar run & status pipeline | FR-13, FR-14 | waktu run |
| Tanggal tidak lengkap per (satelit, tanggal) | FR-G7 | satelit, tanggal |

## 7. Di luar ruang lingkup

Mengikuti charter §6.3: akun pengguna, notifikasi/alert, prediksi kebakaran, estimasi luas terbakar, klasifikasi penyebab, perbandingan lintas sensor, klaim tanggap darurat real-time, dan pengayaan kabupaten/kota (*Could*).
