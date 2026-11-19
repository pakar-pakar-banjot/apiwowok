# 05 — Register Risiko Teknis & Proyek

Status: **DRAFT**. Ditinjau ulang di setiap gerbang fase.

Skala: Probabilitas (P) dan Dampak (D) masing-masing 1 (rendah) – 3 (tinggi). **Skor = P × D** (maks. 9). Skor ≥6 = prioritas tinggi.
Pemilik memakai kode peran dari charter §9 (R1–R4) karena nama anggota `UNKNOWN`.

## Risiko prioritas tinggi (skor ≥ 6)

| ID | Risiko | P | D | Skor | Pemicu/indikator dini | Mitigasi | Kontingensi | Pemilik |
|---|---|---|---|---|---|---|---|---|
| R-01 | **Scope creep**: tim mencoba menyelesaikan 10 fitur. | 3 | 3 | 9 | Fitur *Should/Could* dikerjakan sebelum semua *Must* berjalan end-to-end. | Kunci MVP di gerbang Fase 2; setiap fitur baru butuh persetujuan tertulis. | Potong *Should* mulai D13 jika jalur kritis tertinggal. | R4 |
| R-02 | **Overhead proses/dokumentasi** (8 fase + gerbang) menghabiskan waktu implementasi. | 3 | 3 | 9 | Fase 0–3 belum selesai pada D5. | Time-box Fase 0–3 ±4 hari; dokumen ringkas; Fase 4 paralel; gerbang dapat disetujui secara asinkron (chat tim). | Persetujuan bertahap per bagian, bukan per dokumen utuh. | R4 |
| R-19 | **Rubrik mata kuliah tidak diketahui** → tim mengirim hal yang salah. | 2 | 3 | 6 | Rubrik belum diterima pada D2. | Minta rubrik D1 (OQ-01). | Prioritaskan komponen yang disebut eksplisit dalam brief (pipeline, Cassandra, eksperimen). | R4 |
| R-03 | Struktur, format, atau kelengkapan data FIRMS **berbeda dari asumsi**. | 2 | 3 | 6 | Header/sampel file berbeda dari data dictionary awal. | Fase 1 memeriksa file nyata sebelum desain; data dictionary dari data, bukan dari ingatan. | Sesuaikan requirement di gerbang Fase 1. | R1 |
| R-04 | **Akses data terhambat** (MAP_KEY terlambat, unduhan arsip lambat, kuota/rate limit API). | 2 | 3 | 6 | MAP_KEY/arsip belum diterima D2. | Daftar MAP_KEY D1; simpan semua file mentah di *raw zone* lokal agar pipeline dapat diulang tanpa memanggil API lagi. | Jalur unduhan alternatif (CSV per negara/arsip); kurangi periode. | R1 |
| R-06 | **Deduplikasi tidak deterministik** (koordinat float, NRT vs arsip, tidak ada ID unik). | 2 | 3 | 6 | Jumlah baris berbeda antar re-run; duplikat terdeteksi di Fase 1. | Natural key eksplisit dengan aturan pembulatan/format terdokumentasi; test idempotensi otomatis. | Batasi MVP ke arsip saja (tanpa NRT). | R1 |
| R-09 | **Desain Cassandra bergaya relasional** (JOIN mental, `ALLOW FILTERING`, full scan, tabel tanpa query). | 2 | 3 | 6 | Skema diusulkan sebelum access patterns disetujui. | Access patterns disetujui dulu; setiap tabel ↔ query terdokumentasi; review lintas agen. | Desain ulang tabel sebelum D8 (setelahnya mahal). | R2 |
| R-10 | **Agregat ganda** karena counter table/increment pada re-run. | 2 | 3 | 6 | Angka agregat berubah setelah ingest ulang. | Agregat = nilai absolut hasil hitung ulang per partisi; test idempotensi. | Rebuild agregat penuh dari tabel detail. | R2 |
| R-14 | **Integrasi terlambat**: frontend menunggu API, API menunggu skema. | 2 | 3 | 6 | Belum ada data nyata di Cassandra pada D10. | Kontrak API disepakati D5; frontend memakai mock; integrasi pertama paling lambat D13. | Demo memakai subset data kecil yang termuat. | R3 |
| R-15 | **Salah tafsir ilmiah** (hotspot disebut kebakaran; perbandingan antar sensor/periode tanpa metodologi). | 2 | 3 | 6 | Label UI/laporan memakai kata "kebakaran"; grafik gabungan sensor. | Disclaimer wajib (charter §3); review terminologi di Definition of Done; perbandingan hanya produk sama. | Revisi teks sebelum presentasi. | R4 |
| R-18 | **Ketersediaan anggota menurun** (ujian, sakit, tugas lain) / *bus factor* 1. | 2 | 3 | 6 | Tugas melewati estimasi >2 hari tanpa kabar. | Reviewer kedua per area; standup asinkron harian; tugas kecil (≤1 hari). | Realokasi tugas; potong *Should*. | R4 |

## Risiko prioritas sedang/rendah (skor ≤ 4)

| ID | Risiko | P | D | Skor | Mitigasi | Pemilik |
|---|---|---|---|---|---|---|
| R-05 | Volume data besar → partisi terlalu besar, respons peta lambat. | 2 | 2 | 4 | Ukur volume di Fase 1; batas jumlah titik per respons; evaluasi ukuran partisi di Fase 3. | R2 |
| R-07 | Kesalahan zona waktu (UTC vs lokal) → agregasi harian salah. | 2 | 2 | 4 | Aturan tertulis (OQ-08); test unit untuk kasus deteksi malam lintas tanggal. | R1 |
| R-08 | Batas provinsi usang (34 vs 38) atau lisensi tidak jelas. | 2 | 2 | 4 | Evaluasi sumber di Fase 1; catat versi; satu versi tetap. | R1 |
| R-11 | Hardware tidak mampu menjalankan cluster Cassandra 3 node. | 2 | 2 | 4 | Survei hardware; batasi heap per node untuk eksperimen; jalankan di mesin terbesar. | R2 |
| R-12 | Lingkungan pengembangan heterogen (Windows/WSL2/Docker Desktop, versi Python vs kompatibilitas driver Cassandra, instalasi GeoPandas). | 2 | 2 | 4 | Kunci versi Python & dependensi di Fase 4; jalankan ETL di container; uji setup di ≥2 laptop. | R3 |
| R-13 | Konflik/inkonsistensi kode dari dua agen AI; kode yang tidak dipahami tim. | 2 | 2 | 4 | AGENTS.md sebagai aturan bersama; satu implementer per tugas; branch per tugas; review manusia sebelum merge. | R3 |
| R-16 | Benchmark tidak valid/tidak dapat direproduksi (noise laptop, cache, data berbeda). | 2 | 2 | 4 | Protokol eksperimen: variabel terkendali, warm-up, repetisi, catat hardware & versi; tidak ada angka tanpa log mentah. | R2 |
| R-17 | Kebocoran secret (MAP_KEY) ke repo. | 2 | 2 | 4 | `.env` di `.gitignore` sejak commit pertama harness; `.env.example` berisi placeholder; repo privat (OQ-16). | R3 |
| R-21 | Celah data satelit (gangguan sensor/satelit) mengganggu timeline & perbandingan historis. | 2 | 2 | 4 | Profil kelengkapan harian di Fase 1; tandai hari tanpa data di UI ("tidak ada data" ≠ "nol deteksi"). | R1 |
| R-20 | Layanan FIRMS tidak tersedia atau berubah selama proyek. | 1 | 2 | 2 | Raw zone lokal; pipeline membaca dari file tersimpan. | R1 |
| R-22 | Basemap tile publik membatasi penggunaan. | 1 | 1 | 1 | Atribusi; volume demo rendah; penyedia alternatif. | R4 |

## Catatan

- `AI-PRIOR` yang mendasari R-03, R-04, R-06, R-07, R-21 harus diverifikasi di Fase 1. Probabilitas dapat turun/naik setelahnya.
- Risiko yang skornya berubah dicatat di tabel ini beserta tanggal perubahannya.
