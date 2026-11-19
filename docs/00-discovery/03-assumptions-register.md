# 03 — Register Asumsi

Status: **DRAFT**. Setiap asumsi harus divalidasi atau dibatalkan pada fase yang tercantum. Asumsi yang terbukti salah diberi status `INVALIDATED` beserta dampaknya — jangan dihapus.

Kolom *Status*: `OPEN` (belum divalidasi) · `VALIDATED` · `INVALIDATED`.

| ID | Asumsi | Label | Dampak jika salah | Cara validasi | Fase validasi | Status |
|---|---|---|---|---|---|---|
| A-01 | Apache Cassandra adalah teknologi wajib (dipersyaratkan mata kuliah), bukan pilihan bebas. | `ASSUMPTION` (tersirat dari brief) | Jika bebas, pemilihan DB perlu ADR tersendiri. | Konfirmasi rubrik (OQ-01). | 0 | OPEN |
| A-02 | Tim terdiri dari 4 orang dengan durasi 21 hari kalender. | `USER` | Jadwal & peran harus disusun ulang. | Konfirmasi tim. | 0 | OPEN |
| A-03 | Kapasitas efektif tiap anggota sekitar 3–4 jam/hari rata-rata, karena ada mata kuliah lain. | `ASSUMPTION` | Jika lebih kecil, MVP harus dipangkas lagi. | Tiap anggota menyatakan ketersediaan (OQ-03). | 0 | OPEN |
| A-04 | Aplikasi dijalankan lokal via Docker Compose; tidak perlu hosting publik. | `ASSUMPTION` | Butuh pekerjaan deployment & keamanan tambahan. | Rubrik (OQ-21). | 0 | OPEN |
| A-05 | Data NASA FIRMS dapat diakses gratis; API memerlukan MAP_KEY. | `AI-PRIOR` | Jalur ekstraksi berubah. | Mendaftar MAP_KEY; mencoba unduhan. | 1 | OPEN |
| A-06 | Field FIRMS mencakup latitude, longitude, tanggal & waktu akuisisi, satelit, instrumen, confidence, FRP — tetapi nama & formatnya berbeda antar produk (mis. kolom brightness MODIS vs VIIRS). | `USER` + `AI-PRIOR` | Data dictionary & normalisasi berubah. | Inspeksi header dan sampel file nyata. | 1 | OPEN |
| A-07 | `acq_date` dan `acq_time` dinyatakan dalam UTC; `acq_time` berformat HHMM (mungkin tanpa nol di depan). | `AI-PRIOR` | Seluruh logika waktu & agregasi harian salah. | Dokumentasi resmi FIRMS + cek sampel. | 1 | OPEN |
| A-08 | FIRMS tidak menyediakan ID unik per deteksi, sehingga deduplikasi membutuhkan natural key komposit. | `AI-PRIOR` | Jika ada ID, dedup jauh lebih sederhana. | Inspeksi kolom. | 1 | OPEN |
| A-09 | Data NRT kemudian digantikan versi arsip standar, dan keduanya dapat dibedakan dari field `version`. | `AI-PRIOR` | Kebijakan dedup NRT vs arsip berubah. | Bandingkan file NRT & arsip untuk tanggal yang sama. | 1 | OPEN |
| A-10 | Volume deteksi VIIRS untuk Indonesia selama beberapa tahun dapat diproses Pandas di memori laptop dan disimpan di Cassandra single-node. | `ASSUMPTION` | Butuh pemrosesan per-chunk atau pemangkasan periode. | Hitung baris & ukuran file nyata. | 1 | OPEN |
| A-11 | Ada sumber batas provinsi Indonesia (versi 38 provinsi) dengan lisensi yang memperbolehkan penggunaan akademik. | `ASSUMPTION` | Pengayaan memakai versi lama dengan keterbatasan terdokumentasi. | Evaluasi kandidat sumber. | 1 | OPEN |
| A-12 | Minimal satu anggota memiliki laptop dengan RAM cukup untuk cluster Cassandra 3 node di Docker. | `ASSUMPTION` | Eksperimen replikasi turun ke *Could* / keterbatasan. | Survei hardware (OQ-15). | 0–1 | OPEN |
| A-13 | Laptop anggota memakai Windows (setidaknya sebagian) dengan Docker Desktop/WSL2. | `ASSUMPTION` (lingkungan sesi ini Windows 11 — `VERIFIED` untuk satu mesin saja) | Instruksi setup perlu varian OS. | Survei (OQ-15). | 0 | OPEN |
| A-14 | Dashboard read-only; tidak membutuhkan autentikasi pengguna. | `ASSUMPTION` | Tambahan fitur keamanan. | Konfirmasi tim (Fase 2). | 2 | OPEN |
| A-15 | Ingestion batch dengan checkpoint dan trigger manual sudah memenuhi syarat "incremental processing". | `ASSUMPTION` | Butuh penjadwal otomatis. | Konfirmasi tim/rubrik. | 2 | OPEN |
| A-16 | Penilaian lebih menekankan rekayasa data (pipeline, Cassandra, eksperimen) daripada estetika UI. | `ASSUMPTION` | Alokasi waktu frontend perlu dinaikkan. | Rubrik (OQ-01). | 0 | OPEN |
| A-17 | Dokumentasi berbahasa Indonesia; identifier kode, path API, dan konvensi teknis berbahasa Inggris. | `USER` | — | — | — | VALIDATED (brief) |
| A-18 | Tim memiliki akses ke Claude Code dan OpenAI Codex selama proyek. | `USER` | Pembagian kerja agen berubah. | — | — | OPEN |
| A-19 | Repositori saat ini kosong (hanya `README.md` kosong, 1 commit) dengan remote GitHub `pakar-pakar-banjot/apiwowok`. | `VERIFIED` (2026-11-19) | — | — | — | VALIDATED |
| A-20 | Satu versi batas wilayah yang tetap dipakai untuk seluruh periode historis (bukan batas yang berubah mengikuti waktu). | `ASSUMPTION` / `PENDING` | Jika memakai batas historis per tahun, pengayaan jauh lebih kompleks. | Keputusan tim (OQ-07). | 1 | OPEN |
| A-21 | Tile peta dasar publik (mis. OpenStreetMap) boleh dipakai untuk demo akademik bervolume rendah, dengan atribusi. | `AI-PRIOR` | Ganti penyedia tile. | Cek kebijakan penggunaan tile. | 3 | OPEN |
