# 08 — Kajian Alternatif Sumber Data Hotspot

Status: **DRAFT — menunggu keputusan tim** (2026-11-19). Disusun atas permintaan tim: mencari sumber selain NASA FIRMS, khususnya yang memiliki mekanisme selain REST pull (push/notifikasi/pub-sub).

Metode: pencarian web umum → kandidat → halaman resmi setiap kandidat dibaca langsung (2026-11-19). Label mengikuti [README](README.md#label-status-informasi). `VERIFIED` di dokumen ini berarti "dinyatakan di halaman resmi yang dibaca pada tanggal tersebut". Hal yang tidak dapat dibaca ditandai `UNKNOWN`.

---

## 1. Temuan kritis (berdampak langsung ke keputusan yang sudah ada)

| # | Temuan | Label | Dampak |
|---|---|---|---|
| K-1 | **Suomi NPP berhenti beroperasi pada 2 November 2026.** Pengiriman data VIIRS S-NPP dihentikan. NASA merekomendasikan **NOAA-20 dan NOAA-21** sebagai pengganti langsung. Arsip historis S-NPP tetap tersedia (2012-01-20 s.d. 2026-11-02). | `VERIFIED` (Earthdata alert & blog FIRMS) | Kandidat OQ-04 (A) "S-NPP saja" dan (B) "S-NPP + NOAA-20" **tidak bisa dipakai untuk polling NRT**. OQ-04 harus diputuskan ulang (§6). |
| K-2 | Terra (MODIS) dijadwalkan berhenti **1 Desember 2026**. | `VERIFIED` (banner Earthdata) | Memperkuat keputusan tidak memakai MODIS. |
| K-3 | Arsip FIRMS: NOAA-20 tersedia sejak **2018-04-01**, NOAA-21 sejak **2023-03-01**. Data NRT digantikan data standar (SP) dengan **jeda ±5 bulan**. | `VERIFIED` (halaman Archive Download FIRMS) | A-27 tervalidasi: backfill "365 hari terakhir" ≈ ±7 bulan SP + ±5 bulan NRT. |
| K-4 | Latensi NRT VIIRS di FIRMS: **< 3 jam (global)**. RT/URT (menit) hanya untuk AS/Kanada. | `VERIFIED` (FAQ FIRMS) | Polling lebih sering dari ±15 menit tidak menambah kesegaran data. |

---

## 2. Kandidat yang dikaji

### C1 — NASA FIRMS (sumber saat ini)

| Aspek | Temuan |
|---|---|
| Mekanisme | **Pull.** (a) Area API CSV: bounding box, `DAY_RANGE` 1–5, `DATE` opsional. (b) **OGC WFS**: region `SouthEast_Asia`, jendela 24 jam/7 hari, output CSV, **diperbarui setiap 15 menit**. (c) Archive Download: permintaan lewat web, hasil dikirim via email (SHP/CSV/JSON). Email alert ada untuk pengguna, tetapi bukan mekanisme mesin. `VERIFIED` |
| Satelit | VIIRS NOAA-20, NOAA-21 (375 m), MODIS, arsip S-NPP. `VERIFIED` |
| Data | Titik deteksi siap pakai (CSV) dengan confidence dan FRP; skema NRT dan SP konsisten. `VERIFIED` (sebagian; field lengkap dicek di Fase 1) |
| Riwayat | NOAA-20 sejak 2018, NOAA-21 sejak 2023. `VERIFIED` |
| Akses | MAP_KEY gratis via email; 5000 transaksi/10 menit. Country API "currently not available". `VERIFIED` |
| Kelebihan | Paling siap pakai; riwayat + NRT dalam satu skema; kuota longgar; tidak perlu parsing format ilmiah; terms jelas. |
| Kekurangan | Hanya pull (tidak ada push untuk mesin); latensi < 3 jam; bounding box ikut mengambil negara tetangga; tidak ada ID unik per deteksi. |

### C2 — NOAA Open Data Dissemination (NODD) di AWS: produk eFire VIIRS I-band

| Aspek | Temuan |
|---|---|
| Mekanisme | **Push / event-driven.** Bucket S3 publik `noaa-nesdis-n20-pds` dan `noaa-nesdis-n21-pds` (us-east-1), dengan **SNS topic** `NewNOAA20Object` / `NewNOAA21Object` untuk notifikasi objek baru. Protokol langganan: **"only Lambda and SQS"**. Membaca data tanpa akun AWS (`--no-sign-request`). `VERIFIED` (registry AWS Open Data) |
| Produk | Prefix `VIIRS_EFIRE_VIIRSI_EDR/` ada di bucket NOAA-20 dan NOAA-21, dengan data 2024–2026. File `.nc` berukuran ±0,4–1,7 MB per granule. `VERIFIED` (listing S3) |
| Granularitas | Granule ±83–85 detik; diperkirakan ±1.000 file/hari/satelit (ekstrapolasi dari listing terpotong, `ASSUMPTION`). |
| Latensi | Dari selisih waktu observasi dan waktu pembuatan di nama file (3 sampel): **±23–44 menit**. Ini inferensi, bukan pernyataan resmi. |
| Dokumentasi produk | Halaman eFire NOAA OSPO/STAR **tidak dapat dibaca** (403/404). Field per piksel, format NetCDF, dan cakupan granule: `UNKNOWN`. |
| Lisensi | "open to the public and can be used as desired"; NOAA meminta atribusi; tidak boleh menyiratkan endorsement. `VERIFIED` |
| Kelebihan | Satu-satunya kandidat dengan **push resmi + data publik + satelit yang sama dengan FIRMS (NOAA-20/21)**; latensi kemungkinan lebih baik dari FIRMS. |
| Kekurangan | Butuh akun AWS + SQS/Lambda untuk langganan SNS. Granule bersifat **global**, sehingga notifikasi untuk seluruh dunia harus disaring dan sebagian besar granule bukan Indonesia (nama file tidak memuat cakupan geografis). Butuh parsing NetCDF. Dokumentasi field tidak terverifikasi. Algoritma eFire berbeda dari produk NASA di FIRMS sehingga angkanya tidak identik. Riwayat di bucket baru sejak 2024. Kompleksitas tinggi untuk 21 hari. |

### C3 — ASMC WIS2 (WMO Information System 2.0, MQTT pub/sub)

| Aspek | Temuan |
|---|---|
| Mekanisme | **Push via MQTT.** Notifikasi WIS2 lewat Global Broker Météo-France (`globalbroker.meteo.fr:8883`, TLS, kredensial publik `everyone/everyone`). Topik: `origin/a/wis2/sg-mss-asmc/data/recommended/weather/space-based-observations/noaa-20/viirs`. URL data ada di `links[rel=canonical]` pesan notifikasi. `VERIFIED` |
| Produk | Active Fires EDR (CSPP), **750 m** (ID `JP1_AFEDR_750M_NRT/LATE`), NOAA-20 dan S-NPP (S-NPP sudah berhenti, K-1). Ada versi NRT (penerimaan lokal) dan Standard (delayed 8–12 jam). `VERIFIED` |
| Cakupan | Poligon 80–140°BT, 15°LS–30°LU. Ujung timur Papua (140–141°BT) di luar cakupan. `VERIFIED` |
| Frekuensi | "Twice daily" dengan jendela waktu UTC tertentu. Format file, retensi, dan arsip historis: `UNKNOWN` / tidak dinyatakan. |
| Terms | Hanya untuk penggunaan "personal, internal, non-commercial or informational purposes". Redistribusi butuh izin tertulis MSS. **Klausul 6.2 melarang akses otomatis ("robot … or automatic device") tanpa izin tertulis.** `VERIFIED` |
| Kelebihan | Pub/sub sungguhan (MQTT); data diterima di kawasan (ground station regional). |
| Kekurangan | **Risiko lisensi tinggi** untuk aplikasi publik dan akses otomatis; resolusi 750 m (bukan 375 m); tidak ada backfill; format tidak terdokumentasi; hanya 1 satelit aktif. File teks di situs ASMC hanya mencakup Sumatra dan Kalimantan, tanpa FRP maupun confidence per titik. |

### C4 — JAXA Himawari Monitor (P-Tree): produk Wild Fire (WLF) Himawari-9

| Aspek | Temuan |
|---|---|
| Mekanisme | **Pull via FTP** (`ftp.ptree.jaxa.jp`, path `/pub/himawari/L2/WLF/...`), dengan registrasi akun. Ada batas koneksi simultan. Sumber: hasil pencarian dan proyek pihak ketiga (`AI-PRIOR`/sekunder). |
| Produk | Satelit **geostasioner** yang meliput Indonesia, dengan resolusi temporal **10 menit** dan spasial **±2 km**. Latensi ±20–30 menit menurut pihak ketiga. |
| Terms | Hasil pencarian: data mulai 1 Feb 2026 boleh untuk komersial, data sebelumnya hanya non-profit. Halaman terms lama masih menyebut non-profit. `UNKNOWN` (belum terkonfirmasi). |
| Verifikasi | **Semua halaman P-Tree menampilkan "EORC Web and FTP service are temporarily unavailable"** saat dicek (2026-11-19). |
| Kelebihan | Cadence paling rapat (10 menit), paling mendekati "near real-time" untuk Indonesia. |
| Kekurangan | Resolusi 2 km jauh lebih kasar (kebakaran kecil terlewat). Studi pihak ketiga melaporkan F1 0,68 terhadap data lapangan. FTP tanpa HTTPS. Registrasi dengan waktu persetujuan `UNKNOWN`. Layanan sedang down, yang menjadi sinyal risiko keandalan. Sensornya berbeda sehingga jumlah deteksinya tidak dapat digabung atau dibandingkan dengan VIIRS. |

### C5 — Copernicus Data Space Ecosystem (CDSE): Sentinel-3 SLSTR FRP

| Aspek | Temuan |
|---|---|
| Mekanisme | **Push atau pull subscription resmi** lewat OData `POST /odata/v1/Subscriptions`. PUSH dikirim ke endpoint HTTPS milik kita (retry 3×). PULL masuk antrean (maks. 100.000) dengan read/ack. Event: created/modified/deleted. Batas **2 subscription aktif per user**. Wajib akun dan token. `VERIFIED` (ringkasan halaman dokumentasi) |
| Produk | `SL_2_FRP___` (NRT dan NTC). NTC tersedia sejak Mar 2016. NRT online hanya **"last one month"**. `VERIFIED` (ringkasan) |
| Detail | Latensi NRT, format (SAFE/NetCDF), ukuran granule, frekuensi lintasan di tropis, deteksi siang/malam: `UNKNOWN` (tidak dinyatakan di halaman yang dibaca). |
| Terms | Data Sentinel "free, full and open"; registrasi wajib; ada kuota (mis. 4 koneksi konkuren). `VERIFIED` |
| Kelebihan | Mekanisme subscription paling formal dan terdokumentasi; data terbuka; ada FRP. |
| Kekurangan | Revisit Sentinel-3 jauh lebih jarang daripada VIIRS NOAA-20+21 (`AI-PRIOR`); resolusi lebih kasar dari 375 m (`AI-PRIOR`); produk berupa granule ilmiah yang harus di-parse; NRT hanya 1 bulan; PUSH butuh endpoint publik; sensor berbeda dari VIIRS. |

### C6 — Sumber resmi Indonesia: SiPongi+ (Kemenhut), BMKG, BRIN

| Sumber | Temuan |
|---|---|
| SiPongi+ | Aplikasi berbasis JavaScript. UI menyediakan unduhan XLSX/TXT/KMZ, tetapi URL-nya tidak terlihat di HTML. Atribut sudah per kab/kota dan provinsi, confidence Low/Medium/High; sumber data tertulis "BMKG". Wajib mencantumkan "SIPONGI KEMENHUT". **Tidak ada API terdokumentasi.** `VERIFIED` |
| BMKG | Halaman Citra Polar Hotspot hanya berupa gambar PNG. Portal Data Terbuka BMKG tidak memuat dataset hotspot. `VERIFIED` |
| BRIN | `hotspot.brin.go.id` hanya shell JavaScript, tanpa API terdokumentasi. Berita 2026: memakai VIIRS S-NPP/NOAA-20 dari stasiun bumi lokal dengan pemrosesan ±30 menit (sekunder). |
| Kesimpulan | Tidak cocok sebagai sumber ingestion (butuh scraping, rapuh, terms tidak jelas). **Berguna sebagai pembanding/validasi manual** jumlah deteksi per provinsi, dengan atribusi. |

### C7 — Global Forest Watch / Global Nature Watch Data API

| Aspek | Temuan |
|---|---|
| Temuan | Dataset `nasa_viirs_fire_alerts` merupakan **turunan dari FIRMS** (VNP14IMGT), diperbarui **"Daily"**. Data terbaru 2026-11-18. Informasi versi "latest" tidak konsisten. Dokumentasi API berbasis JS dan tidak terbaca. Terms: akses dapat ditangguhkan "for any reason, without notice". `VERIFIED` |
| Kesimpulan | Tidak menambah nilai: lebih lambat dan menambah satu perantara dibanding FIRMS langsung. |

### Kandidat yang dikeluarkan lebih awal

| Kandidat | Alasan |
|---|---|
| Himawari L1b di AWS (NODD) | Hanya radiansi, sehingga kita harus membuat algoritma deteksi api sendiri. Di luar ruang lingkup. |
| GK2A (KMA) | API Hub butuh kunci baru; dokumentasi produk fire untuk Asia Tenggara tidak ditemukan (`UNKNOWN`). |
| CAMS GFAS | Produk grid harian, bukan titik deteksi. |
| NASA CMR/LANCE granule (VJ114IMG_NRT) | Data sama dengan FIRMS tetapi dalam format granule; butuh Earthdata Login; mekanisme subscription tidak terverifikasi. Tidak lebih baik dari C1/C2. |

---

## 3. Matriks tradeoff

Skala: ●●● baik · ●● sedang · ● buruk · ? tidak diketahui.

| Kriteria | C1 FIRMS | C2 NOAA NODD (SNS) | C3 ASMC WIS2 (MQTT) | C4 JAXA Himawari | C5 CDSE Sentinel-3 | C6 Sumber RI |
|---|---|---|---|---|---|---|
| Mekanisme | Pull (REST, WFS 15 mnt) | **Push** (SNS→SQS/Lambda) | **Push** (MQTT) | Pull (FTP) | **Push/Pull subscription** | Manual/scraping |
| Latensi | ●● < 3 jam | ●●● ±23–44 mnt (inferensi) | ●● (jendela 2×/hari) | ●●● 10 mnt + ±20–30 mnt | ? | ? |
| Resolusi spasial | ●●● 375 m | ●●● 375 m (I-band) | ●● 750 m | ● 2 km | ●● (AI-PRIOR) | ●●● (dari VIIRS) |
| Riwayat untuk backfill | ●●● 2018+ | ●● 2024+ | ● tidak ada | ? | ●●● 2016+ (NTC) | ● |
| Cakupan Indonesia | ●●● (bbox + clip) | ●●● (global, perlu filter) | ●● (tanpa 140–141°BT) | ●●● | ●●● | ●●● |
| Kesiapan format | ●●● CSV titik | ● NetCDF granule global | ? | ? | ● granule ilmiah | ●● XLSX/TXT |
| Dokumentasi | ●●● | ● (halaman produk 403/404) | ●● | ● (situs down) | ●● | ● |
| Lisensi untuk aplikasi publik | ●●● | ●●● (atribusi) | ● (non-komersial, larangan otomasi) | ●● (belum pasti) | ●●● | ●● (atribusi, terms tidak jelas) |
| Kompleksitas 21 hari | ●●● rendah | ● tinggi | ●● sedang | ●● sedang | ● tinggi | ● rapuh |
| Konsistensi dengan riwayat | ●●● satu skema | ●● beda algoritma | ● | ● beda sensor | ● beda sensor | — |

---

## 4. Analisis

1. **Mekanisme push memang ada** (C2, C3, C5). Namun di ketiganya, push hanya berupa **notifikasi bahwa file baru tersedia**. Setelah notifikasi diterima, kita tetap harus mengunduh lewat HTTP(S) dan mem-parse file ilmiah. Arsitekturnya berubah dari "poll tiap N menit" menjadi "event → fetch → parse". Volume data tidak berubah secara berarti.
2. **Keunggulan nyata push hanya latensi** (C2 kemungkinan ±1 jam vs FIRMS < 3 jam). Bagi persona primer (analis & peneliti), selisih ini tidak mengubah nilai aplikasi. Data tetap hanya muncul saat satelit melintas.
3. **Biaya push untuk proyek 21 hari tinggi.** C2 butuh akun AWS + SQS, filter granule global, parsing NetCDF tanpa dokumentasi field yang terverifikasi, dan hasilnya tidak identik dengan riwayat FIRMS. C3 terhalang lisensi. C5 berbeda sensor dan revisit-nya jarang.
4. **Polling FIRMS sudah memenuhi prinsip "near real-time" proyek.** WFS diperbarui tiap 15 menit dan latensi sumbernya < 3 jam. Polling 15–30 menit dengan upsert idempoten sudah menangkap data secepat FIRMS menyediakannya.
5. **Masalah terbesar justru K-1**, bukan mekanisme: satelit kandidat kita (S-NPP) sudah berhenti.

---

## 5. Rekomendasi (`RECOMMENDATION`)

1. **Sumber utama tetap NASA FIRMS**, tetapi produk diganti ke **VIIRS NOAA-20 (utama) + NOAA-21 (kedua)**, untuk backfill (SP) maupun polling (NRT).
   - NOAA-20 memiliki riwayat terpanjang yang masih berlanjut (sejak 2018).
   - NOAA-21 menambah frekuensi lintasan sejak 2023.
   - Satu skema data untuk riwayat dan data terkini.
2. **Mode incremental memakai polling FIRMS setiap 15–30 menit.** Bandingkan Area API (`DAY_RANGE=1`) dan WFS `SouthEast_Asia` di Fase 1, lalu pilih yang paling sederhana dan stabil.
3. **Rancang pipeline dengan antarmuka "source adapter"** (ekstraksi terpisah dari validasi→Cassandra), sehingga sumber push dapat ditambahkan tanpa mengubah inti pipeline.
4. **NOAA NODD + SNS (C2) sebagai *Could*** setelah D13, hanya jika tim ingin mendemonstrasikan ingestion event-driven. Jika dijalankan, perlakukan sebagai eksperimen terpisah dengan produk dan versi tersendiri, bukan pengganti FIRMS.
5. **Tidak dipakai:**
   - ASMC WIS2: terms melarang akses otomatis tanpa izin tertulis.
   - JAXA: sensor berbeda, 2 km, layanan sedang down, terms belum pasti.
   - CDSE: sensor berbeda, revisit jarang.
   - GFW: turunan FIRMS yang lebih lambat.
6. **SiPongi+/BMKG sebagai pembanding manual** di laporan atau eksperimen validasi, dengan atribusi resmi. Bukan sumber ingestion.

---

## 6. Keputusan yang dibutuhkan dari tim

| ID | Keputusan | Rekomendasi |
|---|---|---|
| OQ-04 (diputuskan ulang) | Produk satelit setelah S-NPP berhenti: (A) NOAA-20 saja · (B) NOAA-20 + NOAA-21 · (C) S-NPP untuk riwayat + NOAA-20/21 untuk data terkini | **B** sebagai kandidat profiling, final di gerbang Fase 1. C tidak disarankan karena riwayat dan data terkini berasal dari satelit berbeda sehingga timeline tidak konsisten. |
| OQ-28 (baru) | Sumber data | **FIRMS** sebagai sumber utama; NOAA NODD (push) sebagai *Could*. |

---

## 7. Sumber yang dibaca

NASA / FIRMS:
- [Suomi NPP Observations to Cease on November 2, 2026](https://www.earthdata.nasa.gov/data/alerts-outages/suomi-npp-observations-cease-november-2-2026)
- [Transitioning from Suomi NPP VIIRS & OMPS: What FIRMS Users Need to Know](https://www.earthdata.nasa.gov/news/blog/transitioning-from-suomi-npp-viirs-omps-what-firms-users-need-know)
- [NOAA NESDIS — Update #4 Cessation of S-NPP data](https://www.nesdis.noaa.gov/news/update-4-cessation-of-suomi-national-polar-orbiting-partnership-s-npp-data-users-november-02-2026-1540-utc-and-decommissioning-issued-november-2-2026-1800-utc)
- [FIRMS API](https://firms.modaps.eosdis.nasa.gov/api/) · [Area API](https://firms.modaps.eosdis.nasa.gov/api/area/) · [MAP_KEY](https://firms.modaps.eosdis.nasa.gov/api/map_key/) · [data_availability](https://firms.modaps.eosdis.nasa.gov/api/data_availability/) · [missing_data](https://firms.modaps.eosdis.nasa.gov/api/missing_data/)
- [FIRMS WFS info](https://firms2.modaps.eosdis.nasa.gov/mapserver/wfs-info/)
- [FIRMS Archive Download](https://firms.modaps.eosdis.nasa.gov/download/)
- [FIRMS FAQ](https://www.earthdata.nasa.gov/data/tools/firms/faq)

NOAA NODD:
- [Registry of Open Data on AWS — NOAA JPSS](https://registry.opendata.aws/noaa-jpss/)
- [open-data-registry noaa-jpss.yaml](https://github.com/awslabs/open-data-registry/blob/main/datasets/noaa-jpss.yaml)
- [NOAA Big Data Program JPSS docs](https://github.com/NOAA-Big-Data-Program/bdp-data-docs/tree/main/JPSS)
- Listing S3: `noaa-nesdis-n20-pds`, `noaa-nesdis-n21-pds` prefix `VIIRS_EFIRE_VIIRSI_EDR/`

ASMC:
- [ASMC Hotspot](https://asmc.asean.org/asmc-hotspot/) · [ASMC Terms of Use](https://asmc.asean.org/terms-of-use/)
- [ASMC WIS2 Portal](https://wis2.asmc.asean.org/) · [WIS2 FAQ](https://wis2.asmc.asean.org/faq/) · [Hotspot NOAA-20](https://wis2.asmc.asean.org/hotspot-reports-jpss-1-noaa-20/) · [WIS2 Terms](https://wis2.asmc.asean.org/terms-of-use/)
- [WMO training — Connecting to WIS2 over MQTT](https://training.wis2box.wis.wmo.int/practical-sessions/connecting-to-wis2-over-mqtt)

JAXA (situs sedang maintenance saat dicek; informasi dari hasil pencarian/sekunder):
- [JAXA Himawari Monitor](https://www.eorc.jaxa.jp/ptree/) · [FAQ](https://www.eorc.jaxa.jp/ptree/faq.html) · [Terms](https://www.eorc.jaxa.jp/ptree/terms.html)
- [Real-Time Wildfire Detection Algorithm Based on VIIRS Fire Product and Himawari-8 Data (Remote Sensing, 2023)](https://doi.org/10.3390/rs15061541)
- [10-minute level and near real-time wildfire detection for Himawari-8/9 (IJRS, 2026)](https://www.tandfonline.com/doi/abs/10.1080/01431161.2026.2628303)
- [GitHub — Syechran/firewatch](https://github.com/Syechran/firewatch) (proyek pihak ketiga)

Copernicus:
- [CDSE Subscriptions](https://documentation.dataspace.copernicus.eu/APIs/Subscriptions.html) · [Sentinel-3 di CDSE](https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel3.html) · [Quotas](https://documentation.dataspace.copernicus.eu/Quotas.html) · [Terms](https://dataspace.copernicus.eu/terms-and-conditions)

Indonesia:
- [SiPongi+](https://sipongi.gakkum.kehutanan.go.id/) · [BMKG Citra Polar Hotspot](https://www.bmkg.go.id/cuaca/satelit/polar-hotspot) · [Data Terbuka BMKG](https://data.bmkg.go.id/) · [BRIN Hotspot](https://hotspot.brin.go.id/)
- [BRIN Olah Data Satelit 30 Menit (Tangselpos)](https://tangselpos.id/detail/53978/brin-olah-data-satelit-30-menit-deteksi-dini-karhutla-lebih-cepat)

Global Forest Watch:
- [GFW Data API — nasa_viirs_fire_alerts](https://data-api.globalforestwatch.org/dataset/nasa_viirs_fire_alerts) · [Global Nature Watch Terms](https://globalnaturewatch.org/terms/)
