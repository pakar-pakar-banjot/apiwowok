# 03 — MVP Lock dan Urutan Descoping (D-P2-003)

> Fase 2 · Draf agen 2026-11-26 · Pemilik: R4 (Abigail) · Status: `RECOMMENDATION`, menunggu G2 (ruang lingkup)
> Input: [FR + AC](01-functional-requirements.md) (D-P2-001/002, disetujui), [NFR](02-non-functional-requirements.md) (C-P2-001, disetujui), [semantik data](../03-specs/data/01-data-semantics.md) (A-P2-001, disetujui), [charter §6](../00-discovery/01-project-charter.md#6-ruang-lingkup-awal-dan-mvp), [risk & kapasitas §3](../10-execution-plan/09-risk-capacity-plan.md), [kontingensi jadwal §7](../10-execution-plan/05-project-schedule.md#7-kontingensi-dipicu-di-checkpoint).
> Serah-terima: R2 (Abi Funn) untuk X-P2-901 (paket G2).
> Label: [legenda](../00-discovery/README.md#label-status-informasi). Dokumen ini **tidak** menambah atau mengubah FR; ia mengunci daftar Must dan mengurutkan pemotongan. Keputusan ruang lingkup di tangan tim (STATUS §2 butir 4).

## 1. Yang sudah diputuskan (masukan ke penguncian)

| Keputusan | Hasil | Dasar |
|---|---|---|
| KEP-01 (= HD-12) default confidence | Semua (`l`+`n`+`h`), filter menonjol | Lanang (R1) + Abigail (R4), 2026-11-26, disetujui lewat chat tim (belum ada jejaknya di repo) |
| KEP-04 default satelit | NOAA-20 saja; gabungan opsional dengan peringatan, tanpa dedup | idem |
| KEP-05 ranking dan pemotongan titik peta | Ranking absolut tanpa per luas; titik terpotong urut `frp` menurun, lalu `acq_datetime_utc` menurun, lalu `detection_id` naik | idem |
| NFR §11 (HD-13), enam butir | Sesuai usulan C-P2-001: batas titik 2.000/5.000, rentang maks 7 hari, ambang 18/30 jam, keamanan minimum, rate limit *Should* 60 req/menit/IP, target p95 | Zita (R3) dan Abigail (R4), 2026-11-26, lewat chat tim; angka tetap `RECOMMENDATION` sampai dikalibrasi (C-P5, B-P5-007) |

Pencatatan resmi ID keputusan baru di [12-human-decision-register](../10-execution-plan/12-human-decision-register.md) adalah tugas koordinator (X-P2-901), bukan tugas ini.

## 2. Daftar Must final

Mengikuti [charter §6.1](../00-discovery/01-project-charter.md#61-pemetaan-10-fitur-usulan-ke-moscow-recommendation-pending) dan MoSCoW di FR. **Must = 27 FR, Should = 5 FR; total 32 FR.**

### 2.1 Must (27 FR)

| Fitur | MoSCoW fitur | FR Must |
|---|---|---|
| Aturan umum (#1–#8, #12) | Must | FR-G1, FR-G2, FR-G3, FR-G4, FR-G5, FR-G6, FR-G7, FR-G8 |
| #1 Ringkasan nasional/regional | Must | FR-01, FR-02 |
| #2 Peta hotspot interaktif | Must | FR-03, FR-04 |
| #3 Timeline | Must | FR-05 |
| #4 Ranking provinsi | Must | FR-06 |
| #6 Filter confidence & satelit | Must | FR-08, FR-09 |
| #8 Eksplorasi regional (digabung ke #1–#4) | Must | FR-12 |
| #9 Monitoring pipeline (minimal) | Must | FR-13, FR-14 |
| #10 Eksperimen Cassandra (≥1 eksperimen partisi) | Must | FR-15 |
| #11 Hosting di cloud (setelah integrasi lokal) | Must | FR-17, FR-18 |
| #12 Ingestion incremental NRT | Must | FR-19, FR-20, FR-21, FR-22 |
| Lintas fitur: provenance | Must | FR-24 |

### 2.2 Should (5 FR), dipotong lebih dulu bila terlambat

| FR | Fitur | Isi singkat | Tugas WBS (jam PERT) |
|---|---|---|---|
| FR-07 | #5 Perbandingan periode | Dua periode berdampingan | D-P6-008 (4,17) |
| FR-10 | #6 Filter tipe non-vegetasi | Opsional; hanya bermakna untuk SP (Q-5) | tidak punya tugas sendiri; bagian filter UI/API |
| FR-11 | #7 Distribusi FRP | Histogram FRP | C-P6-010 (3,0) dan D-P6-008 (4,17) |
| FR-16 | #10 Eksperimen 3 node | Replikasi dan kegagalan node | B-P4-002 (3,0) dan B-P7-003 (4,17) |
| FR-23 | #12 Rekonsiliasi NRT→SP manual | Penggantian per tanggal | A-P7-003 (3,0) |

Total jam tugas *Should* di WBS: 3,0 + 3,0 + 4,17 + 3,0 + 4,17 = **17,34 jam**, cocok dengan "±17 jam tim" di [risk plan](../10-execution-plan/09-risk-capacity-plan.md).

### 2.3 Bentuk MVP (charter §6.2)

MVP = enam kapabilitas yang harus berjalan **lokal dulu**, baru di-deploy ke cloud:

| Kapabilitas MVP | FR pendukung |
|---|---|
| 1. Satu pipeline ETL dua mode (backfill SP, incremental NRT) | FR-19, FR-21, FR-22, FR-24 |
| 2. Read model Cassandra untuk access pattern MVP | diturunkan di B-P2-001 / Fase 3 |
| 3. FastAPI: ringkasan, timeline, ranking, titik peta, status pipeline | FR-01, 03, 05, 06, 14 |
| 4. Dashboard React + Leaflet: ringkasan, timeline, peta, ranking, filter, disclaimer | FR-G1–G8, FR-01–06, 08, 09, 12, 20 |
| 5. Monitoring pipeline minimal | FR-13, FR-14 |
| 6. Satu eksperimen partisi Cassandra dengan hasil aktual | FR-15 |

## 3. Urutan descoping (`RECOMMENDATION`)

Prinsip nomor 6 di [overview](../10-execution-plan/00-execution-plan-overview.md): *Must dulu; Should dipotong lebih dulu.* Urutan di bawah mengikuti pemicu yang **sudah ada** di kontingensi jadwal, lalu mengurutkan sisanya menurut dampak ke FR Must.

| Urutan potong | Tugas | FR | Jam | Pemicu / alasan |
|---|---|---|---|---|
| 1 | B-P4-002 smoke test 3 node | prasyarat FR-16 | 3,0 | Checkpoint D6: G3 belum disetujui |
| 2 | C-P6-010 endpoint FRP dan D-P6-008 histogram + perbandingan periode | FR-11, FR-07 | 3,0 + 4,17 | Checkpoint D10: belum ada data nyata di Cassandra (R-14), potong semua *Should* Fase 6. FR-10 ikut ditunda di sini bila Q-5 = Should |
| 3 | B-P7-003 eksperimen replikasi/failure 3 node | FR-16 | 4,17 | Checkpoint D13: integrasi lokal gagal, freeze *Should*. Kriteria keberhasilan charter §7 butir 4 sudah dipenuhi oleh satu eksperimen partisi (FR-15, Must) |
| 4 | A-P7-003 rekonsiliasi NRT→SP manual | FR-23 | 3,0 | Dipotong paling akhir di antara *Should* karena mendukung FR-22 (Must); lihat risiko di bawah |

**Setelah semua *Should* dipotong dan masih terlambat:** satu-satunya pemotongan yang sudah punya dasar di dokumen adalah cloud (FR-17, R-23): demo lokal + rekaman, cloud jadi upaya terbaik sampai D19 (checkpoint D17). **Pemotongan Must lain tidak ada dasarnya dan butuh CR charter + persetujuan tim.** *Could* (kab/kota, clustering/heatmap, adapter NODD, rekonsiliasi terjadwal) tidak dijadwalkan dan tidak perlu dipotong.

**Risiko yang perlu diputuskan tim ⚖️:**
- **Memotong FR-23 (urutan 4):** FR-22 (Must) menuntut SP menggantikan NRT per tanggal. Tanpa perintah manual FR-23, penggantian hanya bisa lewat menjalankan ulang backfill (FR-21). Tim perlu memastikan jalur itu cukup sebelum urutan 4 dieksekusi.
- **Memotong FR-16 (urutan 3):** FR-16 Should di charter, tetapi eksperimen replikasi adalah bagian pembelajaran Cassandra. Tim bisa menukar urutan 3 dan 4 bila bobot pembelajaran lebih penting.
- **FR-10:** tidak punya tugas WBS sendiri, jadi pemotongannya berarti menyembunyikan filter, bukan menghemat jam yang terukur.

## 4. Keputusan terbuka untuk G2 (ruang lingkup)

| ID | Pertanyaan | Rekomendasi (dari FR §5 dan penguncian ini) | Pengaruh ke MVP |
|---|---|---|---|
| Q-5 | Prioritas filter tipe non-vegetasi | (b) *Should* | Menentukan FR-10 ada di §2.2 (Should), bukan §2.1 |
| Q-6 | Mode backfill dipetakan ke fitur #12 | (a) setuju, tanpa CR | Menentukan FR-21 tetap Must di bawah fitur #12 |
| Q-1 | Periode default ringkasan | (a) 30 hari terakhir | Tidak mengubah daftar Must |
| Q-2 | Granularitas default timeline | (c) otomatis menurut rentang | Tidak mengubah daftar Must |
| Q-3 | Ranking per luas wilayah | (a) absolut; per luas = *Could* (selaras KEP-05) | Per luas tidak masuk MVP |
| Q-4 | Agregat nasional dan `OUTSIDE` | (a) nasional = jumlah 38 provinsi, `OUTSIDE` terpisah | Tidak mengubah daftar Must |
| HD-25 | Teks final disclaimer | diputuskan tim | Memengaruhi AC-G1.1 dan AC-G2.1 |

Bila keputusan tim berbeda dari rekomendasi, daftar di §2 dan §3 diperbarui sebelum G2 ditutup.

## 5. Cek kriteria penerimaan

Kriteria D-P2-003: *daftar descoping berurutan disetujui tim.* Pemeriksaan yang bisa dilakukan sebelum G2 (hasil ditempel di `bukti:` tracker dan deskripsi PR):
- Daftar Must dan Should di §2 identik dengan MoSCoW di [FR](01-functional-requirements.md): tidak ada FR yang hilang atau berlebih.
- Setiap tugas *Should* di WBS muncul tepat sekali di §3 (5 tugas, 4 baris urutan karena C-P6-010 dan D-P6-008 dipotong bersama).
- Persetujuan tim atas urutan = keputusan G2 (ruang lingkup); belum terjadi.
