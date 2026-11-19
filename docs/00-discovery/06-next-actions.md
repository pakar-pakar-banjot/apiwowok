# 06 — Tindakan Berikutnya & Gerbang Persetujuan

Status: **DRAFT**. Kode peran (R1–R4) mengacu pada charter §9.

## 1. Tindakan segera (D1, sebelum Fase 1)

| ID | Tindakan | Pemilik | Keluaran | Terkait |
|---|---|---|---|---|
| NA-01 | Mendaftar **MAP_KEY NASA FIRMS** (dan akun lain yang dibutuhkan untuk unduhan arsip). Simpan hanya di catatan pribadi/`.env` lokal — **jangan** ditulis di repo, chat publik, atau dokumen. | R1 | MAP_KEY aktif | R-04, R-17 |
| NA-02 | Meminta **rubrik penilaian** dan jadwal (presentasi, pengumpulan) dari dosen/asisten. | R4 | Rubrik tertulis | OQ-01, OQ-02 |
| NA-03 | Rapat tim 30–45 menit: tinjau dokumen Fase 0, tetapkan peran, isi tanggal nyata, jawab OQ-03–OQ-06 (sementara). | Semua | Kolom *Keputusan* terisi | OQ-03–OQ-06 |
| NA-04 | **Survei hardware** tiap anggota: OS, RAM, CPU, Docker terpasang atau belum. | R3 | Tabel hardware | OQ-15, R-11, R-12 |
| NA-05 | Tentukan visibilitas repo GitHub (rekomendasi: privat selama pengembangan). | Semua | Pengaturan repo | OQ-16 |
| NA-06 | Sepakati kanal komunikasi & ritme: standup asinkron harian (kemarin/hari ini/hambatan), review gerbang secara asinkron. | R4 | Aturan komunikasi | R-02, R-18 |

## 2. Persiapan Fase 1 (dapat dimulai setelah gerbang G0)

Fase 1 hanya menginspeksi dan memprofil data. **Belum** ada kode aplikasi, skema, atau pipeline produksi.

| ID | Tugas Fase 1 (usulan) | Pemilik | Keluaran |
|---|---|---|---|
| P1-01 | Inventaris sumber: produk, format, jalur unduhan, batas akses, lisensi/atribusi FIRMS. | R1 | Source inventory |
| P1-02 | Unduh sampel nyata untuk kandidat produk (OQ-04) & periode (OQ-05) ke folder data mentah lokal yang **tidak** di-commit. | R1 | File mentah + checksum |
| P1-03 | Data dictionary dari header & nilai nyata (bukan dari ingatan), termasuk perbedaan antar produk. | R1 | Data dictionary |
| P1-04 | Profiling: jumlah baris, null, nilai di luar rentang, duplikat (dengan beberapa kandidat natural key), cakupan temporal & geografis, kelengkapan harian. | R1 + R2 | Laporan profil |
| P1-05 | Verifikasi `AI-PRIOR` kritis: zona waktu `acq_time`, format confidence, field `version`, field `type`, perbandingan NRT vs arsip pada tanggal yang sama. | R1 | Tabel verifikasi A-05–A-09 |
| P1-06 | Evaluasi sumber batas provinsi (jumlah provinsi, lisensi, ukuran, CRS). | R1 | Rekomendasi sumber batas |
| P1-07 | Estimasi volume per provinsi per hari/bulan untuk masukan desain partisi di Fase 3 (hanya angka hasil ukur). | R2 | Tabel volume |
| P1-08 | Draf requirements awal (Fase 2) dapat dimulai paralel, berdasarkan MVP charter. | R4 | Draf FR/NFR |

Catatan tooling: skrip profiling sekali pakai boleh dibuat di Fase 1 (di folder `notebooks/` atau `scratch/` yang disepakati), tetapi dependensi proyek dan struktur repo resmi baru ditetapkan di Fase 4.

## 3. Hal yang sengaja BELUM dilakukan

- Tidak ada kode aplikasi, skema Cassandra, `docker-compose.yml`, atau instalasi dependensi.
- Tidak ada keputusan final atas produk, periode, zona waktu, atau kebijakan kualitas data.
- Tidak ada commit atau push. File Fase 0 berada di working tree untuk ditinjau tim; commit dilakukan setelah tim setuju.

## 4. Gerbang persetujuan G0 (checklist)

Fase 1 dimulai hanya setelah semua butir berikut dicentang:

- [ ] Piagam proyek (01) disetujui atau direvisi — termasuk problem statement, disclaimer ilmiah, dan MVP.
- [ ] Pemetaan MoSCoW 10 fitur disetujui (boleh dengan perubahan).
- [ ] Peran R1–R4 ditetapkan dengan nama anggota (OQ-03).
- [ ] Tanggal D1 dan deadline nyata diisi (OQ-02).
- [ ] Rubrik diminta (OQ-01) — boleh masih ditunggu, tetapi statusnya dicatat.
- [ ] Jawaban sementara: kandidat produk (OQ-04), kandidat periode (OQ-05), cakupan geografis (OQ-06).
- [ ] MAP_KEY FIRMS sudah diminta (NA-01).

**Format persetujuan yang disarankan:** balas dengan "G0 disetujui" disertai keputusan/revisi per butir, atau daftar perubahan yang diminta.
