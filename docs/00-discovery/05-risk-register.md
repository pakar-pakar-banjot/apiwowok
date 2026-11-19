# 05 — Register Risiko Teknis & Proyek

Status: **DIPERBARUI 2026-11-19** setelah jawaban tim. Ditinjau ulang di setiap gerbang fase.

Skala: Probabilitas (P) dan Dampak (D) masing-masing 1 (rendah) – 3 (tinggi). **Skor = P × D** (maks. 9). Skor ≥6 = prioritas tinggi.
Pemilik memakai kode peran dari charter §9 (R1–R4); nama anggota ditetapkan kemudian.

## Risiko prioritas tinggi (skor ≥ 6)

| ID | Risiko | P | D | Skor | Pemicu/indikator dini | Mitigasi | Kontingensi | Pemilik |
|---|---|---|---|---|---|---|---|---|
| R-01 | **Scope creep**: tim mencoba menyelesaikan 10 fitur, ditambah deployment cloud. | 3 | 3 | 9 | Fitur *Should/Could* dikerjakan sebelum semua *Must* berjalan end-to-end secara lokal. | Kunci MVP di gerbang Fase 2; setiap fitur baru butuh persetujuan tertulis. | Potong *Should* mulai D13 jika jalur kritis tertinggal. | R4 |
| R-02 | **Overhead proses/dokumentasi** (8 fase + gerbang) menghabiskan waktu implementasi. | 3 | 3 | 9 | Fase 0–3 belum selesai pada D5 (2026-11-23). | Time-box Fase 0–3 ±4 hari; dokumen ringkas; Fase 4 paralel; gerbang dapat disetujui asinkron. | Persetujuan bertahap per bagian. | R4 |
| R-03 | Struktur, format, atau kelengkapan data FIRMS **berbeda dari asumsi**. | 2 | 3 | 6 | Header/sampel file berbeda dari data dictionary awal. | Fase 1 memeriksa file nyata sebelum desain. | Sesuaikan requirement di gerbang Fase 1. | R1 |
| R-04 | **Akses data terhambat** (MAP_KEY terlambat, unduhan arsip lambat, kuota/rate limit API). | 2 | 3 | 6 | MAP_KEY/arsip belum diterima D2. | Daftar MAP_KEY D1; simpan file mentah di *raw zone* agar pipeline dapat diulang tanpa memanggil API lagi. | Jalur unduhan alternatif; kurangi periode. | R1 |
| R-06 | **Deduplikasi tidak deterministik** (koordinat float, NRT vs arsip, tidak ada ID unik). | 2 | 3 | 6 | Jumlah baris berbeda antar re-run. | Natural key eksplisit dengan aturan format terdokumentasi; test idempotensi otomatis. | Batasi MVP ke arsip saja. | R1 |
| R-09 | **Desain Cassandra bergaya relasional** (`ALLOW FILTERING`, full scan, tabel tanpa query). | 2 | 3 | 6 | Skema diusulkan sebelum access patterns disetujui. | Access patterns disetujui dulu; setiap tabel ↔ query terdokumentasi; review lintas agen. | Desain ulang tabel sebelum D8. | R2 |
| R-10 | **Agregat ganda** karena counter table/increment pada re-run. | 2 | 3 | 6 | Angka agregat berubah setelah ingest ulang. | Agregat = nilai absolut hasil hitung ulang per partisi; test idempotensi. | Rebuild agregat penuh dari tabel detail. | R2 |
| R-14 | **Integrasi terlambat**: frontend menunggu API, API menunggu skema. | 2 | 3 | 6 | Belum ada data nyata di Cassandra pada D10 (2026-11-28). | Kontrak API disepakati D5; frontend memakai mock; integrasi lokal pertama paling lambat D13 (2026-12-01). | Demo memakai subset data yang termuat. | R3 |
| R-15 | **Salah tafsir ilmiah** (hotspot disebut kebakaran; perbandingan tanpa metodologi). Risiko lebih besar karena aplikasi akan publik. | 2 | 3 | 6 | Label UI memakai kata "kebakaran"; grafik gabungan sensor. | Disclaimer wajib; review terminologi di Definition of Done. | Revisi teks sebelum deploy. | R4 |
| R-18 | **Ketersediaan anggota menurun** / *bus factor* 1. | 2 | 3 | 6 | Tugas melewati estimasi >2 hari tanpa kabar. | Reviewer kedua per area; standup asinkron; tugas ≤1 hari. | Realokasi tugas; potong *Should*. | R4 |
| R-23 | **Deployment cloud menyita waktu MVP** (provisioning, HTTPS, domain, secret, debugging lingkungan). | 2 | 3 | 6 | Pekerjaan cloud dimulai sebelum integrasi lokal berjalan; deploy pertama belum berhasil pada D17. | Deploy baru dikerjakan setelah integrasi lokal (≥D13); image container yang sama untuk lokal dan cloud; penyedia dipilih paling lambat D12; time-box 2–3 hari. | Demo lokal tetap menjadi jalur utama; deployment cloud disederhanakan (single VM, single node). | R3 |
| R-25 | **Keamanan aplikasi publik**: port Cassandra terekspos, MAP_KEY bocor dari server, penyalahgunaan API. | 2 | 3 | 6 | Port database terbuka di firewall; secret ada di image atau repo. | Cassandra hanya di jaringan privat; secret lewat environment/secret store; API read-only; HTTPS; CORS terbatas (OQ-26). Perubahan keamanan butuh persetujuan manusia. | Matikan akses publik sampai diperbaiki. | R3 |

## Risiko prioritas sedang/rendah (skor ≤ 4)

| ID | Risiko | P | D | Skor | Mitigasi | Pemilik |
|---|---|---|---|---|---|---|
| R-05 | Volume data besar → partisi terlalu besar, respons peta lambat. | 2 | 2 | 4 | Ukur volume di Fase 1; batas jumlah titik per respons; evaluasi ukuran partisi di Fase 3. | R2 |
| R-07 | Kesalahan zona waktu (UTC vs lokal) → agregasi harian salah. | 2 | 2 | 4 | Aturan tertulis (OQ-08); test unit untuk deteksi malam lintas tanggal. | R1 |
| R-08 | Batas provinsi usang (34 vs 38) atau lisensi tidak jelas untuk publikasi. | 2 | 2 | 4 | Evaluasi sumber di Fase 1; catat versi; satu versi tetap. | R1 |
| R-11 | Lingkungan multi-node untuk eksperimen replikasi tidak tersedia (laptop di bawah spesifikasi minimum atau cloud terlalu mahal). | 2 | 2 | 4 | Spesifikasi minimum + smoke test ([07](07-three-node-laptop-spec.md)); heap dan CPU dibatasi per node; node dinyalakan berurutan; cloud berumur pendek sebagai alternatif. | R2 |
| R-12 | Lingkungan pengembangan heterogen (versi Python vs kompatibilitas driver Cassandra, instalasi GeoPandas). | 2 | 2 | 4 | Kunci versi di Fase 4; jalankan pipeline di container. | R3 |
| R-13 | Konflik/inkonsistensi kode dari dua agen AI; kode yang tidak dipahami tim. | 2 | 2 | 4 | AGENTS.md; satu implementer per tugas; branch per tugas; review manusia sebelum merge. | R3 |
| R-16 | Benchmark tidak valid/tidak dapat direproduksi (noise mesin, cache, perbedaan lokal vs cloud). | 2 | 2 | 4 | Protokol eksperimen: variabel terkendali, warm-up, repetisi, catat hardware dan versi; lingkungan eksperimen dicatat eksplisit. | R2 |
| R-17 | Kebocoran secret (MAP_KEY) ke repo. | 2 | 2 | 4 | `.env` di `.gitignore` sejak harness; `.env.example` berisi placeholder; repo privat. | R3 |
| R-21 | Celah data satelit mengganggu timeline dan perbandingan historis. | 2 | 2 | 4 | Profil kelengkapan harian di Fase 1; UI membedakan "tidak ada data" dari "nol deteksi". | R1 |
| R-24 | Biaya cloud melebihi anggaran / kredit habis; VM kecil tidak cukup memori untuk Cassandra. | 2 | 2 | 4 | Pilih ukuran minimum yang layak setelah volume diketahui; matikan resource yang tidak dipakai; pasang peringatan anggaran bila tersedia. | R3 |
| R-26 | Anggota tanpa Docker Compose tidak dapat menguji integrasi → bug integrasi baru muncul terlambat. | 2 | 2 | 4 | Mock API berbasis kontrak; backend dev bersama setelah deploy awal (OQ-27); R3 menjalankan test integrasi rutin. | R3 |
| R-19 | ~~Rubrik tidak diketahui.~~ → **Tanpa rubrik tertulis, ekspektasi penilaian bersifat implisit.** | 1 | 3 | 3 | Brief proyek dan dokumen ini dipakai sebagai acuan ruang lingkup; prioritas: produk jadi + implementasi teknis (OQ-01). | R4 |
| R-20 | Layanan FIRMS tidak tersedia atau berubah selama proyek. | 1 | 2 | 2 | Raw zone; pipeline membaca dari file tersimpan. | R1 |
| R-22 | Basemap tile publik membatasi penggunaan untuk aplikasi yang di-hosting. | 1 | 2 | 2 | Atribusi; cek kebijakan; siapkan penyedia alternatif. | R4 |

## Riwayat perubahan

| Tanggal | Perubahan |
|---|---|
| 2026-11-19 | Versi awal. |
| 2026-11-19 | Setelah jawaban tim: R-19 turun dari 6 ke 3 (tidak ada rubrik; acuan jelas dari tim). R-11 dirumuskan ulang (hardware laptop tidak relevan; multi-node di cloud). R-22 dampak naik ke 2 (aplikasi di-hosting). Ditambahkan R-23, R-24, R-25, R-26 (deployment cloud dan alur kerja tanpa Docker). |
| 2026-11-19 | R-11: eksperimen 3 node boleh di laptop; mitigasi mengacu ke dokumen 07. R-04: verifikasi halaman FIRMS menunjukkan Country API tidak tersedia dan `DAY_RANGE` maks. 5 hari. Ekstraksi historis membutuhkan banyak request per bounding box, tetapi masih jauh di bawah batas 5000 transaksi/10 menit; probabilitas tidak diubah sampai uji unduhan di Fase 1. |

## Catatan

- `AI-PRIOR` yang mendasari R-03, R-04, R-06, R-07, R-21 harus diverifikasi di Fase 1.
