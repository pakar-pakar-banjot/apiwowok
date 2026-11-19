# 01 — Piagam Proyek Awal (Preliminary Project Charter)

Status: **DRAFT / PENDING** — belum disetujui tim. Label informasi: lihat [README](README.md#label-status-informasi).

## 1. Identitas proyek

| Atribut | Nilai | Label |
|---|---|---|
| Nama | NusaFire — Indonesian Hotspot Intelligence | `USER` |
| Jenis | Proyek universitas, aplikasi data engineering bergaya produksi | `USER` |
| Durasi | 21 hari kalender | `USER` |
| Tim | 4 mahasiswa | `USER` |
| Tanggal mulai (D1) / tanggal akhir | `UNKNOWN` — lihat OQ-02 | |
| Dosen/penilai & rubrik | `UNKNOWN` — lihat OQ-01 | |
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
| 10 | Eksperimen engineering Cassandra | **Must** (≥1 eksperimen partisi) / **Should** (replikasi & failure) | Lihat O-E3 | Kemungkinan inti penilaian mata kuliah (OQ-01) |

### 6.2 Definisi MVP yang diusulkan

MVP = enam kapabilitas yang dapat didemonstrasikan end-to-end:

1. **ETL batch** untuk satu keluarga produk (usulan: VIIRS 375 m) dan satu periode historis: ekstraksi → validasi → normalisasi → pengayaan provinsi → deduplikasi → Cassandra, idempoten, dengan rejected records dan checkpoint.
2. **Read model Cassandra** untuk access pattern MVP (ditetapkan di Fase 3, bukan sekarang).
3. **FastAPI** dengan endpoint untuk ringkasan, timeline, ranking, titik peta, dan status pipeline.
4. **Dashboard React + Leaflet**: ringkasan + timeline, peta, ranking, filter tanggal/provinsi/confidence, disclaimer ilmiah.
5. **Monitoring pipeline minimal** (log run).
6. **Satu eksperimen partisi Cassandra** dengan hasil aktual.

### 6.3 Di luar ruang lingkup (Won't, untuk proyek ini)
- Kafka, Spark, Airflow, Kubernetes, atau orkestrator lain (`USER` + `RECOMMENDATION`).
- Autentikasi/akun pengguna, notifikasi/alert.
- Prediksi kebakaran, estimasi luas terbakar, klasifikasi penyebab.
- Perbandingan langsung jumlah deteksi antar sensor (MODIS vs VIIRS).
- Hosting publik/produksi (kecuali diwajibkan rubrik — OQ-21).
- Pengayaan sampai tingkat kabupaten/kecamatan (*Could*, hanya jika waktu tersisa).

### 6.4 Could (jika waktu tersisa)
- Ingestion NRT terjadwal otomatis (cron sederhana) — versi manual adalah *Should*.
- Produk satelit kedua (mis. NOAA-20 di samping S-NPP).
- Pengayaan kabupaten/kota.
- Clustering/heatmap di peta.

## 7. Kriteria keberhasilan proyek (tingkat piagam)
1. Demo end-to-end berjalan dari `docker compose up` + perintah ingest yang terdokumentasi.
2. Menjalankan ulang ingest dengan input sama menghasilkan jumlah baris dan agregat yang identik (dibuktikan test).
3. Setiap tabel Cassandra memetakan ke ≥1 query aplikasi yang terdokumentasi.
4. Eksperimen memiliki hasil aktual yang dapat direproduksi.
5. Disclaimer ilmiah tampil di aplikasi dan laporan.
6. Laporan, presentasi ≤20 menit, dan naskah video selesai sebelum deadline.

## 8. Kendala (constraints)

| Kendala | Sumber |
|---|---|
| 21 hari kalender termasuk akhir pekan | `USER` |
| 4 anggota, kemungkinan sambil menjalani mata kuliah lain | `USER` / `ASSUMPTION` |
| Tech stack awal: Python, Pandas, GeoPandas, Cassandra, FastAPI, React, Leaflet, Docker Compose, Git | `USER` |
| Infrastruktur: laptop pribadi anggota (spesifikasi `UNKNOWN`) | `ASSUMPTION` |
| Dua agen AI harus memakai spesifikasi yang sama | `USER` |
| Data sumber eksternal (NASA FIRMS) dengan kemungkinan batas akses/kuota | `AI-PRIOR` |
| Tidak boleh ada keputusan besar tanpa persetujuan manusia | `USER` |

## 9. Tim dan peran (usulan, `PENDING` — lihat OQ-03)

Nama anggota `UNKNOWN`. Peran disusun mengikuti alur pipeline agar setiap anggota memiliki area kepemilikan yang jelas dan minim tabrakan file.

| Peran | Tanggung jawab utama | Kepemilikan file (usulan) | Fase paling sibuk |
|---|---|---|---|
| **R1 — Data/ETL Lead** | Fase 1 profiling, validasi, normalisasi, pengayaan spasial, deduplikasi, rejected records | `pipeline/` | 1, 5 |
| **R2 — Cassandra Lead** | Access patterns, model data, Docker Cassandra, read model/agregat, eksperimen | `db/`, `experiments/` | 3, 5, 7 |
| **R3 — Backend & DevOps Lead** | Harness repo, Docker Compose, FastAPI, test API, CI lokal | `api/`, `docker-compose*.yml` | 4, 6 |
| **R4 — Frontend & Product Lead** | Requirements, UI spec, React/Leaflet, disclaimer, koordinasi dokumen akhir | `web/`, `docs/` | 2, 6, 8 |

Peran tambahan (dirangkap): **Integrator/PM mingguan** (bergilir atau R4) yang menjaga papan tugas, gerbang persetujuan, dan jadwal. Setiap area wajib memiliki *reviewer* kedua dari anggota lain untuk mengurangi *bus factor*.

## 10. Jadwal tingkat tinggi (usulan)

Tanggal relatif (D1 = hari pertama, `UNKNOWN`). Fase 4 dijalankan paralel dengan Fase 2–3 karena tidak bergantung pada skema.

| Hari | Fase | Keluaran utama | Gerbang |
|---|---|---|---|
| D1 | 0 | Dokumen ini disetujui; MAP_KEY diminta; peran ditetapkan | G0 |
| D2–D3 | 1 | Profil dataset nyata, rekomendasi produk & periode | G1 |
| D3–D5 | 2 + 3 | Requirements + access patterns + model Cassandra + kontrak API | G2, G3 |
| D3–D5 | 4 (paralel) | Kerangka repo, Docker Compose, AGENTS.md/CLAUDE.md, test runner | G4 |
| D6–D12 | 5 + 6 (paralel) | ETL + Cassandra; API; frontend dengan data mock lalu data nyata | Review mingguan |
| D13 | — | **Integrasi end-to-end pertama** (titik kritis) | |
| D13–D16 | 7 | Test integrasi, idempotensi, eksperimen Cassandra | |
| D17 | — | **Feature freeze** | |
| D17–D19 | 7 | Perbaikan bug, hasil eksperimen, dokumentasi teknis | |
| D20–D21 | 8 | Laporan, presentasi, video, checklist penerimaan | G8 |

Prinsip: **integrasi end-to-end paling lambat D13**. Jika pada D10 ETL belum memuat data nyata ke Cassandra, aktifkan kontingensi R-14.

## 11. Pemangku kepentingan dan persetujuan

| Pihak | Peran dalam persetujuan |
|---|---|
| Empat anggota tim | Menyetujui seluruh gerbang fase; keputusan konsekuensial butuh kesepakatan tim (mekanisme: `PENDING`, usulan: mayoritas + pemilik area setuju) |
| Dosen/asisten | Sumber rubrik; persetujuan topik jika diwajibkan (`UNKNOWN`) |
| Agen AI | Mengusulkan, mengimplementasi, me-review — **tidak** menyetujui |
