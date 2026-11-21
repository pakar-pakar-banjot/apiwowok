# 00 — Draf User Stories & Functional Requirements (D-P1-001)

> Fase 1 · Draf agen 2026-11-19 · Pemilik: R4 (Abigail) · Reviewer: R3 (Zita) · Status: `RECOMMENDATION`, bahan awal untuk D-P2-001 (FR + acceptance criteria, G2)
> Sumber: [charter §2–§7](../00-discovery/01-project-charter.md), OQ-09, OQ-10, OQ-11, OQ-19, OQ-20, OQ-22. Label: [legenda](../00-discovery/README.md#label-status-informasi).
> Penanda **⏳ F1** = rincian menunggu hasil Fase 1 ([docs/01-dataset/](../01-dataset/)).

## Persona (OQ-19)

| Kode | Persona | Prioritas | Kebutuhan inti |
|---|---|---|---|
| **AL** | Analis lingkungan | Primer | Tren & sebaran per provinsi, filter kualitas deteksi |
| **PN** | Peneliti | Primer | Asal-usul data (produk, versi, file sumber), metodologi |
| **PD** | Pemerintah daerah | Sekunder | Ringkasan satu provinsi |
| **OP** | Operator sistem (anggota tim) | Internal | Pipeline dapat diulang, terpantau, dan dapat di-deploy |

Aturan umum yang berlaku untuk semua story:
- **FR-G1:** semua label memakai "deteksi hotspot", tidak pernah "kebakaran" (charter §3).
- **FR-G2:** disclaimer ilmiah dan waktu pembaruan data terakhir tampil di setiap halaman.
- **FR-G3:** UI berbahasa Indonesia (OQ-20).
- **FR-G4:** tanggal yang ditampilkan dan dipakai untuk agregasi adalah tanggal lokal provinsi (WIB/WITA/WIT, OQ-08).

## Stories per fitur

| ID | Fitur (charter §6.1) | MoSCoW | User story | Draf FR | Catatan |
|---|---|---|---|---|---|
| US-01 | #1 Ringkasan nasional/regional | Must | Sebagai **AL**, saya ingin melihat total deteksi hotspot nasional dan timeline singkat untuk periode yang saya pilih, agar saya tahu besaran aktivitas secara cepat. | FR-01: Halaman ringkasan menampilkan total deteksi, jumlah provinsi dengan deteksi, dan timeline nasional untuk rentang tanggal terpilih. | Default periode ⏳ F1 (OQ-05) |
| US-02 | #2 Peta interaktif | Must | Sebagai **AL**, saya ingin melihat titik deteksi di peta untuk satu provinsi dan rentang tanggal pendek, agar saya melihat sebaran geografisnya. | FR-02: Peta menampilkan titik deteksi untuk provinsi + rentang tanggal; jumlah titik dibatasi; muncul notice bila hasil terpotong. | Batas titik ⏳ F1 (volume per provinsi-hari, B-P1-001) → NFR |
| US-03 | #3 Timeline | Must | Sebagai **AL**, saya ingin melihat jumlah deteksi per hari atau per bulan, nasional maupun per provinsi, agar saya dapat mengenali kenaikan dan musim. | FR-03: Timeline harian/bulanan, nasional dan per provinsi, berdasarkan tanggal lokal. | — |
| US-04 | #4 Ranking provinsi | Must | Sebagai **AL**, saya ingin melihat provinsi dengan deteksi terbanyak pada periode terpilih, agar saya tahu wilayah mana yang perlu diperhatikan. | FR-04: Top-N provinsi berdasarkan jumlah deteksi; titik di luar provinsi tidak ikut (OQ-11). | 38 provinsi ⏳ F1 (sumber batas, OQ-07) |
| US-05 | #5 Perbandingan periode | Should | Sebagai **PN**, saya ingin membandingkan dua periode dengan produk/satelit dan batas wilayah yang sama, agar perbandingannya sah secara metodologis. | FR-05: Dua periode berdampingan; satelit/produk dikunci sama; catatan metodologi tampil. | Charter §3: tidak boleh lintas sensor |
| US-06a | #6 Filter confidence | Must | Sebagai **AL**, saya ingin memfilter deteksi berdasarkan confidence, agar saya dapat memilih tingkat keyakinan yang sesuai analisis saya. | FR-06a: Filter confidence berlaku untuk semua panel; default ditentukan di Fase 2 (OQ-09). | Nilai confidence nyata ⏳ F1 (data dictionary) |
| US-06b | #6 Filter satelit | Must | Sebagai **PN**, saya ingin memilih NOAA-20, NOAA-21, atau keduanya, agar saya dapat mengendalikan pengaruh jumlah lintasan satelit. | FR-06b: Filter satelit berlaku untuk semua panel; panel menjelaskan bahwa jumlah deteksi bergantung pada jumlah lintasan. | Cakupan NOAA-21 mulai 2023 ⏳ F1 |
| US-07 | #7 Distribusi FRP | Should | Sebagai **PN**, saya ingin melihat histogram FRP untuk wilayah dan periode terpilih, agar saya memahami sebaran intensitas deteksi. | FR-07: Histogram FRP per wilayah & periode. | Rentang FRP ⏳ F1 (profil) |
| US-08 | #8 Eksplorasi regional | Must (digabung) | Sebagai **PD**, saya ingin memilih provinsi saya dan melihat semua panel tersaring ke provinsi itu, agar saya mendapat ringkasan wilayah saya. | FR-08: Pemilih provinsi memfilter ringkasan, timeline, ranking (menyorot provinsi), dan peta; tersinkron ke URL. | — |
| US-09 | #9 Monitoring pipeline | Must (minimal) | Sebagai **OP**, saya ingin melihat daftar run ingest dengan waktu, file sumber, dan jumlah diterima/ditolak/duplikat, agar kegagalan pipeline segera terlihat. | FR-09: Tabel run + endpoint status + halaman sederhana (OQ-22). | Reason code ⏳ F1 (aturan DQ) |
| US-10 | #10 Eksperimen Cassandra | Must (partisi) / Should (3 node) | Sebagai **PN**, saya ingin membaca eksperimen partisi Cassandra yang dapat diulang, agar keputusan desain data punya bukti. | FR-10: Laporan eksperimen dengan hipotesis, prosedur, hasil aktual, keterbatasan, dan skrip yang dapat dijalankan ulang. | Volume uji ⏳ F1 |
| US-11 | #11 Hosting cloud | Must (≥ integrasi lokal) | Sebagai **AL**, saya ingin membuka dashboard lewat HTTPS tanpa instalasi, agar saya dapat memakainya dari mana saja. | FR-11: Aplikasi dapat diakses via HTTPS; database tidak terekspos. | — |
| US-12 | #12 Ingestion NRT | Must | Sebagai **AL**, saya ingin deteksi terbaru muncul di dashboard beberapa jam setelah lintasan satelit, beserta waktu pembaruannya, agar saya tahu seberapa segar datanya. | FR-12: Poller berkala memuat NRT baru tanpa duplikat; UI menampilkan waktu data terakhir dan peringatan bila data basi. | Interval & ambang basi ⏳ F1 (latensi, A-P1-008) |
| US-13 | Provenance (lintas fitur) | Must | Sebagai **PN**, saya ingin mengetahui produk, versi, dan file sumber setiap deteksi, agar hasil saya dapat ditelusuri. | FR-13: Setiap deteksi menyimpan source ID, tingkat pemrosesan (SP/NRT), versi, checksum file sumber, dan versi batas wilayah; ditampilkan di detail titik peta. | Kontrak canonical event (A-P3-001) |
| US-14 | Reproduksibilitas (O-E4) | Must | Sebagai **OP**, saya ingin menjalankan seluruh sistem dari nol mengikuti README, agar anggota lain dapat menguji tanpa bantuan. | FR-14: `docker compose up` + perintah ingest terdokumentasi menghasilkan dashboard berisi data. | — |

## Hal yang sengaja tidak menjadi story (charter §6.3)

Akun pengguna, notifikasi/alert, prediksi kebakaran, estimasi luas terbakar, perbandingan antar sensor (MODIS vs VIIRS), dan klaim tanggap darurat real-time.

## Pertanyaan untuk D-P2-001

1. Periode default halaman ringkasan: 30 hari terakhir atau satu musim kemarau? (bergantung OQ-05)
2. Granularitas timeline default: harian atau bulanan?
3. Apakah ranking memakai jumlah deteksi absolut saja, atau juga per luas wilayah? Kalau per luas, butuh `LUASWH` dari BIG; lihat [05-boundary-sources](../01-dataset/05-boundary-sources.md).
