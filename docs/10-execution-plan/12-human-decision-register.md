# 12 — Human Decision Register

> Keputusan yang **harus** diambil empat anggota tim. Agen hanya mengusulkan. Status: `PENDING HUMAN DECISION` kecuali diubah tim. Kolom *Diputuskan* diisi tim (tanggal + siapa).
> Keputusan dari Fase 0 yang sudah disetujui **tidak** dibuka ulang di sini.

## Dibutuhkan untuk GATE-EP (target D2, 2026-11-20) — **DIPUTUSKAN 2026-11-19**

Tim menyetujui semua rekomendasi di bawah pada 2026-11-19 (D1). Keputusan disampaikan oleh anggota tim lewat sesi Claude Code, lalu dicatat oleh agen. Penugasan peran ditetapkan langsung oleh tim tanpa matriks skill.

| ID | Keputusan | Opsi | Rekomendasi | Dampak bila tertunda | Diputuskan |
|---|---|---|---|---|---|
| HD-01 | Anggota mana memegang R1–R4 | Isi matriks skill [01 §0](01-role-charters.md#0-penugasan-anggota-hd-01) | Pemilik peran = skill inti ≥2 | Tidak ada tugas yang bisa mulai | **Tim, 2026-11-19:** R1/A = **Lanang**, R2/B = **Abi Funn**, R3/C = **Zita**, R4/D = **Abigail**. Matriks skill tidak dipakai. |
| HD-02 | Koordinator integrasi | R1 / **R2** / R3 / R4 / bergilir | **R2**: satu-satunya opsi tanpa masalah jadwal ([09 §2](09-risk-capacity-plan.md#2-pemilihan-koordinator-integrasi)) | Paket gerbang tidak punya pemilik | **Tim, 2026-11-19:** R2 (Abi Funn) |
| HD-03 | Ketersediaan nyata per anggota (jam/hari, hari tidak tersedia, akhir pekan) | — | Konfirmasi 4 jam/hari setiap hari, atau catat pengecualian | Jadwal tetap `PROVISIONAL` | **Tim, 2026-11-19:** 4 jam/hari setiap hari, termasuk akhir pekan (ditambah HD-07) |
| HD-04 | Persetujuan rencana eksekusi + struktur direktori + kepemilikan file (CR-01, CR-02, CR-04) | Setujui / revisi | Setujui | Fase 4 tidak bisa mulai | **Tim, 2026-11-19:** disetujui; CR-01, CR-02, CR-04 disetujui ([change-requests](../change-requests/)) |
| HD-05 | Mekanisme persetujuan gerbang (charter §11 `PENDING`) | Mayoritas + pemilik area / konsensus / koordinator | Mayoritas (3 dari 4) + pemilik area setuju; asinkron ≤ ½ hari | Gerbang macet | **Tim, 2026-11-19:** mayoritas 3 dari 4 + pemilik area setuju; asinkron ≤ ½ hari kerja |
| HD-06 | Pasangan reviewer | Default WBS: A↔B, C↔D (+ pengecualian per tugas) | Pakai default | — | ~~Tim, 2026-11-19: default, yaitu Lanang ↔ Abi Funn, Zita ↔ Abigail~~ → **Diganti 2026-11-19** (disampaikan anggota tim lewat sesi Claude Code): **tidak ada review wajib antar peran.** Tugas selesai saat seorang manusia, anggota tim mana pun, mengisi `disetujui:`. Dependensi Hard hanya butuh persetujuan itu. Persetujuan gerbang (HD-05) tidak berubah. |
| HD-07 | Kapasitas vs ruang lingkup | (a) terima D15/D18 · (b) **±5 jam/hari pada D9–D15 untuk rantai kritis** · (c) potong Should lebih awal | **(b)**, dengan (c) sebagai cadangan otomatis | Integrasi D15, tanpa buffer akhir | **Tim, 2026-11-19:** (b). R1 (Lanang) dan R3 (Zita) ±5 jam/hari pada D9–D15; (c) sebagai cadangan. Hasil jadwal ulang: G6 **D14**, G8 **D20** ([05](05-project-schedule.md)) |
| HD-22 | Poller latensi NRT Fase 1 (berjalan sejak 2026-11-19 09:09 UTC, 2 request per 15 menit, berhenti sendiri setelah 24 jam) yang memakai kuota API. Unduhan sampel **sudah selesai** (2026-11-19 ±10:18 UTC). | Lanjutkan sampai selesai / hentikan sekarang | **Lanjutkan**: dibutuhkan untuk P1-10 (interval polling); ±8 transaksi per 15 menit, jauh di bawah 5000/10 menit | Pengamatan latensi tidak lengkap | **Tim, 2026-11-19:** lanjutkan sampai selesai sendiri (±2026-11-20 09:09 UTC) |
| HD-23 | Tanggal presentasi dan pengumpulan (A-22 mengasumsikan D21 = 2026-12-09) | — | Konfirmasi ke dosen | Seluruh jadwal bisa bergeser | **Tim, 2026-11-19:** presentasi diasumsikan **2026-12-10** (D22). Tanggal ini dianggap tidak kritis. Hari kerja terakhir tetap D21 = 2026-12-09, dan G8 direncanakan D20. Tidak perlu konfirmasi lanjutan. |
| HD-24 | Apakah `scratch/phase1/` dan `docs/10-execution-plan/` di-commit, dan di branch apa | commit di branch `docs/phase-1-dataset` / tidak | Commit keduanya (tanpa `data/`), branch terpisah, PR ke `main` | Agen lain tidak melihat rencana | **Tim, 2026-11-19:** commit keduanya tanpa `data/`. Pekerjaan Fase 1 sudah di `main` (`9214337`) atas permintaan langsung tim. Rencana eksekusi menyusul lewat branch terpisah + PR ke `main` (**belum dijalankan**). |

## Dibutuhkan di G1 (target D3)

| ID | Keputusan | Rekomendasi (dari Fase 1, menyusul) | Diputuskan |
|---|---|---|---|
| HD-09 | Periode historis final (OQ-05) | Di laporan Fase 1 | |
| HD-10 | Aturan tumpang tindih NRT/SP NOAA-21 (P1-09) | Di 04-nrt-vs-sp | |
| HD-11 | Aturan kualitas data awal | Di 06-data-quality-rules | |
| HD-08 | Lisensi BIG: boleh dipakai di aplikasi publik dan di-commit? (A-11, OQ-07) | Konfirmasi ke BIG/tanahair.indonesia.go.id; sampai ada jawaban: snapshot lokal, cadangan HDX | |

## Dibutuhkan di G2–G4 (D5–D8)

| ID | Keputusan | Pemilik usulan | Rekomendasi | Diputuskan |
|---|---|---|---|---|
| HD-12 | Default tampilan confidence (OQ-09) | R1 + R4 | Di A-P2-001 | |
| HD-13 | Target angka NFR (latensi API, batas titik peta, ambang kesegaran) | R3 | Di C-P2-001 | |
| HD-14 | Tooling frontend: TypeScript, library chart, alat E2E | R4 | TypeScript + Vitest + Playwright; library chart dipilih di ADR-001 | |
| HD-15 | CI memakai GitHub Actions di repo privat (kuota menit) | R3 | Ya, dengan path filter | |
| HD-17 | Mode akses Codex (CLI lokal di worktree vs cloud dengan akses repo) | Tim | CLI lokal di worktree, hanya-baca untuk review | |
| HD-18 | Repo privat (NA-05) + branch protection `main` | Tim | Privat; PR wajib; 1 approval; CI hijau | |
| HD-19 | Kanal komunikasi & standup (NA-06) | R4 | Standup asinkron harian (kemarin / hari ini / hambatan) di satu kanal | |
| HD-20 | Urutan descoping (dikunci di D-P2-003) | R4 | Should Fase 7 → Should Fase 6 → kab/kota → B-P4-002 | |
| HD-21 | *Grid assignment* / query viewport peta | R2 | Tidak di MVP; peta per provinsi + tanggal (C-11) | |

## Dibutuhkan ≤ D12 (2026-11-30)

| ID | Keputusan | Rekomendasi | Diputuskan |
|---|---|---|---|
| HD-16 | Penyedia cloud, anggaran, cara Cassandra & poller berjalan, kontrol keamanan minimum (OQ-23–OQ-26) | Di ADR-003/004 (C-P3-003); VM tunggal self-managed, Cassandra di jaringan privat | |

## Di Fase 7–8

| ID | Keputusan | Kapan | Diputuskan |
|---|---|---|---|
| HD-25 | Teks final disclaimer ilmiah di UI | D-P6-005 | |
| HD-26 | Kesimpulan analitis laporan eksperimen | B-P7-002 | |
| HD-27 | Eksekusi rekonsiliasi NRT→SP (menghapus NRT) | A-P7-003 | |
| HD-28 | Feature freeze & kontingensi R-23 | X-P7-901 | |
