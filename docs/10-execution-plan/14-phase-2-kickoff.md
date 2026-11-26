# Kickoff Fase 2 — Requirements & Semantik Data

> Catatan koordinasi, **bukan** tugas WBS dan bukan pengganti kartu tugas. Sumber kebenaran status tetap `python -I docs/10-execution-plan/tools/task.py` dan [13-progress-tracker.md](13-progress-tracker.md). Dibuat 2026-11-22 atas permintaan manusia; perubahan file ini di luar WBS.

## 1. Posisi

| Item | Nilai |
|---|---|
| Fase | 2 — Requirements & semantik data (mulai 2026-11-22, setelah G1 disetujui 4/4) |
| Gerbang | **G2**, target **D7 (2026-11-25)**; paket gerbang = X-P2-901 |
| Syarat masuk G2 | D-P2-001, D-P2-002, D-P2-003, C-P2-001, A-P2-001, B-P2-001, X-P2-901 |
| Keputusan G1 yang berlaku | Periode 2023-01-01 s.d. sekarang (HD-09); NOAA-20 + NOAA-21, SP lalu NRT; tumpang tindih per (satelit, tanggal UTC) (HD-10); batas BIG Juni 2026, cadangan B5 (HD-08); DQ-01…DQ-15 (HD-11); polling 15 menit |

## 2. Status tugas (per 2026-11-22, dari `task.py check`)

| Tugas | Pemilik | Rencana | Status | Hard-dependensi |
|---|---|---|---|---|
| A-P2-001 Semantik data & aturan perhitungan | Lanang (R1/A) | D4 | ▶ SIAP (jalur kritis) | GATE-G1 ✅ |
| C-P2-001 NFR kuantitatif | Zita (R3/C) | D3 | ▶ SIAP | — |
| D-P2-001 FR final | Abigail (R4/D) | D2→D3 | ⛔ terblokir | D-P1-001 ⏳ (menunggu `disetujui:`) |
| D-P2-002 Acceptance criteria per FR | Abigail (R4/D) | D3→D4 | ⛔ terblokir | D-P2-001 |
| B-P2-001 Kebutuhan query (Q-xx) | Abi Funn (R2/B) | D3→D4 | ⛔ terblokir | D-P2-001 (A-P2-001 = Soft) |
| D-P2-003 Kunci MVP + urutan descoping | Abigail (R4/D) | D6 | ⛔ terblokir | D-P2-002, C-P2-001 |
| X-P2-901 Paket gerbang G2 | Abi Funn (R2/B, koordinator) | D7 | ⛔ terblokir | D-P2-003, A-P2-001, B-P2-001 |

**Penghalang utama:** D-P1-001 (`docs/02-requirements/00-draft-user-stories.md`) belum disetujui seorang manusia. Selama itu, rantai D-P2-001 → D-P2-002 → D-P2-003 dan B-P2-001 tidak boleh dimulai. Jalan keluar: (a) seorang manusia mereview draf lalu mengisi `disetujui:` di tracker, atau (b) tim mengizinkan mulai lebih awal secara eksplisit; izinnya (siapa, kapan) dikutip di PR tugas terkait.

## 3. Tugas per orang

### Lanang (R1/A) — A-P2-001
- **Keluaran:** `docs/03-specs/data/01-data-semantics.md`.
- **Isi:** aturan SEM-xx yang mendefinisikan "jumlah deteksi": tanggal lokal per zona waktu provinsi (OQ-08), default confidence (OQ-09), titik di luar provinsi (OQ-11), sumber statis (OQ-12), presedensi SP/NRT (HD-10), penggabungan satelit.
- **Langkah:** tulis SEM-xx → beri contoh numerik → tandai keputusan yang butuh persetujuan.
- **Kriteria:** setiap angka di dashboard dapat dijelaskan oleh satu aturan SEM-xx.
- **Serah-terima:** ke Abi (B-P2-001, X-P2-901). Membuka A-P3-001.
- **Catatan:** angka hanya dari perintah yang benar-benar dijalankan; beri label `VERIFIED`/`ASSUMPTION`/…. Hotspot ≠ kebakaran terkonfirmasi; jangan membandingkan jumlah deteksi antar sensor.

### Zita (R3/C) — C-P2-001
- **Keluaran:** `docs/02-requirements/02-non-functional-requirements.md`.
- **Isi:** NFR-xx dengan target, metode ukur, dan alasan: latensi API, batas titik peta, kesegaran data, interval polling (15 menit, angka final di sini), keamanan, reproduksibilitas. Tandai NFR yang hanya berlaku di cloud.
- **Kriteria:** setiap NFR punya angka dan metode verifikasi.
- **Dasar angka:** volume terukur dan latensi NRT Fase 1 (1,8 sampai ±9 jam, [04 §3](../01-dataset/04-nrt-vs-sp-and-latency.md#3-latensi-nrt-a-p1-008)).
- **Serah-terima:** ke Abigail (D-P2-003).
- **Opsional, bukan syarat G2:** C-P1-001 (inventaris toolchain & opsi cloud, NA-07) masih terbuka dan dibutuhkan untuk OQ-23…OQ-27.

### Abi Funn (R2/B, koordinator) — B-P2-001 dan X-P2-901
- **B-P2-001** → `docs/03-specs/database/01-query-requirements.md`: setiap FR yang membaca data dipetakan ke ≥1 Q-xx (parameter, filter, urutan, kardinalitas, estimasi baris hasil dari volume); query yang butuh pra-agregasi ditandai. Verifikasi: matriks FR↔Q lengkap. Serah-terima ke Abigail (D-P2-003).
- **X-P2-901** → `docs/STATUS.md`: kumpulkan dokumen Fase 2, bagikan paket G2, catat keputusan (mekanisme gerbang 3/4 + pemilik area, GATE-EP). Jalan setelah semua dokumen di atas selesai.
- **Sementara menunggu:** jangan mulai B-P4-001/B-P3-004 sebelum G2 kecuali tim mengizinkan secara eksplisit.

### Abigail (R4/D) — D-P2-001, D-P2-002, D-P2-003
- **D-P2-001** → `docs/02-requirements/01-functional-requirements.md`: FR-xx (pernyataan, persona, prioritas, sumber) dari draf story + keputusan G1; matriks fitur #1…#12 ↔ FR; tandai MoSCoW. Kriteria: tiap fitur Must ↔ ≥1 FR, tidak ada FR tanpa fitur.
- **D-P2-002** → bagian AC di file yang sama: ≥1 AC Given/When/Then per FR, termasuk kasus kosong/error; tandai AC yang butuh data nyata. Kriteria: tiap FR Must punya AC terukur.
- **D-P2-003** → `docs/02-requirements/03-mvp-lock.md`: daftar Must final + urutan descoping, mengikuti [charter §6](../00-discovery/01-project-charter.md#6-ruang-lingkup-awal-dan-mvp). Menunggu D-P2-002 dan C-P2-001. Serah-terima ke Abi (X-P2-901).
- **Langkah pertama:** D-P1-001 perlu disetujui seorang manusia (lihat §2).

## 4. Urutan kerja yang disarankan

1. **Sekarang, paralel:** Lanang → A-P2-001; Zita → C-P2-001; manusia mana pun → putuskan D-P1-001.
2. **Setelah D-P1-001 ✅:** Abigail → D-P2-001, lalu D-P2-002; Abi → B-P2-001 (dapat dimulai begitu D-P2-001 ✅).
3. **D6:** Abigail → D-P2-003 (butuh D-P2-002 dan C-P2-001 ✅).
4. **D7:** Abi → X-P2-901; G2 diputuskan tim.

## 5. Aturan yang tetap berlaku

- Satu tugas = satu branch (`<peran>/<ID>-<slug>`) = satu worktree = satu implementer. Mulai dengan `task.py check <ID>` (exit `0`), selesai dengan `task.py scope <ID> --base <branch asal>` (exit `0`).
- Catat progres hanya di baris task ID sendiri di [13-progress-tracker.md](13-progress-tracker.md), lalu jalankan `build_plan.py` (`ISSUES: 0`). `disetujui:` hanya diisi bila manusia menyatakannya langsung.
- Akhir fase: **STOP dan tunggu persetujuan G2.** Tidak ada pekerjaan Fase 3 sebelum G2, kecuali tim mengizinkan secara eksplisit.
