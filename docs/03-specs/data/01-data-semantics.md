# 01 — Semantik Data & Aturan Perhitungan (A-P2-001)

> Fase 2 · **DRAF agen 2026-11-22** · Pemilik: R1 (Lanang) · Status: `RECOMMENDATION`, menunggu review Lanang dan persetujuan G2 (kebijakan data).
> Sumber: keputusan G1 (HD-09, HD-10, HD-11), OQ-08…OQ-12, [04](../../01-dataset/04-nrt-vs-sp-and-latency.md), [06](../../01-dataset/06-data-quality-rules.md), [07](../../01-dataset/07-dataset-recommendation.md), [draf story](../../02-requirements/00-draft-user-stories.md).
> Label: [legenda](../../00-discovery/README.md#label-status-informasi). Semua pilihan di bawah adalah **rekomendasi agen** (`RECOMMENDATION`), diisi penuh supaya tim tinggal menyetujui atau mengubah. Tidak ada yang sah sebelum G2.

## 0. Cara membaca dokumen ini

- **SEM-xx** = aturan semantik. Setiap angka di dashboard harus dapat dijelaskan oleh satu aturan SEM-xx (kriteria penerimaan A-P2-001). Peta jejaknya ada di [§4](#4-peta-jejak-angka-dashboard--sem).
- **KEP-xx** = keputusan yang butuh persetujuan manusia (rangkuman di [§3](#3-keputusan-yang-butuh-persetujuan-g2)). Setiap SEM yang bergantung pada keputusan baru diberi penanda **⚑ KEP-xx**.
- Hotspot ≠ kebakaran terkonfirmasi. Semua label UI memakai "deteksi hotspot".
- Angka hanya dari Fase 1 (bersumber ke dokumen 03/04/06) atau dari perintah yang dijalankan sesi ini (bukti di deskripsi PR). Contoh yang dibuat sendiri diberi label **ILUSTRASI**.

## 1. Definisi inti

### SEM-00 — Definisi formal "jumlah deteksi"

Jumlah deteksi untuk satu kueri adalah banyaknya **kejadian deteksi** `e` (satu baris produk FIRMS yang lolos DQ, setelah dedup) yang memenuhi semua syarat berikut:

```
count(P, [d1..d2], S, C, F) =
  | { e :
        e.region_status = INSIDE                       (SEM-02)
    and e.province     ∈ P                             (P = {38 provinsi} bila tidak difilter)
    and local_date(e)  ∈ [d1..d2]                      (SEM-03)
    and e.satellite    ∈ S                             (SEM-07)
    and e.confidence   ∈ C                             (SEM-04)
    and F(e)                                           (SEM-05; F = benar bila filter tipe tidak aktif)
    and e dipilih menurut presedensi produk            (SEM-06)
  } |
```

- Satu **kejadian deteksi** = satu `detection_id` (hash `(processing_level, satellite, acq_datetime_utc, latitude, longitude)`; [04 §2](../../01-dataset/04-nrt-vs-sp-and-latency.md#2-aturan-tumpang-tindih-nrtsp-yang-diusulkan-keputusan-hd-10)). Baris yang ditolak DQ-01…DQ-06, DQ-13…DQ-15 **tidak** menjadi kejadian dan tidak pernah dihitung. Duplikat DQ-08 menjadi satu kejadian.
- Semua angka di dashboard (total, timeline, ranking, peta, histogram) adalah **kueri `count` atau turunannya** dengan parameter berbeda. Tidak ada angka dashboard yang boleh dihitung dengan definisi lain.
- **Invarian:** hasil `count` harus identik apa pun jalur penghitungannya (dari baris detail, atau dari pra-agregasi milik R2). Pra-agregasi hanya cache, bukan definisi.

### SEM-01 — Satuan hitung dan klaim ilmiah

- Satuan = deteksi hotspot (piksel VIIRS 375 m yang terdeteksi pada satu lintasan), **bukan** jumlah kebakaran, titik api unik, atau luas terbakar.
- Satu kebakaran yang sama dapat menghasilkan banyak deteksi (banyak piksel, banyak lintasan, dua satelit). Tidak ada penggabungan antar-deteksi (tidak ada pengelompokan spasial atau temporal) di MVP. `RECOMMENDATION`
- Jumlah deteksi antar sensor/produk tidak dibandingkan sebagai ukuran kebakaran (STATUS §2 butir 6).

## 2. Aturan semantik

### SEM-02 — Wilayah: INSIDE, OUTSIDE, dan total nasional  ⚑ KEP-02

Dasar: OQ-11, DQ-07, DQ-07b.

1. Setiap kejadian punya `region_status` ∈ {`INSIDE`, `OUTSIDE`} dan, bila `INSIDE`, tepat satu `province` (kode BIG, 38 provinsi).
2. Titik yang masuk >1 poligon (DQ-07b) dihitung **sekali**, di poligon pertama menurut urutan fitur BIG. Jumlah per provinsi tidak pernah menghitung satu kejadian dua kali.
3. **OUTSIDE tidak masuk agregat apa pun**: tidak di ranking, tidak di total per provinsi, **dan tidak di total nasional**. Jumlahnya dilaporkan terpisah sebagai angka "deteksi di luar provinsi (tidak dihitung)" pada monitoring dan di catatan metodologi.
4. Akibatnya **total nasional = jumlah 38 provinsi** (identik dengan jumlah ranking penuh).
5. Tidak ada snapping titik tepi (HD-11). Titik ≤ 2 km dari tepi poligon tetap OUTSIDE.

| Opsi total nasional | Kelebihan | Kekurangan |
|---|---|---|
| **A. Hanya INSIDE (rekomendasi)** | Total = jumlah provinsi; satu aturan menjelaskan semua angka; tidak ada titik lautan atau negara tetangga di "Indonesia" | Total lebih kecil dari semua baris di raw zone |
| B. INSIDE + OUTSIDE | Cocok dengan jumlah baris mentah | Memasukkan titik offshore dan negara tetangga (bbox ekstraksi memuat tetangga) ke "total Indonesia"; total ≠ jumlah ranking |

Angka Fase 1 (`VERIFIED`, [06](../../01-dataset/06-data-quality-rules.md), per produk N20 SP · N21 SP · N20 NRT · N21 NRT): OUTSIDE = 104.763 · 102.091 · 62.560 · 81.751 baris; di antaranya ≤ 2 km dari tepi = 2.892 · 2.671 · 2.992 · 3.127. Untuk N20 SP, deteksi dekat tepi hanya 2,76% dari OUTSIDE (2.892 / 104.763). Dokumen 06 mencatat bahwa keputusan tanpa snapping mengeluarkan paling banyak 0,6% deteksi dari ranking.

Keterbatasan wajib disebut di catatan metodologi: versi batas wilayah (BIG Juni 2026, cadangan B5, lisensi `UNKNOWN`, HD-08) menentukan keanggotaan provinsi. **Mengganti versi batas = memproses ulang semua `province`, dan angka dapat berubah.** Satu kueri hanya boleh memakai satu versi batas (`boundary_version`, FR-13).

### SEM-03 — Tanggal lokal dan zona waktu

Dasar: OQ-08.

1. Timestamp kanonis `acq_datetime_utc` = `acq_date` + `acq_time` (di-pad 4 digit, HHMM UTC).
2. **Tanggal lokal** `local_date(e)` = tanggal dari `acq_datetime_utc + offset(zona provinsi e)`. Offset: WIB +7, WITA +8, WIT +9. Zona ditentukan oleh **provinsi** kejadian, bukan koordinat.
3. Kejadian OUTSIDE tidak punya provinsi, sehingga tidak punya tanggal lokal dan tidak dihitung (SEM-02). Tanggal UTC-nya tetap disimpan untuk monitoring.
4. Agregasi harian = per `local_date`. Agregasi bulanan = bulan kalender dari `local_date` (bukan bulan UTC). Tidak ada agregasi mingguan di MVP.
5. **Total nasional untuk satu tanggal** = jumlah dari tanggal lokal masing-masing provinsi. Karena itu tanggal nasional mencampur tiga zona. Selisih antar zona maksimal 2 jam, sehingga hanya deteksi dalam 2 jam menjelang tengah malam yang terpengaruh. Hal ini wajib disebut di catatan metodologi. `RECOMMENDATION`
6. Satu tanggal UTC `D` dapat berkontribusi ke dua tanggal lokal (`D` dan `D+1`). Konsekuensi untuk rekonsiliasi: ganti satu tanggal UTC = hitung ulang dua tanggal lokal ([04 §2](../../01-dataset/04-nrt-vs-sp-and-latency.md#2-aturan-tumpang-tindih-nrtsp-yang-diusulkan-keputusan-hd-10)).

Pemetaan provinsi → zona (`AI-PRIOR`, **harus dicocokkan dengan atribut provinsi BIG saat A-P5-005**, 18 + 12 + 8 = 38):

| Zona | Provinsi |
|---|---|
| WIB (UTC+7) | Aceh, Sumatera Utara, Sumatera Barat, Riau, Kepulauan Riau, Jambi, Sumatera Selatan, Kepulauan Bangka Belitung, Bengkulu, Lampung, Banten, DKI Jakarta, Jawa Barat, Jawa Tengah, DI Yogyakarta, Jawa Timur, Kalimantan Barat, Kalimantan Tengah |
| WITA (UTC+8) | Bali, Nusa Tenggara Barat, Nusa Tenggara Timur, Kalimantan Selatan, Kalimantan Timur, Kalimantan Utara, Sulawesi Utara, Gorontalo, Sulawesi Tengah, Sulawesi Barat, Sulawesi Selatan, Sulawesi Tenggara |
| WIT (UTC+9) | Maluku, Maluku Utara, Papua, Papua Barat, Papua Barat Daya, Papua Selatan, Papua Tengah, Papua Pegunungan |

Tabel ini harus disimpan sebagai data referensi (bukan di-hardcode di banyak tempat) dan diuji: tepat 38 provinsi, tidak ada yang tanpa zona.

**ILUSTRASI** (nilai contoh, bukan baris data; dihitung dengan perintah di deskripsi PR). `acq_date = 2025-03-10`:

| `acq_time` (UTC) | WIB | WITA | WIT | Tanggal lokal (WIB / WITA / WIT) |
|---|---|---|---|---|
| 0645 | 03-10 13:45 | 03-10 14:45 | 03-10 15:45 | 10 / 10 / 10 |
| 1500 | 03-10 22:00 | 03-10 23:00 | 03-11 00:00 | 10 / 10 / **11** |
| 1630 | 03-10 23:30 | 03-11 00:30 | 03-11 01:30 | 10 / **11** / **11** |
| 1830 | 03-11 01:30 | 03-11 02:30 | 03-11 03:30 | **11** / **11** / **11** |

Titik pindah tanggal: UTC ≥ 17:00 → hari berikutnya di WIB, ≥ 16:00 di WITA, ≥ 15:00 di WIT. Karena lintasan malam di Indonesia berada pada kisaran 15–19 UTC ([04 §3](../../01-dataset/04-nrt-vs-sp-and-latency.md#3-latensi-nrt-a-p1-008)), **lintasan malam sering membelah dua tanggal lokal**, dan unit test konversi waktu wajib mencakup kasus ini.

### SEM-04 — Confidence  ⚑ KEP-01 (= HD-12)

Dasar: OQ-09, DQ-13.

1. Semua deteksi disimpan dengan `confidence` ∈ {`l`, `n`, `h`} (OQ-09). Tidak ada penghapusan saat ingest.
2. Filter confidence adalah himpunan pilihan `C ⊆ {l, n, h}`; ia berlaku sama untuk **semua panel** (FR-06a) dan nilainya selalu tampil di panel.
3. **Default tampilan: `C = {l, n, h}` (semua).** Panel menampilkan rincian jumlah per confidence di tooltip atau legenda.
4. `C = ∅` tidak diperbolehkan (UI mencegahnya).

| Opsi default | Dampak | Penilaian |
|---|---|---|
| **A. Semua (l+n+h) (rekomendasi)** | Konsisten dengan OQ-09 dan dengan SEM-00 (satu definisi dasar tanpa saringan tersembunyi); sebanding antara SP dan NRT (confidence sama pada 99,9% pasangan, [04 §1](../../01-dataset/04-nrt-vs-sp-and-latency.md#1-perbandingan-noaa-21-nrt-vs-sp-tumpang-tindih-12-bulan)); tidak ada klaim "ini yang benar-benar kebakaran" | Mengandung deteksi confidence rendah yang lebih mungkin bukan kebakaran (`AI-PRIOR`, belum diukur di data tim); analis harus menyaring sendiri |
| B. `n` + `h` | Jumlah lebih "bersih" | Menyembunyikan data secara default; pembagian `l` vs `n` berbeda antara NRT dan SP pada sebagian kecil deteksi (`n→l` 76, `l→n` 24, `h→l` 1 pasang), sehingga tanggal NRT dan SP sedikit tidak sebanding |
| C. `h` saja | Paling konservatif | Membuang sebagian besar deteksi tanpa dasar terukur; mudah dibaca sebagai "ini kebakaran terkonfirmasi" (salah) |

`PENDING`: distribusi `l`/`n`/`h` pada data tim **belum dikutip di dokumen ini**. Sebelum G2, jalankan agregasi confidence dari raw zone (dengan izin) supaya KEP-01 diputuskan dengan angka. Tanpa angka itu, rekomendasi A tetap berdiri karena alasannya adalah konsistensi dan transparansi, bukan jumlah.

### SEM-05 — Sumber statis & tipe non-vegetasi  ⚑ KEP-03

Dasar: OQ-12, DQ-11, HD-11 (opsi (a)).

1. Field `type` ∈ {0 dugaan vegetasi, 1 gunung api aktif, 2 sumber statis darat, 3 offshore}; **NULL pada seluruh data NRT** (kolom tidak ada, DQ-01/DQ-02).
2. **Semua tipe dihitung** (SEM-00 tidak menyaring `type`). Flag `NON_VEGETATION_TYPE` pada tipe 1–3 hanya penanda.
3. Filter opsional **"hanya dugaan vegetasi (type = 0)"** tersedia di UI, **hanya** bila seluruh rentang tanggal terpilih (dalam tanggal UTC kejadian) berasal dari produk SP.
4. Bila rentang memuat satu pun hari NRT, filter ini **dinonaktifkan** dengan pesan "tidak tersedia untuk data NRT (tipe sumber tidak ada)". Tidak ada penyaringan separuh-separuh.

| Opsi perilaku filter di rentang campuran SP+NRT | Dampak |
|---|---|
| **A. Nonaktifkan filter (rekomendasi)** | Sederhana; setiap angka punya satu penjelasan; tidak menyesatkan |
| B. Terapkan ke SP saja, NRT ikut tanpa disaring | Angka mencampur dua definisi tanpa terlihat |
| C. Terapkan ke SP, buang NRT | Hasil terlihat "kurang" untuk hari terbaru tanpa alasan jelas |
| D. Bangun masker lokasi statis dari SP dan terapkan ke NRT | Konsisten, tetapi menambah logika dan `ASSUMPTION` (lokasi statis tetap); dinilai *Could* oleh [06](../../01-dataset/06-data-quality-rules.md) |

Kerugian opsi A: karena NRT mencakup bulan-bulan terakhir (NOAA-20 sejak 2026-08-01), rentang "30 hari terakhir" biasanya tidak bisa memakai filter ini. Ini keterbatasan yang diterima, dan dicatat di UI serta laporan. Angka Fase 1 (`VERIFIED`): tipe 1–3 = 54.067 (10,4%) pada N20 SP dan 56.788 (11,0%) pada N21 SP di dalam Indonesia, sehingga filter mengubah jumlah sekitar 10–11% untuk periode SP.

### SEM-06 — Presedensi SP/NRT dan stabilitas angka  ⚑ (HD-10, tidak ada keputusan baru)

Dasar: HD-10, [04 §2](../../01-dataset/04-nrt-vs-sp-and-latency.md#2-aturan-tumpang-tindih-nrtsp-yang-diusulkan-keputusan-hd-10).

1. Untuk setiap `(satellite, acq_date UTC)` hanya **satu** `processing_level` yang berlaku: **SP** bila tanggal itu ≤ akhir ketersediaan SP (dibaca dari `data_availability` saat run), jika tidak **NRT**. Kedua produk tidak pernah hidup berdampingan untuk satu tanggal. Tidak ada pencocokan per deteksi.
2. Karena itu SEM-00 tidak perlu memilih saat kueri: data yang dimuat sudah memenuhi aturan ini. Bila rekonsiliasi (A-P7-003, *Should*) belum aktif, hari NRT tetap NRT meski SP sudah terbit.
3. **Angka tanggal yang masih NRT dapat berubah** setelah diganti SP. Setiap tanggal lokal membawa label produk: `SP` (semua kontribusi UTC-nya SP), `NRT` (semua NRT), atau `campuran`. UI wajib menandai tanggal `NRT` dan `campuran` sebagai "sementara".
4. Besar perubahan (`VERIFIED` hanya untuk NOAA-21, jendela 2025-08-01…2026-07-31, [04 §1](../../01-dataset/04-nrt-vs-sp-and-latency.md#1-perbandingan-noaa-21-nrt-vs-sp-tumpang-tindih-12-bulan)): NRT 121.213 baris vs SP 120.248, selisih 965 baris (0,80% dari SP). Median rasio harian NRT/SP = 1,00 (p5 1,00; p95 1,04). Tetapi pada hari tertentu NRT bisa jauh lebih sedikit (2025-09-05: NRT 75 vs SP 422). **Perilaku untuk NOAA-20 tidak diukur** karena NRT-nya baru mulai 2026-08-01 (`UNKNOWN`).
5. Dua tanggal lokal yang berbagi satu tanggal UTC yang diganti ikut berubah (SEM-03 butir 6).

### SEM-07 — Satelit: default dan penggabungan  ⚑ KEP-04

Dasar: OQ-04, charter §3, [07 §2](../../01-dataset/07-dataset-recommendation.md#2-produk).

1. Filter satelit `S ⊆ {NOAA-20, NOAA-21}`, berlaku sama untuk semua panel (FR-06b).
2. **Default tampilan: `S = {NOAA-20}`** (satelit utama, OQ-04). `S = {NOAA-20, NOAA-21}` ("gabungan") dan `{NOAA-21}` dapat dipilih.
3. **Gabungan = penjumlahan deteksi dua sensor**, tanpa deduplikasi antar-satelit (dua satelit dapat melihat kebakaran yang sama di lintasan berbeda, dan ini dua deteksi). Panel gabungan wajib menyatakan: "jumlah deteksi dari dua sensor; bergantung pada jumlah lintasan".
4. **Diskontinuitas seri gabungan pada 2023-03-01**: NOAA-21 tersedia sejak 2023-03-01, sehingga sebelum tanggal itu "gabungan" hanya berisi NOAA-20. Rentang yang memuat tanggal < 2023-03-01 dengan `S` gabungan wajib menampilkan peringatan; **perbandingan periode** (FR-05) dengan `S` gabungan hanya diperbolehkan bila kedua periode seluruhnya ≥ 2023-03-01.
5. Perbandingan periode mengunci `S` yang sama di kedua sisi (charter §3).

| Opsi default | Dampak |
|---|---|
| **A. NOAA-20 saja (rekomendasi)** | Seri konsisten sepanjang 2023-01-01…sekarang (satu sensor); tidak ada lonjakan buatan pada 2023-03-01; sejalan dengan OQ-04 ("utama"); aman dari salah baca "dua kali lebih banyak kebakaran" |
| B. Gabungan | Menampilkan semua data; tetapi seri tidak seragam sebelum/sesudah 2023-03-01 dan jumlahnya bergantung jumlah lintasan dua satelit |
| C. NOAA-21 saja | Seri hanya mulai 2023-03-01; bukan satelit utama |

Cakupan jam lintasan juga berbeda antar satelit (NOAA-21 dan NOAA-20 mengorbit berselang ±50 menit; `AI-PRIOR`, belum diukur). Karena itu **jumlah deteksi antar satelit tidak boleh dibaca sebagai selisih aktivitas kebakaran**.

### SEM-08 — Hari tidak lengkap dan hari berjalan

Dasar: DQ-12, [04 §3](../../01-dataset/04-nrt-vs-sp-and-latency.md#3-latensi-nrt-a-p1-008).

1. Tanggal UTC yang ditandai `INCOMPLETE_DAY` (DQ-12: ada di tabel `missing_data` FIRMS, atau 0 baris untuk `(satellite, tanggal)`) **tidak boleh ditampilkan sebagai "0 deteksi"**. Ia ditampilkan sebagai "data tidak lengkap" (celah di timeline, tanpa titik nol).
2. Tanggal lokal `L` dianggap tidak lengkap bila salah satu tanggal UTC yang dicakupnya (SEM-03 butir 6) berstatus `INCOMPLETE_DAY` untuk **salah satu satelit dalam `S`**.
3. **Tanggal lokal "sebagian"** (hari berjalan): tanggal lokal `L` dianggap *sebagian* bila `acq_datetime` terbaru yang sudah dimuat untuk satelit mana pun di `S` masih lebih awal dari akhir jendela UTC milik `L` untuk zona provinsi itu. Penentuannya per `(satellite, zona)`, bukan per hari kalender. Tanggal "sebagian" ditandai di timeline dan tidak ikut perbandingan periode (SEM-10).
4. Karena latensi NRT 1,8 sampai ±9 jam (`VERIFIED` pada pengamatan 2 hari), data hari ini hampir selalu tidak lengkap. UI memakai kalimat "biasanya 2–3 jam, kadang hingga ±9 jam", bukan "real-time". Ambang peringatan/basi data (usulan 18 jam / 30 jam) milik C-P2-001, bukan dokumen ini.
5. Musim hujan dapat membuat satu lintasan benar-benar 0 deteksi. "0 deteksi" valid dan beda dengan "tidak lengkap": pembedanya adalah ada atau tidaknya file/lintasan (DQ-12), bukan nilai nol.

### SEM-09 — Flag kualitas tidak memengaruhi hitungan

Dasar: prinsip 06 ("simpan semua yang valid secara struktural").

- Flag `TI4_SATURATED` (DQ-09), `FRP_ZERO` (DQ-10), `MULTI_POLYGON` (DQ-07b), `NON_VEGETATION_TYPE` (DQ-11) **tidak mengubah hitungan**. Sisa efek yang sah hanyalah `OUTSIDE` (SEM-02) dan filter eksplisit pengguna (SEM-04, SEM-05).
- Dampak terukur Fase 1 (`VERIFIED`, N20 SP · N21 SP · N20 NRT · N21 NRT): `TI4_SATURATED` 16.647 · 19.762 · 36.359 · 34.042; `FRP_ZERO` 0 · 9 · 3 · 17; `MULTI_POLYGON` 30 · 16 · 34 · 26.
- Duplikat DQ-08 dihitung sekali; saat nilainya berbeda dipilih FRP tertinggi lalu `bright_ti4` tertinggi (0 · 1 · 1 · 0 kasus, semuanya konflik nilai).
- Pengamatan non-aturan ([06](../../01-dataset/06-data-quality-rules.md): `bright_ti4` < 280 K dan `bright_ti4` < `bright_ti5`) tidak dipakai untuk menyaring.

### SEM-10 — Perbandingan periode

Dasar: FR-05 (*Should*), charter §3.

Dua periode A dan B sah dibandingkan hanya bila:
1. `S`, `C`, filter tipe (SEM-05), provinsi, dan `boundary_version` **identik** di kedua sisi.
2. Panjang periode sama (dalam hari lokal) **atau** UI menampilkan nilai per hari, bukan total, dan menyatakan perbedaan panjangnya.
3. Tidak ada tanggal "tidak lengkap" atau "sebagian" (SEM-08) di kedua periode; bila ada, perbandingan ditolak atau tanggal itu dikeluarkan secara eksplisit dengan keterangan.
4. Bila `S` gabungan, kedua periode ≥ 2023-03-01 (SEM-07 butir 4).
5. Catatan metodologi menyatakan: perubahan jumlah dapat mencerminkan perubahan jumlah lintasan, cakupan awan, dan produk (SP vs NRT, SEM-06), bukan hanya perubahan aktivitas kebakaran.

### SEM-11 — Ranking provinsi

Dasar: FR-04, OQ-11.

1. Ranking = Top-N provinsi menurut `count` (SEM-00) untuk filter aktif, **jumlah absolut**. Urutan imbang diputus berdasar kode provinsi (deterministik).
2. OUTSIDE tidak ikut ranking (SEM-02).
3. Per-luas (deteksi per km²) **tidak termasuk MVP**. Ranking absolut cenderung menaikkan provinsi besar; hal ini dicatat sebagai keterbatasan di UI. Ranking per luas hanya dapat dibuat dengan luas dari atribut BIG (`LUASWH`, [05](../../01-dataset/05-boundary-sources.md)) dan dinilai *Could*. `RECOMMENDATION` ⚑ KEP-05.

### SEM-12 — Peta: pemotongan titik dan histogram FRP

Dasar: FR-02, FR-07.

1. Titik di peta berasal dari himpunan SEM-00 yang sama dengan angka di panel lain. Jumlah titik tampil dibatasi (batas angka: NFR milik C-P2-001).
2. Bila hasil dipotong, **jumlah total (SEM-00) dan jumlah yang tampil sama-sama dilaporkan**. Pemilihan titik bersifat deterministik: urutkan menurut `frp` menurun, lalu `acq_datetime_utc` menurun, lalu `detection_id` menaik. (Opsi lain: sampel acak, ditolak karena tidak dapat direproduksi.) `RECOMMENDATION` ⚑ KEP-05.
3. Histogram FRP memakai himpunan SEM-00 dan satuan MW. Deteksi `FRP_ZERO` ikut dihitung (SEM-09). FRP adalah ukuran per deteksi; **jumlah atau rata-rata FRP tidak disajikan sebagai "intensitas kebakaran" atau "energi kebakaran"** tanpa persetujuan baru. Batas bin: keputusan desain di D-P3.

### SEM-13 — Provenance dan versi

Dasar: FR-13, US-13.

- Setiap kejadian membawa: `source_id`, `processing_level` (SP/NRT), `version` (DQ-14), checksum file sumber, `boundary_version`, dan flag DQ. Kolom persisnya ditentukan A-P3-001, bukan di sini.
- Setiap angka dapat ditelusuri dari kejadian ke file sumber. Mengganti `boundary_version` atau mengganti NRT dengan SP mengubah angka dan harus tercatat di run log (jumlah baris berubah per `(satellite, tanggal UTC)`).

## 3. Keputusan yang butuh persetujuan (G2)

| ID | Keputusan | Rekomendasi agen | Alternatif utama | Pemilik keputusan |
|---|---|---|---|---|
| **KEP-01** (= HD-12) | Default confidence | Semua (`l`+`n`+`h`), filter menonjol (SEM-04) | `n`+`h`; `h` saja | Lanang (R1) + Abigail (R4) |
| **KEP-02** | OUTSIDE di total nasional | Tidak dihitung; total = jumlah 38 provinsi (SEM-02) | Dihitung di total | Tim |
| **KEP-03** | Filter tipe di rentang campuran SP+NRT | Nonaktifkan filter (SEM-05) | Terapkan ke SP saja; masker statis (Could) | Tim |
| **KEP-04** | Default satelit | NOAA-20 saja; gabungan opsional dengan peringatan (SEM-07) | Gabungan sebagai default | Lanang (R1) + Abigail (R4) |
| **KEP-05** | Ranking absolut; pemotongan titik peta deterministik (SEM-11, SEM-12) | Absolut; urut FRP menurun | Per luas (Could); sampel acak | Abigail (R4) + Lanang (R1) |

KEP-01 sampai KEP-05 belum tercatat di [12-human-decision-register.md](../../10-execution-plan/12-human-decision-register.md) selain HD-12. Pencatatan ID baru adalah tugas koordinator (X-P2-901). Agen ini tidak mengubah register itu.

Keputusan yang **sudah** final dan hanya dirujuk: OQ-08 (UTC + tanggal lokal), OQ-09 (simpan semua), OQ-11 (OUTSIDE), OQ-12 (field `type`), HD-09 (periode), HD-10 (presedensi SP/NRT), HD-11 (DQ-01…DQ-15, tanpa snapping, tipe dihitung semua).

## 4. Peta jejak angka dashboard → SEM

Kriteria penerimaan: setiap angka dapat dijelaskan oleh satu aturan. Semua baris di bawah adalah `count` SEM-00 dengan parameter berbeda; kolom kedua menyebut aturan yang **menentukan arti angkanya**.

| Angka/elemen dashboard (story) | Aturan penentu | Catatan |
|---|---|---|
| Total deteksi nasional (US-01) | SEM-00, SEM-02 | = jumlah 38 provinsi |
| Jumlah provinsi dengan deteksi (US-01) | SEM-00, SEM-02 | provinsi dengan `count` > 0 pada filter aktif |
| Titik timeline harian/bulanan (US-03) | SEM-03, SEM-08 | tanggal lokal; celah untuk hari tidak lengkap; penanda "sementara" (SEM-06) |
| Ranking provinsi (US-04) | SEM-11, SEM-02 | absolut; OUTSIDE keluar |
| Perbandingan dua periode (US-05) | SEM-10 | syarat kesetaraan |
| Filter confidence (US-06a) | SEM-04 | default semua |
| Filter satelit & jumlah gabungan (US-06b) | SEM-07 | default NOAA-20 |
| Histogram FRP (US-07) | SEM-12 | satuan MW |
| Pemilih provinsi (US-08) | SEM-03, SEM-02 | zona = zona provinsi |
| Titik peta + "terpotong" (US-02) | SEM-12 | deterministik |
| Filter tipe (opsional, ranking dan lainnya) | SEM-05 | hanya SP |
| Waktu data terakhir & basi (US-12) | SEM-08 | ambang: C-P2-001 |
| Jumlah diterima/ditolak/duplikat/OUTSIDE di monitoring (US-09) | DQ-01…DQ-15 dan SEM-02 | **bukan** `count` dashboard (hitungan baris run); dijelaskan di dokumen 06 |
| Label produk SP/NRT/campuran per tanggal (US-12, US-13) | SEM-06, SEM-13 | |

## 5. Masukan untuk tugas lain (bukan keputusan di sini)

| Penerima | Masukan |
|---|---|
| A-P3-001 (kontrak canonical event) | Kejadian wajib punya `region_status`, `province`, `local_date`, `zone`, `source_acq_date_utc`, `processing_level`, `boundary_version`, `type` nullable, flag DQ (SEM-00, SEM-03, SEM-13). |
| B-P2-001 (kueri) | Semua Q-xx baca dari himpunan SEM-00. Butuh dimensi: provinsi, `local_date`, satelit, confidence, `type` (nullable). Pra-agregasi harus identik dengan hitung dari detail (invarian SEM-00). Operasi ganti per `(satellite, tanggal UTC)` perlu akses per tanggal UTC walau partisi tampilan memakai tanggal lokal ([04 §4](../../01-dataset/04-nrt-vs-sp-and-latency.md#4-masukan-untuk-fase-berikutnya)). |
| D-P2-001/002 (FR/AC) | Default UI: confidence semua, satelit NOAA-20. Tanggal "sementara" dan "tidak lengkap" butuh AC khusus (SEM-06, SEM-08). Filter tipe nonaktif di rentang NRT (SEM-05). Perbandingan periode ditolak di kondisi SEM-10. |
| C-P2-001 (NFR) | Ambang kesegaran per satelit dari `acq_datetime` terbaru; batas titik peta; keduanya dipakai SEM-08 dan SEM-12. |

## 6. Verifikasi dan hal yang belum ada

| Item | Status |
|---|---|
| Konversi tanggal lokal (contoh §SEM-03) | Dihitung dengan perintah Python pada sesi ini; perintah dan output ditempel di deskripsi PR |
| Aritmetika contoh (selisih NRT–SP 965 = 0,80%; OUTSIDE ≤ 2 km = 2,76%) | Dihitung dari angka Fase 1 yang sudah ter-commit |
| Distribusi `l`/`n`/`h` pada data tim | `PENDING`: belum dijalankan. Dibutuhkan untuk KEP-01 |
| Perilaku NRT NOAA-20 vs SP | `UNKNOWN`: NRT NOAA-20 baru mulai 2026-08-01 |
| Jam lintasan NOAA-20 vs NOAA-21 (±50 menit) | `AI-PRIOR`: belum diukur |
| Pemetaan provinsi → zona | `AI-PRIOR`: cocokkan dengan atribut BIG pada A-P5-005 |
| Matriks jejak angka ↔ SEM (§4) | Selesai, perlu review manual oleh pemilik |
