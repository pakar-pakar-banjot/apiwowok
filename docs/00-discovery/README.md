# Fase 0 — Project Discovery: NusaFire

| Atribut | Nilai |
|---|---|
| Proyek | NusaFire — Indonesian Hotspot Intelligence |
| Fase | 0 — Project Discovery |
| Status | **DIPERBARUI 2026-11-19** — open questions dijawab tim; menunggu konfirmasi G0 (status MAP_KEY) |
| Tanggal penyusunan | 2026-11-19 |
| Penyusun | Claude Code (AI), untuk ditinjau oleh tim (4 anggota) |
| Kode aplikasi | Tidak ada (sesuai aturan Fase 0) |

## Daftar dokumen

| No | Dokumen | Isi |
|---|---|---|
| 01 | [01-project-charter.md](01-project-charter.md) | Piagam proyek awal: masalah, pengguna, tujuan, ruang lingkup, MVP, MoSCoW, peran, jadwal |
| 02 | [02-analysis-and-feasibility.md](02-analysis-and-feasibility.md) | Kontradiksi dalam brief, keputusan yang belum dibuat, kajian kelayakan 21 hari |
| 03 | [03-assumptions-register.md](03-assumptions-register.md) | Register asumsi beserta cara validasinya |
| 04 | [04-open-questions-register.md](04-open-questions-register.md) | Register pertanyaan terbuka/keputusan yang menunggu persetujuan |
| 05 | [05-risk-register.md](05-risk-register.md) | Register risiko teknis & proyek |
| 06 | [06-next-actions.md](06-next-actions.md) | Tindakan berikutnya per peran, langkah mendapatkan MAP_KEY, gerbang persetujuan |
| 07 | [07-three-node-laptop-spec.md](07-three-node-laptop-spec.md) | Spesifikasi minimum laptop dan smoke test untuk eksperimen Cassandra 3 node |

## Label status informasi

Semua dokumen Fase 0 memakai label berikut agar fakta tidak tercampur dengan dugaan:

| Label | Arti |
|---|---|
| `VERIFIED` | Diverifikasi langsung di sesi ini (mis. isi repositori, remote Git). |
| `USER` | Berasal dari brief tim. Belum tentu fakta teknis. |
| `AI-PRIOR` | Pengetahuan awal AI tentang sistem eksternal (NASA FIRMS, Cassandra, dll.). **Belum diverifikasi** untuk proyek ini; wajib dicek di Fase 1/3. |
| `ASSUMPTION` | Asumsi rekayasa sementara agar perencanaan bisa berjalan. |
| `RECOMMENDATION` | Rekomendasi AI. Bukan keputusan. |
| `PENDING` | Keputusan menunggu persetujuan manusia. |
| `UNKNOWN` | Informasi belum tersedia. |

> Catatan: dalam Fase 0 **tidak ada** data FIRMS yang diunduh atau diperiksa. Semua pernyataan tentang isi dataset FIRMS berlabel `AI-PRIOR` dan akan diuji di Fase 1.

---

## Laporan Fase 0 (format 12 bagian)

### 1. Tujuan fase
Memahami konteks proyek, menemukan kontradiksi dan keputusan yang belum dibuat, menilai kelayakan dalam 21 hari, serta mengusulkan MVP yang realistis sebelum ada data yang diperiksa atau kode yang ditulis.

### 2. Konteks proyek saat ini
- Repositori `VERIFIED`: branch `main`, 1 commit (`f0572ff first commit`), hanya berisi `README.md` kosong. Remote: `github.com/pakar-pakar-banjot/apiwowok`. Visibilitas repo (publik/privat): `UNKNOWN`.
- Belum ada spesifikasi, data, kode, atau konfigurasi lingkungan.
- Brief proyek (`USER`) memuat 10 fitur usulan, tech stack awal, dan pipeline usulan.
- Jawaban tim (2026-11-19, `USER`): tidak ada rubrik; Cassandra wajib; fokus pada produk jadi dan implementasi teknis; laporan, presentasi, dan video ditangani tim; sisa waktu 21 hari; peran R1–R4 dengan ±4 jam/hari; spesifikasi laptop tidak relevan; aplikasi akan di-hosting di cloud dengan prioritas lokal terlebih dahulu. Pertanyaan lain memakai default/rekomendasi.

### 3. Tugas yang memerlukan keputusan manusia
Lihat [04-open-questions-register.md](04-open-questions-register.md). Semua pemblokir Fase 1 (OQ-01–OQ-06) **sudah terjawab**. Yang tersisa untuk G0 hanya konfirmasi NA-01 (MAP_KEY FIRMS). Pertanyaan baru OQ-23–OQ-27 (deployment cloud) tidak memblokir Fase 1.

### 4. Tugas yang cocok diotomasi (oleh agen AI, di fase berikutnya)
- Profiling dataset (skrip Pandas: hitung null, duplikat, rentang nilai) — Fase 1.
- Pembuatan kerangka repositori, Docker Compose, konfigurasi linting/test — Fase 4.
- Kode ETL, endpoint API, komponen UI sesuai spesifikasi yang disetujui — Fase 5–6.
- Penulisan test otomatis dan skrip benchmark — Fase 5–7.

Yang **tidak** boleh diotomasi tanpa persetujuan: keputusan ruang lingkup, skema Cassandra, kebijakan kualitas data, interpretasi hasil analitis.

### 5. Rencana eksekusi terperinci
Lihat jadwal tingkat tinggi di [01-project-charter.md §10](01-project-charter.md#10-jadwal-tingkat-tinggi-usulan) dan daftar tindakan di [06-next-actions.md](06-next-actions.md).

### 6. Rekomendasi teknis (ringkas)
1. Perkecil ruang lingkup ke MVP 6 kapabilitas wajib (lihat charter §6).
2. Gunakan **satu keluarga sensor (VIIRS 375 m)** untuk MVP; jangan membandingkan MODIS vs VIIRS.
3. Ingestion **batch historis dahulu**, NRT sebagai *Should*.
4. Simpan waktu kanonis dalam **UTC**; tanggal agregasi harian berdasarkan **zona waktu lokal provinsi** (WIB/WITA/WIT) — lihat C-07.
5. Agregat dibangun ulang secara deterministik oleh pipeline, **bukan** dengan counter table (counter tidak idempoten).
6. Cassandra single-node untuk pengembangan dan hosting; cluster 3 node berumur pendek **hanya** untuk eksperimen replikasi.
7. Fase dokumentasi 0–3 dibatasi waktu (*time-boxed*) maksimal ±4 hari total.
8. Satu set image container untuk lokal dan cloud; deployment cloud dimulai setelah integrasi lokal (≥D13).

Rekomendasi 1–7 diterima tim sebagai default (2026-11-19). Rekomendasi 8 berasal dari jawaban OQ-21 dan dirinci di OQ-23–OQ-27 (`OPEN`).

### 7. Artefak yang dihasilkan
Enam dokumen pada daftar di atas + file README ini. Tidak ada kode, dependensi, atau skema yang dibuat. `README.md` di root repositori diisi penunjuk singkat ke folder ini.

### 8. Checklist validasi (untuk reviewer manusia)
- [ ] Problem statement dan target pengguna sesuai maksud tim.
- [ ] Pembagian Must/Should/Could/Won't dapat diterima.
- [ ] Tidak ada fakta tentang FIRMS yang diperlakukan sebagai terverifikasi.
- [ ] Usulan peran sesuai kemampuan anggota.
- [ ] Jadwal sesuai kalender akademik tim (ujian, tugas lain).
- [ ] Risiko utama dan mitigasinya masuk akal.

### 9. Kriteria penerimaan Fase 0
Fase 0 dianggap selesai bila:
1. ✅ Tim menyetujui piagam proyek dan MVP (melalui default/rekomendasi, dengan revisi hosting).
2. ✅ Pertanyaan pemblokir Fase 1 (OQ-01–OQ-06) dijawab.
3. ✅ Peran disepakati sebagai R1–R4 (nama ditetapkan kemudian).
4. ⏳ MAP_KEY FIRMS sudah diminta (NA-01).

### 10. Risiko tersisa
Risiko teratas (skor tertinggi) — detail di [05-risk-register.md](05-risk-register.md):
R-01 scope creep, R-02 overhead proses/dokumentasi, R-23 deployment cloud menyita waktu MVP, R-25 keamanan aplikasi publik, R-06 deduplikasi NRT vs arsip, R-03 struktur data FIRMS berbeda dari asumsi. R-19 (rubrik) turun ke prioritas rendah.

### 11. Gerbang persetujuan
**STOP.** Fase 1 belum dimulai. Dibutuhkan konfirmasi eksplisit "G0 disetujui" beserta status MAP_KEY.

### 12. Tindakan berikutnya yang direkomendasikan
Lihat [06-next-actions.md](06-next-actions.md). Yang paling mendesak: daftar MAP_KEY FIRMS dan atur repo menjadi privat. Inventaris opsi cloud (NA-07) dapat menyusul paling lambat D12.
