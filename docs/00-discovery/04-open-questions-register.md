# 04 — Register Pertanyaan Terbuka & Keputusan Tertunda

Status: **DIPERBARUI 2026-11-19** setelah jawaban tim. Tim menyatakan: *pertanyaan yang tidak dijawab secara eksplisit memakai jawaban default/rekomendasi.*

Prioritas: **P0** = memblokir Fase 1 · **P1** = dibutuhkan sebelum Fase 2/3 · **P2** = dapat diputuskan kemudian.

Status keputusan:
- `DECIDED (USER)`: dijawab eksplisit oleh tim.
- `DECIDED (DEFAULT)`: tim menerima rekomendasi AI.
- `PROVISIONAL`: jawaban sementara, final di gerbang fase yang disebut.
- `OPEN`: belum diputuskan.

## Ringkasan

- **Semua pemblokir Fase 1 (OQ-01–OQ-06) sudah terjawab.** OQ-04 dan OQ-05 bersifat `PROVISIONAL`; keputusan finalnya diambil di gerbang Fase 1 setelah data nyata diprofil.
- **Pertanyaan baru OQ-23–OQ-27** muncul dari jawaban OQ-15/OQ-21 (deployment cloud). Kelimanya **tidak memblokir Fase 1**.

## Register

### Administratif

| ID | Pertanyaan | Keputusan | Status | Implikasi |
|---|---|---|---|---|
| OQ-01 | Rubrik dan komponen wajib mata kuliah? | Tidak ada rubrik. **Cassandra wajib.** Fokus saat ini: produk jadi dan implementasi teknis di belakangnya. Laporan dan presentasi ditangani tim. | DECIDED (USER) | Agen tidak menyusun laporan akhir/presentasi/video. Agen tetap menyediakan dokumentasi teknis (instalasi, reproduksibilitas, database, hasil eksperimen) sebagai bahan bagi tim. |
| OQ-02 | Tanggal mulai, presentasi, dan pengumpulan? | Waktu tersisa 21 hari. Tanggal pasti tidak diberikan. | DECIDED (USER) | Dokumen memakai **D1 = 2026-11-19, D21 = 2026-12-09** sebagai asumsi kerja (A-22). Tim mohon mengoreksi bila hitungannya berbeda. |
| OQ-03 | Siapa memegang peran R1–R4 dan berapa ketersediaannya? | Penetapan nama dilakukan nanti; dokumen memakai **R1–R4**. Ketersediaan **4 jam/hari/orang**. | DECIDED (USER) | Kapasitas maksimum ≈ 4 orang × 4 jam × 21 hari = **336 jam-orang** (batas atas, bukan target). |

### Data

| ID | Pertanyaan | Keputusan | Status | Implikasi |
|---|---|---|---|---|
| OQ-04 | Produk satelit? | Kandidat profiling: **(A) VIIRS S-NPP saja** dan **(B) VIIRS S-NPP + NOAA-20**. MODIS tidak dipakai di MVP. | PROVISIONAL (final di gerbang Fase 1) | Fase 1 memprofil kedua opsi dan merekomendasikan salah satu. |
| OQ-05 | Periode historis? | Profil **1 tahun penuh** terlebih dahulu untuk mengukur volume; target **≥2 tahun penuh** yang mencakup setidaknya satu musim kemarau dengan aktivitas deteksi tinggi. | PROVISIONAL (final di gerbang Fase 1) | Tahun pasti dipilih berdasarkan hasil profiling. |
| OQ-06 | Cakupan geografis dan granularitas? | **Seluruh Indonesia, tingkat provinsi.** Kabupaten = *Could*. | DECIDED (DEFAULT) | — |
| OQ-07 | Sumber batas administrasi provinsi? | Dievaluasi di Fase 1. Kriteria: memuat 38 provinsi, lisensi jelas untuk penggunaan akademik, ukuran wajar. Versi dan tanggal unduh dicatat. | DECIDED (DEFAULT) — kriteria; sumber dipilih di Fase 1 | — |

### Kebijakan data

| ID | Pertanyaan | Keputusan | Status |
|---|---|---|---|
| OQ-08 | Zona waktu untuk tanggal agregasi harian dan tampilan? | Timestamp kanonis disimpan dalam **UTC**; tanggal agregasi dan tampilan memakai **zona waktu lokal provinsi (WIB/WITA/WIT)**. | DECIDED (DEFAULT) |
| OQ-09 | Kebijakan confidence? | **Simpan semua** deteksi, tidak ada penghapusan saat ingest. Default tampilan diputuskan di Fase 2. | DECIDED (DEFAULT) |
| OQ-10 | Mode ingestion dan kebijakan NRT vs arsip? | MVP: **arsip historis saja**. NRT manual = *Should*; NRT terjadwal = *Could*. Jika NRT dipakai, arsip menggantikan NRT untuk periode yang tumpang tindih. | DECIDED (DEFAULT) — perlu ditinjau ulang terkait OQ-25 |
| OQ-11 | Deteksi di luar poligon provinsi? | **Disimpan dengan status wilayah khusus**, dikeluarkan dari ranking provinsi, dan jumlahnya dilaporkan di monitoring. | DECIDED (DEFAULT) |
| OQ-12 | Sumber panas statis? | Memakai field `type` bila tersedia (dicek di Fase 1); jika tidak, dinyatakan sebagai keterbatasan. | DECIDED (DEFAULT) |

### Cassandra

| ID | Pertanyaan | Keputusan | Status |
|---|---|---|---|
| OQ-13 | Definisi "sharding experiment"? | **Eksperimen bucketing partition key = wajib.** Observasi distribusi token multi-node = jika lingkungan multi-node tersedia (lihat OQ-24). | DECIDED (DEFAULT) |
| OQ-14 | Eksperimen replikasi dan failure wajib? | **Should.** Eksperimen 3 node **boleh dijalankan di laptop** (keputusan tim, 2026-11-19) asalkan memenuhi spesifikasi minimum dan lulus smoke test di [07-three-node-laptop-spec.md](07-three-node-laptop-spec.md). Cloud adalah alternatif (OQ-23). | DECIDED (USER + DEFAULT) |
| OQ-17 | Versi Cassandra dan penggunaan fitur indeks? | Diputuskan lewat ADR di Fase 3/4. Indeks sekunder hanya dipakai dengan justifikasi access pattern tertulis. | DECIDED (DEFAULT) — keputusan teknis ditunda ke Fase 3/4 |

### Infrastruktur & proses

| ID | Pertanyaan | Keputusan | Status | Implikasi |
|---|---|---|---|---|
| OQ-15 | Spesifikasi laptop anggota? | **Tidak relevan.** Tidak semua anggota wajib menjalankan Docker Compose. Aplikasi akan dideploy ke cloud. | DECIDED (USER) | Alur pengembangan harus mendukung anggota yang hanya menjalankan sebagian stack (OQ-27). |
| OQ-16 | Repo publik atau privat? | **Privat selama pengembangan.** `.env` tidak pernah di-commit. | DECIDED (DEFAULT) | Tim perlu mengatur visibilitas repo di GitHub (NA-05). |
| OQ-18 | Pembagian kerja Claude Code vs Codex? | **Satu implementer per tugas + agen lain sebagai reviewer**, branch per tugas, dirinci di AGENTS.md (Fase 4). | DECIDED (DEFAULT) | — |

### Produk

| ID | Pertanyaan | Keputusan | Status |
|---|---|---|---|
| OQ-19 | Persona primer MVP? | Primer: **analis lingkungan dan peneliti**. Sekunder: pemerintah daerah. | DECIDED (DEFAULT) |
| OQ-20 | Bahasa UI dashboard? | **Indonesia.** | DECIDED (DEFAULT) |
| OQ-21 | Apakah aplikasi harus dapat diakses online? | **Ya, akan di-hosting**, tetapi prioritas saat ini **lokal**. Video demo ditangani tim. | DECIDED (USER) |
| OQ-22 | Cakupan fitur monitoring pipeline? | **Tabel run + endpoint + halaman sederhana.** | DECIDED (DEFAULT) |

## Pertanyaan baru dari jawaban OQ-15/OQ-21 (tidak memblokir Fase 1)

| ID | Pertanyaan | Mengapa penting | Opsi | Rekomendasi (`RECOMMENDATION`) | Prioritas / dibutuhkan sebelum | Status |
|---|---|---|---|---|---|---|
| OQ-23 | Penyedia cloud dan anggaran apa yang tersedia (termasuk kredit mahasiswa)? | Menentukan ukuran server, kelayakan Cassandra (butuh memori cukup besar), dan kelayakan eksperimen multi-node. | Bergantung pada akses tim | Desain tetap **netral terhadap penyedia** (container + konfigurasi lewat environment variable). Penyedia dipilih paling lambat **D12**. | P2 / D12 | OPEN |
| OQ-24 | Bagaimana Cassandra dijalankan di cloud? | Layanan terkelola yang "kompatibel Cassandra" dapat membatasi kontrol atas replikasi, konfigurasi node, dan observasi token, sehingga eksperimen tidak setara dengan lingkungan lokal (`AI-PRIOR`, perlu dicek). | (A) Self-managed: container Cassandra di VM, sama dengan lokal · (B) Layanan terkelola kompatibel Cassandra | **A**, karena konsisten dengan lingkungan lokal dan eksperimen. | P2 / Fase 3 (ADR) | OPEN |
| OQ-25 | Di mana ingestion berjalan setelah deploy? | Data di server cloud harus dimuat oleh pipeline yang sama dan tetap idempoten. | (A) Dijalankan dari laptop ke DB cloud · (B) Container pipeline dijalankan manual di server cloud · (C) Job terjadwal di cloud | **B.** Port Cassandra tidak perlu dibuka ke internet. Penjadwalan (C) tetap *Could*. | P2 / Fase 3 | OPEN |
| OQ-26 | Kebutuhan keamanan minimum untuk aplikasi publik? *(sensitif keamanan, wajib disetujui manusia)* | API publik tanpa autentikasi rentan disalahgunakan. Port Cassandra yang terekspos adalah risiko serius. | — | Minimum: HTTPS; Cassandra hanya di jaringan privat; API read-only; CORS terbatas ke domain frontend; secret lewat environment/secret store; rate limit sederhana = *Should*. | P2 / Fase 3 | OPEN |
| OQ-27 | Bagaimana alur kerja anggota yang tidak menjalankan Docker Compose? | Frontend/backend tidak boleh terblokir oleh ketiadaan database lokal. | (A) Frontend memakai mock API sesuai kontrak · (B) Backend dev bersama di cloud · (C) A lalu B | **C**: mock berbasis kontrak API sejak awal, lalu backend dev bersama setelah deployment awal tersedia. | P2 / Fase 4 | OPEN |
