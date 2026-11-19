# 02 — Analisis Konteks, Kontradiksi, dan Kelayakan

Status: **DRAFT**. Label informasi: lihat [README](README.md#label-status-informasi).

Seluruh pernyataan tentang NASA FIRMS dan perilaku Cassandra di dokumen ini berlabel `AI-PRIOR` kecuali dinyatakan lain, dan harus diverifikasi (FIRMS di Fase 1; Cassandra di Fase 3/7).

## A. Kontradiksi dan ketegangan dalam brief

| ID | Temuan | Mengapa penting | Usulan penyelesaian (`RECOMMENDATION`) | Terkait |
|---|---|---|---|---|
| **C-01** | "Distributed event analytics" vs infrastruktur kemungkinan laptop dengan Cassandra single-node. | Satu node tidak dapat mendemonstrasikan distribusi, replikasi, atau toleransi kegagalan. | Single-node untuk pengembangan; profil Docker Compose 3 node hanya untuk eksperimen replikasi, dijalankan di laptop dengan RAM terbesar. Jika tidak memungkinkan, nyatakan sebagai keterbatasan, jangan klaim. | OQ-14, OQ-15, R-11 |
| **C-02** | "Observasi satelit baru terus tersedia" / Near Real-Time vs tidak ada orkestrator (Airflow dilarang tanpa justifikasi). | Ingestion berkelanjutan butuh penjadwal, penanganan kuota API, dan logika NRT→arsip. | MVP: batch historis + perintah incremental manual dengan checkpoint. NRT otomatis = *Could*. Hindari istilah "real-time". | OQ-10 |
| **C-03** | Filter confidence tunggal vs semantik confidence yang berbeda antar produk. `AI-PRIOR`: MODIS memakai angka 0–100, VIIRS memakai kategori (low/nominal/high). | Filter "confidence ≥ 80" tidak bermakna untuk VIIRS; menggabungkan keduanya menghasilkan filter yang menyesatkan. | Pilih satu keluarga sensor untuk MVP sehingga semantik confidence seragam. | OQ-04, OQ-09 |
| **C-04** | "Filter satelit" vs kemungkinan hanya satu satelit dipakai. | Jika hanya satu satelit, filter tersebut kosong makna. | Filter satelit hanya relevan jika ≥2 satelit sekeluarga (mis. VIIRS S-NPP + NOAA-20). Keputusan setelah Fase 1 menilai volume. | OQ-04 |
| **C-05** | "Perbandingan periode historis" vs integritas metodologis. | Jumlah deteksi berubah karena jumlah satelit aktif, gangguan data satelit, tutupan awan, dan perubahan batas provinsi — bukan hanya karena aktivitas api. | Perbandingan hanya untuk produk & satelit yang sama, batas wilayah yang sama, panjang periode yang sama; tampilkan peringatan metodologis. Prioritas *Should*. | R-15, R-21 |
| **C-06** | "Sharding experiments" vs cara kerja Cassandra. Cassandra sudah mendistribusikan partisi antar node secara otomatis melalui token/consistent hashing. | Tanpa definisi, eksperimen bisa menjadi tidak bermakna atau keliru secara konsep. | Definisikan ulang sebagai: (a) eksperimen *bucketing* partisi di tingkat aplikasi (mis. menambah komponen waktu/bucket ke partition key) dan (b) observasi distribusi token/data pada cluster multi-node. | OQ-13 |
| **C-07** | Zona waktu belum ditentukan. `AI-PRIOR`: `acq_date`/`acq_time` FIRMS dalam UTC; VIIRS melintas sekitar pukul ~01:30 dan ~13:30 waktu lokal. | Deteksi malam ~01:30 WIB = ~18:30 UTC **hari sebelumnya**. Agregasi per tanggal UTC akan memindahkan deteksi malam ke hari sebelumnya. Untuk WIT, efeknya lebih besar. Indonesia memiliki 3 zona waktu, sehingga WIB nasional pun keliru untuk wilayah timur. | Simpan timestamp kanonis UTC + tanggal lokal turunan berdasarkan zona waktu provinsi (WIB/WITA/WIT). Dokumentasikan aturan ini. | OQ-08, R-07 |
| **C-08** | "Aggregation" dan "province ranking" vs keterbatasan Cassandra. Cassandra tidak memiliki JOIN dan agregasi lintas partisi yang efisien. | Ranking nasional tidak bisa dihitung dengan query ad hoc tanpa full scan. | Agregat dihitung pipeline dan disimpan sebagai read model khusus query. Desain final di Fase 3. | R-09 |
| **C-09** | "Idempotent ingestion" vs godaan memakai counter table untuk agregat. Counter Cassandra bersifat increment, tidak idempoten. | Re-run atau retry akan menggandakan angka. | Agregat ditulis sebagai nilai absolut hasil perhitungan ulang deterministik per partisi (mis. per provinsi per hari), bukan increment. | R-10 |
| **C-10** | Peta interaktif dengan "semua titik" vs volume data `UNKNOWN`. | Ribuan titik per tampilan dapat membuat Leaflet lambat; query tanpa batas berisiko membaca partisi besar. | Batasi jumlah titik per respons; peta wajib difilter tanggal + provinsi; clustering/heatmap = *Could*. | R-05 |
| **C-11** | Query peta berdasarkan viewport (bounding box) vs Cassandra tanpa indeks spasial bawaan. | Query "titik di dalam kotak peta" bukan pola alami Cassandra. | MVP: peta berbasis provinsi + rentang tanggal. Partisi berbasis grid/geohash = kandidat eksperimen, bukan MVP. Storage-Attached Index (Cassandra 5.x, `AI-PRIOR`) hanya dievaluasi dengan justifikasi di Fase 3. | OQ-17 |
| **C-12** | "Spatial enrichment" vs sumber batas administrasi belum dipilih. `AI-PRIOR`: Indonesia memiliki 38 provinsi sejak pemekaran 2022; banyak dataset batas publik masih 34 provinsi. | Data historis sebelum 2022 akan dipetakan ke provinsi yang belum ada saat itu; dataset lama salah memetakan Papua. Lisensi berbeda antar sumber. | Gunakan satu versi batas wilayah yang tetap untuk seluruh periode (dicatat versinya); evaluasi sumber di Fase 1. | OQ-07, R-08 |
| **C-13** | Titik di luar poligon provinsi (laut, anjungan lepas pantai, negara tetangga di dalam bounding box). | Membuang diam-diam melanggar aturan "no silent data loss"; memasukkan ke ranking menyesatkan. | Simpan dengan status wilayah `UNASSIGNED`/`OUTSIDE_INDONESIA`, keluarkan dari ranking, laporkan jumlahnya di monitoring. | OQ-11 |
| **C-14** | Sumber panas statis (gunung api, industri, gas flare). `AI-PRIOR`: arsip VIIRS/MODIS standar mungkin memiliki field `type`, NRT tidak. | Jumlah deteksi di beberapa lokasi bisa didominasi sumber non-vegetasi. | Verifikasi keberadaan field `type` di Fase 1; jika ada, simpan dan sediakan filter; jika tidak, nyatakan sebagai keterbatasan. | OQ-12 |
| **C-15** | NRT vs arsip standar. `AI-PRIOR`: data NRT kemudian digantikan versi *standard/science processing*; nilai field `version` berbeda (mis. akhiran `NRT`). FIRMS tidak menyediakan ID unik per deteksi. | Jika keduanya dimuat, deteksi yang sama bisa tercatat dua kali. Koordinat/waktu bisa sedikit berbeda setelah pemrosesan ulang (`UNKNOWN`). | Tentukan natural key deterministik dan kebijakan "arsip menggantikan NRT untuk periode yang tumpang tindih". Uji di Fase 1 dengan data nyata. | OQ-10, R-06 |
| **C-16** | 8 fase dengan gerbang persetujuan vs 21 hari. | Jika Fase 0–4 masing-masing memakan 2–3 hari, implementasi baru dimulai sekitar D12. | Batasi waktu Fase 0–3 (±4 hari total), jalankan Fase 4 paralel, dokumen ringkas dan berbasis template. | R-02 |
| **C-17** | 10 fitur vs 4 orang × 21 hari. | Fitur yang selesai setengah jalan tidak bernilai di demo. | MVP 6 kapabilitas (charter §6.2). | R-01 |
| **C-18** | Lima kelompok pengguna dengan kebutuhan berbeda (relawan butuh data terkini; peneliti butuh provenance). | Desain yang mencoba melayani semua akan kabur. | Pengguna primer: analis lingkungan & peneliti. | OQ-19 |

## B. Keputusan yang belum dibuat

Ringkasan; detail opsi dan rekomendasi ada di [04-open-questions-register.md](04-open-questions-register.md).

| Kategori | Keputusan | ID |
|---|---|---|
| Administratif | Rubrik & komponen wajib mata kuliah, tanggal mulai/akhir, peran anggota | OQ-01, OQ-02, OQ-03 |
| Data | Produk satelit, periode historis, cakupan geografis, sumber batas wilayah | OQ-04–OQ-07 |
| Kebijakan data | Zona waktu, confidence, NRT vs arsip, titik di luar wilayah, sumber statis | OQ-08–OQ-12 |
| Cassandra | Definisi eksperimen sharding, eksperimen replikasi wajib/tidak, versi Cassandra | OQ-13, OQ-14, OQ-17 |
| Infrastruktur & proses | Hardware, visibilitas repo, pembagian kerja agen AI | OQ-15, OQ-16, OQ-18 |
| Produk | Persona primer, bahasa UI, hosting, tingkat monitoring | OQ-19–OQ-22 |

## C. Penilaian kelayakan per area

Skala: **Layak** · **Layak bersyarat** · **Berisiko**.

| Area | Penilaian | Alasan | Syarat |
|---|---|---|---|
| Akses data FIRMS | Layak bersyarat | `AI-PRIOR`: data publik gratis, butuh MAP_KEY untuk API; unduhan arsip besar mungkin melalui permintaan yang tidak instan. | MAP_KEY diminta D1; siapkan jalur cadangan (unduhan CSV per negara/arsip) di Fase 1. |
| ETL (Pandas + GeoPandas) | Layak | Volume Indonesia per tahun kemungkinan muat di memori laptop (`ASSUMPTION`, verifikasi Fase 1). Spatial join titik-ke-poligon adalah operasi standar GeoPandas. | Satu versi batas wilayah; natural key dedup disepakati. |
| Model data Cassandra | Layak bersyarat | Pola query MVP sederhana (wilayah × waktu). Risiko utama: pola pikir relasional. | Access patterns disetujui sebelum skema (Fase 3). |
| Eksperimen partisi | Layak | Dapat dijalankan pada single-node dengan dataset nyata. | Prosedur benchmark terkendali (warm-up, repetisi, variabel tetap). |
| Eksperimen replikasi/failure | Berisiko | Butuh ≥3 node; tiap node Cassandra membutuhkan memori signifikan (`AI-PRIOR`). Hardware `UNKNOWN`. | Konfirmasi hardware (OQ-15); jika tidak memadai, turunkan ke *Could* dan nyatakan keterbatasan. |
| FastAPI | Layak | Endpoint read-only, jumlah kecil. | Kontrak API disepakati D5 agar frontend dapat memakai mock. |
| React + Leaflet + grafik | Layak bersyarat | Volume titik peta `UNKNOWN`. | Batas titik per respons; filter wajib. |
| Ingestion NRT | Berisiko (untuk MVP) | Kuota API, logika penggantian NRT→arsip, penjadwalan. | Jadikan *Should* (manual) / *Could* (otomatis). |
| Tim & waktu | Layak bersyarat | Ketersediaan anggota `UNKNOWN`; overhead proses tinggi. | MVP dipatuhi; feature freeze D17; integrasi pertama D13. |
| Koordinasi dua agen AI | Layak bersyarat | Risiko konflik file & kode yang tidak dipahami tim. | Satu implementer per tugas, branch per tugas, review lintas agen + manusia. |

## D. Estimasi upaya relatif (T-shirt sizing)

Estimasi kasar, bukan komitmen. Kapasitas tim `UNKNOWN` (lihat A-03).

| Workstream | Ukuran | Pemilik usulan |
|---|---|---|
| Fase 1 profiling & pemilihan dataset | S | R1 (+R2 untuk volume/partisi) |
| Requirements + spesifikasi UI | S | R4 |
| Access patterns + model Cassandra + ADR | M | R2 |
| Harness repo + Docker Compose + test runner | M | R3 |
| ETL lengkap (validasi, normalisasi, spatial join, dedup, rejected, checkpoint) | **L** | R1 |
| Ingestion Cassandra + read model agregat | M | R2 |
| FastAPI + test API | M | R3 |
| Dashboard (peta, timeline, ranking, filter, state loading/error) | **L** | R4 |
| Monitoring pipeline minimal | S | R1 + R3 |
| Eksperimen partisi | M | R2 |
| Eksperimen replikasi/failure | M–L | R2 + R3 |
| Laporan, presentasi, video | M | Semua (koordinasi R4) |

Dua workstream berukuran L (ETL dan dashboard) adalah jalur kritis. Keduanya harus dimulai paling lambat D6.

## E. Kesimpulan kelayakan

**Layak bersyarat.** NusaFire realistis diselesaikan dalam 21 hari oleh 4 orang **jika**:
1. Ruang lingkup dikunci ke MVP 6 kapabilitas.
2. Satu keluarga sensor (VIIRS 375 m) dipakai untuk MVP.
3. Ingestion historis batch menjadi prioritas; NRT ditunda.
4. Pengayaan spasial hanya sampai provinsi.
5. Fase 0–3 dibatasi waktu dan Fase 4 berjalan paralel.
6. Pertanyaan pemblokir dijawab dalam 1–2 hari.

Tanpa syarat-syarat tersebut, risiko tertinggi adalah demo akhir yang tidak berjalan end-to-end.
