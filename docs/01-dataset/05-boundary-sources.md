# 05 — Evaluasi Sumber Batas Provinsi (P1-06, OQ-07)

> Fase 1 · Diperiksa 2026-11-19 · Label sesuai [legenda](../00-discovery/README.md#label-status-informasi)

## 1. Kebutuhan

Dari keputusan Fase 0 (OQ-06, OQ-07, A-11, A-20):

- **38 provinsi** (pemekaran Papua 2022: Papua Selatan, Papua Tengah, Papua Pegunungan, Papua Barat Daya).
- Satu versi tetap untuk seluruh periode historis.
- Lisensi jelas, termasuk untuk aplikasi yang di-hosting publik.
- Ukuran wajar untuk point-in-polygon dan tampilan peta. CRS diketahui.
- Kabupaten/kota = *Could*, jadi sumber yang juga memuat kabupaten adalah nilai tambah.

## 2. Kandidat dan hasil pemeriksaan

| # | Kandidat | Jumlah provinsi | Edisi / tahun | Lisensi | Format & ukuran | CRS | Status |
|---|---|---|---|---|---|---|---|
| B1 | **BIG** — layanan `BATASWILAYAH/BATAS_KABKOTA_AR` (ArcGIS MapServer, `geoservices.big.go.id`) | **38** (`KDPPUM` 11…96, dihitung dari data) | "Geodatabase data batas wilayah administrasi nasional **edisi Juni 2026**" (deskripsi layanan). Field `METADATA` per fitur bertanggal 2022-12-27 s.d. 2026-06-12. | **`UNKNOWN`.** Katalog data.go.id (`batas_kecamatan_ar_2026`, BIG) berisi `license_title: null`. `copyrightText` layanan `BATAS_WILAYAH`: "Badan Informasi Geospasial". | Query REST, `maxRecordCount` 1000, mendukung `geoJSON`. 541 fitur kab/kota. Unduhan tergeneralisasi (`maxAllowableOffset=0.001°`): **10.004.146 byte (±10 MB)** GeoJSON, 23.063 bagian poligon, 368.435 vertex. | EPSG:4326 | `VERIFIED` (diunduh & dihitung) |
| B2 | **geoBoundaries** gbOpen IDN ADM1 | **34** (`admUnitCount`) | `boundaryYearRepresented` 2017; sumber OpenStreetMap/Wambacher | ODbL 1.0 | GeoJSON/TopoJSON + versi simplified | EPSG:4326 | `VERIFIED` (API geoBoundaries) |
| B3 | **HDX COD-AB Indonesia** (`cod-ab-idn`, OCHA/BPS) | **34** ("Admin 1: 34 province") | Batas dibuat 2020-04-08; ditinjau 2025-10-30 | CC BY-IGO | SHP 498 MB, GeoJSON 456 MB, GDB 219 MB (zip) | — | `VERIFIED` (API HDX) |
| B4 | **GADM** | `UNKNOWN` (sumber sekunder menyebut GADM 4.1 masih 34) | 4.1 | Hanya untuk akademik/non-komersial; **redistribusi tidak diizinkan** tanpa izin (gadm.org/license) | — | — | Lisensi `VERIFIED` lewat ringkasan pencarian; jumlah provinsi tidak diverifikasi |
| B5 | Repo GitHub komunitas berisi "38 provinsi" (GeoJSON/TopoJSON) | Diklaim 38 | Bervariasi | Asal-usul data dan lisensinya tidak jelas (sebagian turunan GADM) | — | — | Tidak dievaluasi lebih lanjut |

Fakta tambahan B1, diukur dari data yang diunduh:

- Field yang tersedia: `NAMOBJ`, `KDPPUM` (kode provinsi), `WADMPR` (nama provinsi), `KDPKAB` (kode kab/kota), `WADMKK` (nama kab/kota), `TIPADM`, `LUASWH`, `METADATA`, dan kode BPS/PUM lain.
- Nilai `TIPADM` yang ditemukan: 4 (422 fitur, mis. "Aceh Barat"), 5 (98 fitur, mis. "Kota Denpasar"), dan 6 (21 fitur). Fitur `TIPADM` 6 punya nama provinsi tetapi `KDPKAB` kosong. Fitur ini berupa area tingkat provinsi tanpa kab/kota: sebagian besar pulau kecil < 2 km², ditambah satu area 3.197 km² di Kalimantan Timur. Arti resmi kode `TIPADM` adalah `UNKNOWN`, karena tidak ada dokumentasi yang terbaca. Kode 4, 5, dan 6 di atas hanya pengamatan, dan untuk penetapan provinsi hal ini tidak berpengaruh.
- Beberapa `KDPKAB` muncul lebih dari sekali (74.02–74.13, Sulawesi Tenggara). Satu kab/kota bisa terdiri dari beberapa fitur, sehingga agregasi kabupaten harus memakai kode, bukan jumlah fitur.
- Extent layanan: 94,972–141,020 BT, −11,008–6,077 LU. Angka ini cocok dengan bounding box ekstraksi FIRMS (`94,-11.5,141.5,6.5`).
- Ada juga layanan lama `BATAS_WILAYAH/MapServer/12` (539 fitur, juga 38 provinsi, `METADATA` 2022–2024). Layanan ini **tidak** dipakai karena edisinya lebih tua.

## 3. Uji pakai pada data FIRMS

Penetapan provinsi diuji dengan point-in-polygon (numpy, ray casting) terhadap B1 tergeneralisasi:

- Seluruh koordinat unik hasil unduhan Fase 1 diproses dalam hitungan detik. Angka akhirnya ada di [03-profiling-report.md](03-profiling-report.md).
- Uji acak: titik di Kupang/Belu → NTT, Indramayu → Jawa Barat, Tanjung Jabung Barat → Jambi. Titik di Timor-Leste, Australia utara, dan Malaysia → di luar.
- Hanya 15 dari ±300 ribu koordinat (uji awal) yang jatuh di dua poligon sekaligus, akibat generalisasi tepi. Aturannya: ambil poligon pertama, lalu laporkan jumlahnya.
- Titik yang tidak masuk poligon mana pun dihitung jaraknya ke tepi poligon terdekat. Distribusinya dipakai untuk aturan kualitas DQ-07 (lihat [06-data-quality-rules.md](06-data-quality-rules.md)).

## 4. Analisis

- **Hanya B1 yang terverifikasi memuat 38 provinsi.** Kandidat terbuka berlisensi jelas (B2, B3) masih 34 provinsi. Akibatnya, wilayah enam provinsi Papua saat ini akan tergabung menjadi dua provinsi lama, sehingga ranking provinsi dan agregasi di Papua (salah satu wilayah dengan deteksi terbanyak) menjadi salah.
- B1 juga memuat kab/kota, jadi fitur kabupaten (*Could*) bisa dikerjakan tanpa sumber baru.
- **Risiko B1 ada di lisensi.** BIG adalah penyelenggara Informasi Geospasial Dasar resmi (Perpres 11/2021), dan layanannya publik tanpa login. Namun tidak ada pernyataan lisensi eksplisit yang terbaca untuk layanan ini. Peraturan BIG 8/2021 menyebut bahwa sebagian produk IG mensyaratkan pernyataan penggunaan. Apakah syarat itu berlaku untuk layanan ini masih `UNKNOWN`.
- Generalisasi 0,001° (±110 m) jauh lebih kecil dari ukuran piksel VIIRS (375 m di nadir). Dampaknya terhadap penetapan provinsi diukur di laporan profil (jumlah titik dekat pantai/perbatasan).

## 5. Rekomendasi (`RECOMMENDATION`, perlu persetujuan di G1)

1. **Pakai B1 (BIG, edisi Juni 2026)** sebagai satu-satunya versi batas provinsi untuk seluruh periode (sesuai A-20). Simpan snapshot GeoJSON tergeneralisasi beserta checksum-nya (SHA-256 gabungan 22 bagian: `0382eeee…f3e478`) agar hasil bisa direproduksi. Snapshot ini tidak bergantung pada ketersediaan server BIG saat aplikasi berjalan.
2. **Atribusi wajib di aplikasi dan README:** "Batas wilayah: Badan Informasi Geospasial (BIG), Batas Wilayah Administrasi edisi Juni 2026".
3. **Tindakan tim sebelum hosting publik (NA baru):** konfirmasi syarat penggunaan ke BIG atau lewat halaman kebijakan tanahair.indonesia.go.id. Sampai ada konfirmasi, statusnya `ASSUMPTION`: penggunaan akademik non-komersial dengan atribusi diperbolehkan.
4. **Cadangan bila lisensi B1 ternyata tidak memadai:** B3 (HDX, CC BY-IGO, 34 provinsi), dengan keterbatasan Papua dinyatakan eksplisit di UI dan dokumentasi.

## 6. Sumber

- Direktori layanan BIG: `https://geoservices.big.go.id/rbi/rest/services/BATASWILAYAH?f=json`; layer `BATAS_KABKOTA_AR/MapServer/0`, diakses 2026-11-19.
- Katalog data.go.id, dataset BIG `batas_kecamatan_ar_2026` ("Edisi Juni 2026"), diakses 2026-11-19.
- geoBoundaries API: `https://www.geoboundaries.org/api/current/gbOpen/IDN/ADM1/`.
- HDX CKAN API: `https://data.humdata.org/api/3/action/package_show?id=cod-ab-idn`.
- GADM license: `https://gadm.org/license.html`.
- Perpres 11/2021; Peraturan BIG 8/2021 (lewat hasil pencarian di peraturan.go.id / peraturan.bpk.go.id).
