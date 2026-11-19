# 06 — Tindakan Berikutnya & Gerbang Persetujuan

Status: **DIPERBARUI 2026-11-19** setelah jawaban tim. Kode peran (R1–R4) mengacu pada charter §9.

## 1. Tindakan segera (D1, sebelum Fase 1)

| ID | Tindakan | Pemilik | Keluaran | Terkait | Status |
|---|---|---|---|---|---|
| NA-01 | Mendaftar **MAP_KEY NASA FIRMS** (dan akun lain yang dibutuhkan untuk unduhan arsip). Simpan hanya di catatan pribadi/`.env` lokal — **jangan** ditulis di repo, chat publik, atau dokumen. | R1 | MAP_KEY aktif | R-04, R-17 | **Menunggu konfirmasi** |
| NA-02 | ~~Meminta rubrik penilaian.~~ Tidak ada rubrik (OQ-01). | — | — | OQ-01 | Selesai / tidak berlaku |
| NA-03 | Tinjau dokumen Fase 0 dan jawab open questions. | Semua | Kolom *Keputusan* terisi | OQ-01–OQ-22 | **Selesai** (2026-11-19) |
| NA-04 | ~~Survei hardware anggota.~~ Tidak relevan (OQ-15). | — | — | OQ-15 | Dibatalkan |
| NA-05 | Atur repo GitHub menjadi **privat** selama pengembangan (OQ-16). | Semua | Pengaturan repo | OQ-16, R-17 | Menunggu |
| NA-06 | Sepakati kanal komunikasi & ritme: standup asinkron harian (kemarin/hari ini/hambatan), review gerbang secara asinkron. | R4 | Aturan komunikasi | R-02, R-18 | Menunggu |
| NA-07 | *(baru)* Inventaris opsi cloud yang tersedia bagi tim (kredit mahasiswa, akun yang sudah ada, batas anggaran). **Tidak mendesak**, dibutuhkan paling lambat D12 (2026-11-30). | R3 | Daftar opsi + anggaran | OQ-23, R-24 | Menunggu |

## 1a. Panduan NA-01 — Mendapatkan MAP_KEY NASA FIRMS

Sumber: halaman resmi FIRMS API (dibaca 2026-11-19). Tampilan halaman dapat berubah sewaktu-waktu.

1. Buka **https://firms.modaps.eosdis.nasa.gov/api/map_key/**
2. Klik tombol **"Get MAP_KEY"**. Sebuah dialog berjudul *"FIRMS WMS Map Key"* akan muncul.
3. Masukkan **alamat email** dan isi field lain yang diminta dialog, lalu kirim. Halaman ini hanya menyebut email; tidak ada keterangan bahwa akun NASA Earthdata dibutuhkan.
4. Buka inbox email tersebut (cek juga folder **Spam/Promosi**). MAP_KEY **dikirim lewat email**, bukan ditampilkan di layar.
5. **Simpan MAP_KEY secara aman**, misalnya di password manager. Jangan menaruhnya di repo, dokumen, grup chat, atau percakapan dengan agen AI. Setelah harness Fase 4 tersedia, MAP_KEY diletakkan di `.env` lokal sebagai `FIRMS_MAP_KEY=...` (file `.env` diabaikan Git).
6. **Uji MAP_KEY.** Buka URL berikut di browser, ganti `<MAP_KEY>` dengan key Anda:
   `https://firms.modaps.eosdis.nasa.gov/api/data_availability/csv/<MAP_KEY>/VIIRS_SNPP_SP`
   Jika key valid, browser menampilkan/mengunduh CSV berisi rentang tanggal data yang tersedia. Jangan membagikan URL ini karena memuat key.
7. **Cek sisa kuota** lewat kontrol **"Check status"** di halaman MAP_KEY (langkah 1). Batas resmi: **5000 transaksi per 10 menit**; request dengan rentang hari lebih besar dapat dihitung sebagai beberapa transaksi.
8. Jika muncul pesan *"Email is already registered"*, kirim ulang/ubah key dengan login melalui **https://firms.modaps.eosdis.nasa.gov/download/** sesuai petunjuk pesan tersebut.

Rekomendasi pembagian key (`RECOMMENDATION`): setiap anggota yang menjalankan ingestion memakai key miliknya sendiri, ditambah satu key terpisah untuk server cloud. Kuota tidak saling berebut, dan key yang bocor dapat diganti tanpa mengganggu anggota lain.

## 2. Persiapan Fase 1 (dapat dimulai setelah gerbang G0)

Fase 1 hanya menginspeksi dan memprofil data. **Belum** ada kode aplikasi, skema, atau pipeline produksi.

| ID | Tugas Fase 1 (usulan) | Pemilik | Keluaran |
|---|---|---|---|
| P1-01 | Inventaris sumber: produk, format, jalur unduhan, batas akses, lisensi/atribusi FIRMS. | R1 | Source inventory |
| P1-02 | Unduh sampel nyata untuk kandidat produk (OQ-04) & periode (OQ-05) ke folder data mentah lokal yang **tidak** di-commit. | R1 | File mentah + checksum |
| P1-03 | Data dictionary dari header & nilai nyata (bukan dari ingatan), termasuk perbedaan antar produk. | R1 | Data dictionary |
| P1-04 | Profiling: jumlah baris, null, nilai di luar rentang, duplikat (dengan beberapa kandidat natural key), cakupan temporal & geografis, kelengkapan harian. | R1 + R2 | Laporan profil |
| P1-05 | Verifikasi `AI-PRIOR` kritis: zona waktu `acq_time`, format confidence, field `version`, field `type`, perbandingan NRT vs arsip pada tanggal yang sama. | R1 | Tabel verifikasi A-05–A-09 |
| P1-06 | Evaluasi sumber batas provinsi (jumlah provinsi, lisensi termasuk untuk aplikasi publik, ukuran, CRS). | R1 | Rekomendasi sumber batas |
| P1-07 | Estimasi volume per provinsi per hari/bulan untuk masukan desain partisi di Fase 3 (hanya angka hasil ukur). | R2 | Tabel volume |
| P1-08 | Draf requirements awal (Fase 2) dapat dimulai paralel, berdasarkan MVP charter. | R4 | Draf FR/NFR |

Catatan tooling: skrip profiling sekali pakai boleh dibuat di Fase 1 (di folder `notebooks/` atau `scratch/` yang disepakati), tetapi dependensi proyek dan struktur repo resmi baru ditetapkan di Fase 4.

## 3. Hal yang sengaja BELUM dilakukan

- Tidak ada kode aplikasi, skema Cassandra, `docker-compose.yml`, atau instalasi dependensi.
- Tidak ada keputusan final atas produk, periode, zona waktu, atau kebijakan kualitas data.
- Tidak ada pekerjaan deployment cloud; hanya pertanyaan terbuka OQ-23–OQ-27 yang dicatat.
- Tidak ada push ke remote. Dokumen Fase 0 di-commit di branch `docs/phase-0-discovery`, sesuai permintaan tim.

## 4. Gerbang persetujuan G0 (checklist)

Fase 1 dimulai hanya setelah semua butir berikut dicentang:

- [x] Piagam proyek (01) disetujui — melalui penerimaan default/rekomendasi oleh tim (2026-11-19), dengan revisi: hosting cloud ditambahkan, laporan/presentasi/video di luar tugas agen.
- [x] Pemetaan MoSCoW disetujui (default), ditambah fitur #11 hosting cloud.
- [x] Peran: dokumen memakai R1–R4; nama ditetapkan kemudian (OQ-03, keputusan tim).
- [x] Waktu: sisa 21 hari; kalender kerja D1 = 2026-11-19 s.d. D21 = 2026-12-09 (A-22, mohon koreksi bila berbeda).
- [x] Rubrik: tidak ada; Cassandra wajib (OQ-01).
- [x] Jawaban sementara: kandidat produk (OQ-04), kandidat periode (OQ-05), cakupan geografis (OQ-06).
- [ ] **MAP_KEY FIRMS sudah diminta (NA-01).** Satu-satunya butir yang belum terkonfirmasi.

**Format persetujuan yang disarankan:** balas "G0 disetujui" + status MAP_KEY. Jika MAP_KEY belum ada, Fase 1 tetap dapat dimulai dengan inventaris sumber dan unduhan yang tidak memerlukan MAP_KEY (bila ada), tetapi bagian yang memakai API ditunda.
