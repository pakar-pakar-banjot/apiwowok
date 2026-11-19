# 01 — Piagam Proyek Awal (Preliminary Project Charter)

Status: **DIPERBARUI 2026-11-19** dengan jawaban tim atas open questions; menunggu konfirmasi G0. Label informasi: lihat [README](README.md#label-status-informasi).

## 1. Identitas proyek

| Atribut | Nilai | Label |
|---|---|---|
| Nama | NusaFire — Indonesian Hotspot Intelligence | `USER` |
| Jenis | Proyek universitas, aplikasi data engineering bergaya produksi | `USER` |
| Durasi | Sisa 21 hari kalender | `USER` |
| Tim | 4 mahasiswa (peran R1–R4; nama ditetapkan kemudian), masing-masing ±4 jam/hari | `USER` |
| Tanggal mulai (D1) / tanggal akhir (D21) | 2026-11-19 / 2026-12-09 | `ASSUMPTION` (A-22) — mohon koreksi bila berbeda |
| Rubrik | Tidak ada rubrik tertulis. Cassandra wajib. | `USER` |
| Prioritas | Produk jadi dan implementasi teknis. Laporan, presentasi, dan video ditangani tim. | `USER` |
| Target operasional | Berjalan lokal terlebih dahulu, kemudian di-hosting di cloud | `USER` |
| Repositori | `github.com/pakar-pakar-banjot/apiwowok` | `VERIFIED` |
| Alat AI | Claude Code, OpenAI Codex | `USER` |

## 2. Problem statement

**Versi brief (`USER`):** Pengguna kesulitan memantau perubahan jumlah deteksi hotspot dan sebaran geografisnya antar wilayah, terutama ketika observasi satelit baru terus tersedia.

**Usulan penajaman (`RECOMMENDATION`):**
> Data deteksi anomali termal (hotspot) dari satelit NASA FIRMS tersedia secara publik, tetapi dalam bentuk titik mentah per lintasan satelit tanpa atribut wilayah administrasi Indonesia. Akibatnya, pengguna sulit menjawab pertanyaan sederhana seperti *"berapa deteksi hotspot di provinsi X selama periode Y, dan bagaimana trennya?"* tanpa mengolah data sendiri. NusaFire menyediakan pipeline yang dapat diulang untuk mengolah data tersebut menjadi informasi per provinsi dan per waktu, serta dashboard untuk mengeksplorasinya — **dengan menegaskan bahwa deteksi hotspot bukan kebakaran yang terkonfirmasi.**

## 3. Batasan ilmiah (wajib tampil di aplikasi dan laporan)

Draf pernyataan (`RECOMMENDATION`, perlu disetujui):
> "Hotspot adalah deteksi anomali termal oleh sensor satelit, bukan konfirmasi kejadian kebakaran hutan/lahan. Satu kebakaran dapat menghasilkan banyak deteksi, dan sebagian deteksi dapat berasal dari sumber panas lain. Jumlah deteksi dipengaruhi oleh jumlah lintasan satelit, tutupan awan, dan resolusi sensor. Jumlah deteksi dari sensor berbeda tidak dapat dibandingkan secara langsung."

Konsekuensi desain:
- Semua label UI memakai "jumlah deteksi hotspot", bukan "jumlah kebakaran".
- Tidak ada fitur yang menyimpulkan luas terbakar, penyebab, atau prediksi kebakaran.
- Perbandingan antar periode hanya untuk produk/satelit yang sama.

## 4. Analisis target pengguna

Brief menyebut 5 kelompok pengguna. MVP 21 hari tidak dapat melayani kelimanya secara setara, sehingga diusulkan pengguna primer dan sekunder (`RECOMMENDATION`, lihat OQ-19).

| Kelompok | Kebutuhan utama | Pertanyaan khas | Implikasi untuk MVP | Prioritas usulan |
|---|---|---|---|---|
| Analis lingkungan | Tren & sebaran per wilayah, filter kualitas deteksi | "Provinsi mana yang deteksinya naik bulan ini?" | Timeline, ranking, filter confidence | **Primer** |
| Peneliti | Data yang dapat ditelusuri asal-usulnya, metodologi jelas | "Dari produk & versi mana data ini?" | Provenance, dokumentasi metodologi | **Primer** |
| Pemerintah daerah | Ringkasan wilayahnya | "Berapa deteksi di provinsi saya minggu ini?" | Eksplorasi per provinsi | Sekunder |
| Relawan bencana | Lokasi deteksi terbaru | "Di mana deteksi terbaru?" | Peta; butuh data NRT agar bermakna | Sekunder (bergantung NRT) |
| Masyarakat umum | Gambaran sederhana | "Apakah daerah saya ada hotspot?" | Bahasa sederhana + disclaimer | Tersier |

Catatan: kebutuhan relawan bencana akan data terkini **bergantung pada ingestion NRT** (OQ-10). Jika NRT tidak masuk MVP, aplikasi tidak boleh diklaim sebagai alat tanggap darurat.

## 5. Tujuan proyek

### Tujuan produk
- **O-P1** Pengguna dapat melihat jumlah deteksi hotspot per provinsi dan per hari/bulan untuk periode yang tersedia.
- **O-P2** Pengguna dapat melihat sebaran titik deteksi di peta untuk rentang waktu dan provinsi tertentu.
- **O-P3** Pengguna dapat memfilter berdasarkan confidence dan satelit (sejauh semantik field-nya konsisten — lihat C-03).

### Tujuan rekayasa (engineering)
- **O-E1** Pipeline ETL yang **idempoten** (menjalankan ulang input yang sama tidak mengubah hasil), menyimpan provenance, mencatat rekaman yang ditolak, dan memiliki checkpoint.
- **O-E2** Model data Cassandra berbasis query: setiap tabel memiliki query aplikasi yang jelas; tidak ada `ALLOW FILTERING` maupun full-table scan di jalur aplikasi.
- **O-E3** Minimal satu eksperimen Cassandra yang terdokumentasi lengkap (hipotesis → hasil aktual → interpretasi → keterbatasan).
- **O-E4** Reproduksibilitas: anggota tim lain dapat menjalankan sistem dari nol mengikuti README.

Target kuantitatif (latensi, volume, cakupan test) **belum ditetapkan** — akan ditetapkan di Fase 2 setelah volume data diketahui di Fase 1.

## 6. Ruang lingkup awal dan MVP

### 6.1 Pemetaan 10 fitur usulan ke MoSCoW (`RECOMMENDATION`, `PENDING`)

| # | Fitur brief | MoSCoW | Bentuk minimum untuk MVP | Alasan |
|---|---|---|---|---|
| 1 | Ringkasan nasional/regional | **Must** | Kartu total deteksi + timeline nasional untuk periode terpilih | Inti problem statement |
| 2 | Peta hotspot interaktif | **Must** | Titik deteksi untuk 1 provinsi atau rentang tanggal pendek; batas jumlah titik | Inti problem statement; volume harus dibatasi (C-10) |
| 3 | Timeline hotspot | **Must** | Jumlah deteksi per hari/bulan, nasional & per provinsi | Menjawab "perubahan jumlah" |
| 4 | Ranking provinsi | **Must** | Top-N provinsi untuk periode terpilih | Menjawab "antar wilayah" |
| 5 | Perbandingan periode historis | **Should** | Dua periode, produk/satelit sama, batas wilayah sama | Rawan salah tafsir metodologis (C-05) |
| 6 | Filter confidence & satelit | **Must** (confidence) / bergantung OQ-04 (satelit) | Filter confidence sesuai semantik produk terpilih | Filter satelit tidak bermakna jika hanya 1 satelit |
| 7 | Visualisasi distribusi FRP | **Should** | Histogram FRP untuk wilayah & periode | Nilai tambah, tidak inti |
| 8 | Eksplorasi regional | **Must (digabung)** | Digabung ke fitur 1–4 sebagai filter provinsi | Menghindari halaman ganda |
| 9 | Monitoring pipeline | **Must (minimal)** | Log per run: waktu, file sumber, jumlah diterima/ditolak/duplikat; endpoint + tabel sederhana | Bukti engineering; murah jika dirancang sejak awal |
| 10 | Eksperimen engineering Cassandra | **Must** (≥1 eksperimen partisi) / **Should** (replikasi & failure) | Lihat O-E3 | Cassandra wajib (OQ-01); eksperimen adalah bukti rekayasa utama |
| 11 | *(baru)* Hosting di cloud | **Must**, dijadwalkan **setelah** integrasi lokal (≥D13) | Satu server, image container yang sama dengan lokal, HTTPS, Cassandra tidak terekspos publik | Diminta tim (OQ-21); prioritas saat ini lokal |

### 6.2 Definisi MVP yang diusulkan

MVP = enam kapabilitas yang dapat didemonstrasikan end-to-end:

1. **ETL batch** untuk satu keluarga produk (usulan: VIIRS 375 m) dan satu periode historis: ekstraksi → validasi → normalisasi → pengayaan provinsi → deduplikasi → Cassandra, idempoten, dengan rejected records dan checkpoint.
2. **Read model Cassandra** untuk access pattern MVP (ditetapkan di Fase 3, bukan sekarang).
3. **FastAPI** dengan endpoint untuk ringkasan, timeline, ranking, titik peta, dan status pipeline.
4. **Dashboard React + Leaflet**: ringkasan + timeline, peta, ranking, filter tanggal/provinsi/confidence, disclaimer ilmiah.
5. **Monitoring pipeline minimal** (log run).
6. **Satu eksperimen partisi Cassandra** dengan hasil aktual.

Urutan pengiriman: keenam kapabilitas di atas harus berjalan **lokal** terlebih dahulu. Setelah itu, versi yang sama di-deploy ke cloud (fitur #11). Deployment cloud tidak boleh dimulai sebelum integrasi lokal berjalan (R-23).

### 6.3 Di luar ruang lingkup (Won't, untuk proyek ini)
- Kafka, Spark, Airflow, Kubernetes, atau orkestrator lain (`USER` + `RECOMMENDATION`).
- Autentikasi/akun pengguna, notifikasi/alert.
- Prediksi kebakaran, estimasi luas terbakar, klasifikasi penyebab.
- Perbandingan langsung jumlah deteksi antar sensor (MODIS vs VIIRS).
- Infrastruktur cloud berskala produksi (autoscaling, multi-region, load balancer bertingkat).
- Pengayaan sampai tingkat kabupaten/kecamatan (*Could*, hanya jika waktu tersisa).
- **Laporan akhir, presentasi, dan video demo**: ditangani tim, di luar tugas agen AI. Agen menyediakan dokumentasi teknis sebagai bahan (§7).

### 6.4 Could (jika waktu tersisa)
- Ingestion NRT terjadwal otomatis (cron sederhana) — versi manual adalah *Should*.
- Produk satelit kedua (mis. NOAA-20 di samping S-NPP).
- Pengayaan kabupaten/kota.
- Clustering/heatmap di peta.

## 7. Kriteria keberhasilan proyek (tingkat piagam)
1. Aplikasi berjalan end-to-end secara lokal dari `docker compose up` + perintah ingest yang terdokumentasi.
2. Menjalankan ulang ingest dengan input sama menghasilkan jumlah baris dan agregat yang identik (dibuktikan test).
3. Setiap tabel Cassandra memetakan ke ≥1 query aplikasi yang terdokumentasi.
4. Eksperimen memiliki hasil aktual yang dapat direproduksi.
5. Disclaimer ilmiah tampil di aplikasi.
6. Aplikasi dapat diakses di cloud melalui HTTPS, dengan Cassandra tidak terekspos ke internet.
7. Dokumentasi teknis tersedia sebagai bahan laporan tim: panduan instalasi, reproduksibilitas, dokumentasi database, ADR, dan hasil eksperimen.

## 8. Kendala (constraints)

| Kendala | Sumber |
|---|---|
| Sisa 21 hari kalender, termasuk akhir pekan | `USER` |
| 4 anggota × ±4 jam/hari ≈ 336 jam-orang (batas atas) | `USER` |
| Cassandra wajib | `USER` |
| Tech stack awal: Python, Pandas, GeoPandas, Cassandra, FastAPI, React, Leaflet, Docker Compose, Git | `USER` |
| Infrastruktur: lokal via Docker Compose untuk pengembangan; cloud untuk hosting (penyedia & anggaran `UNKNOWN` — OQ-23) | `USER` |
| Tidak semua anggota menjalankan Docker Compose; alur kerja harus mendukung stack parsial (OQ-27) | `USER` |
| Dua agen AI harus memakai spesifikasi yang sama | `USER` |
| Data sumber eksternal (NASA FIRMS) dengan kemungkinan batas akses/kuota | `AI-PRIOR` |
| Tidak boleh ada keputusan besar tanpa persetujuan manusia | `USER` |

## 9. Tim dan peran

Keputusan tim (OQ-03): dokumen memakai kode peran **R1–R4**; nama anggota ditetapkan kemudian. Ketersediaan ±4 jam/hari/orang. Peran disusun mengikuti alur pipeline agar setiap anggota memiliki area kepemilikan yang jelas dan minim tabrakan file.

| Peran | Tanggung jawab utama | Kepemilikan file (usulan) | Fase paling sibuk |
|---|---|---|---|
| **R1 — Data/ETL Lead** | Fase 1 profiling, validasi, normalisasi, pengayaan spasial, deduplikasi, rejected records | `pipeline/` | 1, 5 |
| **R2 — Cassandra Lead** | Access patterns, model data, Docker Cassandra, read model/agregat, eksperimen | `db/`, `experiments/` | 3, 5, 7 |
| **R3 — Backend & DevOps Lead** | Harness repo, Docker Compose, FastAPI, test API, deployment cloud & keamanan dasar | `api/`, `docker-compose*.yml`, `deploy/` | 4, 6, 7 |
| **R4 — Frontend & Product Lead** | Requirements, UI spec, React/Leaflet, disclaimer, koordinasi dokumentasi teknis | `web/`, `docs/` | 2, 6, 8 |

Peran tambahan (dirangkap): **Integrator/PM mingguan** (bergilir atau R4) yang menjaga papan tugas, gerbang persetujuan, dan jadwal. Setiap area wajib memiliki *reviewer* kedua dari anggota lain untuk mengurangi *bus factor*.

## 10. Jadwal tingkat tinggi (usulan)

Asumsi kalender (A-22): D1 = 2026-11-19, D21 = 2026-12-09. Fase 4 dijalankan paralel dengan Fase 2–3 karena tidak bergantung pada skema.

| Hari | Tanggal | Fase | Keluaran utama | Gerbang |
|---|---|---|---|---|
| D1 | 11-19 | 0 | Dokumen ini disetujui; MAP_KEY diminta | G0 |
| D2–D3 | 11-20 – 11-21 | 1 | Profil dataset nyata, rekomendasi produk & periode | G1 |
| D3–D5 | 11-21 – 11-23 | 2 + 3 | Requirements + access patterns + model Cassandra + kontrak API + ADR deployment | G2, G3 |
| D3–D5 | 11-21 – 11-23 | 4 (paralel) | Kerangka repo, Docker Compose, AGENTS.md/CLAUDE.md, test runner, mock API | G4 |
| D6–D12 | 11-24 – 11-30 | 5 + 6 (paralel) | ETL + Cassandra; API; frontend dengan mock lalu data nyata | Review mingguan |
| D12 | 11-30 | — | Penyedia cloud dipilih (OQ-23) | |
| D13 | 12-01 | — | **Integrasi end-to-end lokal pertama** (titik kritis) | |
| D13–D16 | 12-01 – 12-04 | 7 | Test integrasi, idempotensi, eksperimen Cassandra; **deployment cloud pertama** | |
| D17 | 12-05 | — | **Feature freeze**; aplikasi sudah berjalan di cloud | |
| D17–D19 | 12-05 – 12-07 | 7 | Perbaikan bug, hardening deployment, hasil eksperimen | |
| D20–D21 | 12-08 – 12-09 | 8 | Dokumentasi teknis final, checklist penerimaan. (Laporan, presentasi, dan video oleh tim) | G8 |

Prinsip: **integrasi end-to-end lokal paling lambat D13**. Jika pada D10 ETL belum memuat data nyata ke Cassandra, aktifkan kontingensi R-14. Jika deployment cloud belum berhasil pada D17, aktifkan kontingensi R-23.

## 11. Pemangku kepentingan dan persetujuan

| Pihak | Peran dalam persetujuan |
|---|---|
| Empat anggota tim | Menyetujui seluruh gerbang fase; keputusan konsekuensial butuh kesepakatan tim (mekanisme: `PENDING`, usulan: mayoritas + pemilik area setuju) |
| Dosen/asisten | Tidak ada rubrik tertulis (OQ-01); berhubungan langsung dengan tim |
| Agen AI | Mengusulkan, mengimplementasi, me-review — **tidak** menyetujui |
