# 04 — Register Pertanyaan Terbuka & Keputusan Tertunda

Status: **DRAFT**. Semua rekomendasi berstatus `RECOMMENDATION` dan **bukan keputusan** sampai tim mengisi kolom *Keputusan*.

Prioritas: **P0** = memblokir Fase 1 · **P1** = dibutuhkan sebelum Fase 2/3 · **P2** = dapat diputuskan kemudian.

## Ringkasan pemblokir Fase 1

OQ-01, OQ-02, OQ-03, OQ-04, OQ-05, OQ-06. Untuk OQ-04–OQ-06 cukup jawaban **sementara** (kandidat yang akan diprofil). Keputusan final diambil di gerbang Fase 1 setelah data nyata diperiksa.

## Register

### Administratif

| ID | Pertanyaan | Mengapa penting | Opsi | Rekomendasi | Prioritas | Diputuskan oleh | Keputusan |
|---|---|---|---|---|---|---|---|
| OQ-01 | Apa rubrik penilaian dan komponen wajib mata kuliah? (Cassandra wajib? Eksperimen replikasi wajib? Format laporan? Durasi presentasi tepat 20 menit?) | Menentukan apa yang harus diprioritaskan; tanpa ini MoSCoW hanya tebakan. | — | Minta rubrik tertulis dari dosen/asisten hari ini. | **P0** | Tim (sumber: dosen) | |
| OQ-02 | Tanggal mulai (D1), tanggal presentasi, dan tanggal pengumpulan? Adakah ujian/libur di tengahnya? | Jadwal relatif D1–D21 harus dipetakan ke kalender nyata. | — | Isi tanggal nyata di charter §10. | **P0** | Tim | |
| OQ-03 | Siapa memegang peran R1–R4, dan berapa jam/hari ketersediaan masing-masing? | Setiap fitur wajib memiliki pemilik. | Usulan peran di charter §9. | Tetapkan berdasarkan minat & kemampuan; tiap area punya reviewer kedua. | **P0** | Tim | |

### Data

| ID | Pertanyaan | Mengapa penting | Opsi | Rekomendasi | Prioritas | Diputuskan oleh | Keputusan |
|---|---|---|---|---|---|---|---|
| OQ-04 | Produk satelit mana yang dipakai? | Menentukan semantik confidence, volume, perbandingan, dan filter satelit (C-03, C-04). | (A) VIIRS S-NPP saja · (B) VIIRS S-NPP + NOAA-20 · (C) MODIS + VIIRS · (D) MODIS saja | **Kandidat profiling: A dan B.** Final setelah Fase 1. Hindari C untuk MVP karena jumlah deteksi antar sensor tidak dapat dibandingkan langsung. Ketersediaan & celah data tiap satelit harus diverifikasi (`AI-PRIOR`: VIIRS S-NPP sejak 2012, NOAA-20 sejak 2018). | **P0** (sementara) | Tim | |
| OQ-05 | Periode historis yang dicakup? | Menentukan volume, ukuran partisi, dan makna perbandingan historis. | (A) 1 tahun · (B) 2–3 tahun · (C) ≥5 tahun | **Sementara:** profil satu tahun penuh terlebih dahulu untuk mengukur volume; target ≥2 tahun penuh yang mencakup setidaknya satu musim kemarau dengan aktivitas deteksi tinggi. Final setelah profiling volume. | **P0** (sementara) | Tim | |
| OQ-06 | Cakupan geografis dan granularitas wilayah? | Menentukan metode ekstraksi (per negara vs bounding box) dan pengayaan. | (A) Seluruh Indonesia, tingkat provinsi · (B) Seluruh Indonesia, kabupaten · (C) Pulau/provinsi tertentu | **A.** Kabupaten = *Could*. | **P0** | Tim | |
| OQ-07 | Sumber batas administrasi provinsi yang mana? | Akurasi pengayaan, jumlah provinsi (34 vs 38), lisensi (C-12). | Kandidat: data BIG/Ina-Geoportal, GADM, geoBoundaries, sumber lain | Evaluasi di Fase 1: pilih yang memuat 38 provinsi, berlisensi jelas untuk penggunaan akademik, dan ukurannya wajar. Catat versi & tanggal unduh. | P1 | Tim (R1 mengusulkan) | |

### Kebijakan data

| ID | Pertanyaan | Mengapa penting | Opsi | Rekomendasi | Prioritas | Diputuskan oleh | Keputusan |
|---|---|---|---|---|---|---|---|
| OQ-08 | Zona waktu apa yang dipakai untuk "tanggal" agregasi harian dan tampilan? | Deteksi malam dapat bergeser ke hari sebelumnya bila memakai UTC (C-07). | (A) UTC · (B) WIB untuk seluruh Indonesia · (C) Zona waktu lokal per provinsi (WIB/WITA/WIT) | **C**, dengan timestamp UTC tetap disimpan sebagai nilai kanonis. | P1 | Tim | |
| OQ-09 | Bagaimana kebijakan confidence? Apakah deteksi confidence rendah disimpan dan ditampilkan secara default? | Memengaruhi jumlah deteksi yang dilaporkan. | (A) Simpan semua, tampilkan semua · (B) Simpan semua, default sembunyikan "low" · (C) Buang "low" saat ingest | **Simpan semua** (tidak ada kehilangan data diam-diam). Default tampilan diputuskan di Fase 2. Tolak C. | P1 | Tim | |
| OQ-10 | Mode ingestion untuk MVP dan kebijakan NRT vs arsip? | Kompleksitas, risiko duplikasi (C-15). | (A) Arsip historis saja · (B) Arsip + NRT manual · (C) Arsip + NRT terjadwal | **A untuk MVP, B sebagai *Should*.** Jika B: arsip menggantikan NRT untuk periode tumpang tindih. | P1 | Tim | |
| OQ-11 | Bagaimana memperlakukan deteksi di luar poligon provinsi (laut, negara tetangga)? | Aturan "no silent data loss" vs ranking yang benar (C-13). | (A) Tolak sebagai rejected · (B) Simpan dengan status wilayah khusus · (C) Buang | **B**; laporkan jumlahnya di monitoring; keluarkan dari ranking provinsi. Deteksi di wilayah negara lain dapat dicatat sebagai *out-of-scope* di log (bukan dibuang tanpa jejak). | P1 | Tim | |
| OQ-12 | Apakah sumber panas statis (gunung api, industri) dipisahkan? | Bias jumlah deteksi (C-14). | (A) Pakai field `type` bila tersedia · (B) Abaikan, nyatakan keterbatasan · (C) Masker statis buatan sendiri | **A jika field tersedia (cek Fase 1), selain itu B.** C di luar ruang lingkup. | P1 | Tim | |

### Cassandra

| ID | Pertanyaan | Mengapa penting | Opsi | Rekomendasi | Prioritas | Diputuskan oleh | Keputusan |
|---|---|---|---|---|---|---|---|
| OQ-13 | Apa definisi "sharding experiment" dalam proyek ini? | Cassandra sudah mendistribusikan partisi secara otomatis (C-06). | (A) Eksperimen bucketing partition key · (B) Observasi distribusi token pada multi-node · (C) Keduanya | **A wajib, B jika cluster multi-node tersedia.** | P1 | Tim (R2 mengusulkan) | |
| OQ-14 | Apakah eksperimen replikasi & failure wajib? | Butuh multi-node dan hardware (C-01). | (A) Wajib · (B) Opsional | Bergantung OQ-01 & OQ-15. Default: *Should*. | P1 | Tim | |
| OQ-17 | Versi Cassandra yang dipakai (mis. 4.1 vs 5.0)? Apakah fitur seperti Storage-Attached Index boleh dipakai? | Fitur indeks dapat menggoda pola query non-Cassandra; kompatibilitas driver. | — | Putuskan di Fase 3/4 lewat ADR. Fitur indeks sekunder hanya dengan justifikasi access pattern tertulis. | P2 | Tim (R2) | |

### Infrastruktur & proses

| ID | Pertanyaan | Mengapa penting | Opsi | Rekomendasi | Prioritas | Diputuskan oleh | Keputusan |
|---|---|---|---|---|---|---|---|
| OQ-15 | Spesifikasi laptop tiap anggota (OS, RAM, CPU, Docker terpasang)? | Kelayakan Docker Compose & cluster multi-node. | — | Survei singkat hari ini. | P1 | Tiap anggota | |
| OQ-16 | Repo GitHub publik atau privat? | Risiko kebocoran MAP_KEY & data; kebijakan pengumpulan. | Publik · Privat | Privat selama pengembangan kecuali rubrik meminta publik. `.env` tidak pernah di-commit apa pun pilihannya. | P1 | Tim | |
| OQ-18 | Bagaimana pembagian kerja Claude Code vs Codex? | Mencegah konflik file & spesifikasi ganda. | (A) Per anggota (tiap orang memilih agen) · (B) Per area · (C) Satu implementer + agen lain reviewer per tugas | **C**, dengan branch per tugas; dirinci di AGENTS.md (Fase 4). | P2 | Tim | |

### Produk

| ID | Pertanyaan | Mengapa penting | Opsi | Rekomendasi | Prioritas | Diputuskan oleh | Keputusan |
|---|---|---|---|---|---|---|---|
| OQ-19 | Siapa persona primer MVP? | Fokus desain (C-18). | — | Primer: analis lingkungan & peneliti. Sekunder: pemerintah daerah. | P1 | Tim | |
| OQ-20 | Bahasa UI dashboard? | Label, disclaimer, format tanggal. | Indonesia · Inggris · Dwibahasa | Indonesia. | P2 | Tim | |
| OQ-21 | Apakah aplikasi harus dapat diakses online saat penilaian? | Kebutuhan deployment & keamanan. | Lokal + video · Hosting | Lokal + video demo, kecuali rubrik meminta hosting. | P1 | Tim (sumber: rubrik) | |
| OQ-22 | Seberapa jauh fitur "monitoring pipeline"? | Hindari membangun sistem observability penuh. | (A) Log file saja · (B) Tabel run + endpoint + halaman sederhana · (C) Dashboard metrik lengkap | **B.** | P2 | Tim | |
