# 10 — Phase Gates, DoR, DoD, Change Management

> Status: `RECOMMENDATION`. Checklist ini melengkapi brief tim (disimpan di luar repo) dan G0 di [06-next-actions §4](../00-discovery/06-next-actions.md#4-gerbang-persetujuan-g0-checklist). Persetujuan gerbang **selalu oleh manusia**; agen hanya menyiapkan paket. Mekanisme persetujuan (HD-05, disetujui): mayoritas 3 dari 4 anggota + pemilik area setuju.

## 1. Proses review gerbang (semua gerbang)

1. Pemilik fase menandai semua tugas fase siap review.
2. Koordinator (agen boleh membantu) menyusun **paket gerbang**: checklist di bawah + tautan bukti + daftar keputusan dalam format "opsi → rekomendasi → bukti".
3. Review asinkron ≤ ½ hari kerja; keberatan ditulis sebagai komentar.
4. Keputusan dicatat di `docs/STATUS.md` (riwayat gerbang) dan register terkait melalui CR.
5. Hasilnya **Disetujui**, **Disetujui dengan syarat** (syarat menjadi tugas baru dengan ID), atau **Ditolak** (tugas yang menunggu gerbang tetap berhenti).

## 2. Gerbang

### GATE-EP — Rencana eksekusi (target D2) — **DISETUJUI 2026-11-19**
- **Masuk:** folder `docs/10-execution-plan/` lengkap; generator `ISSUES: 0`.
- **Keluar:** HD-01–HD-07 dan HD-22–HD-24 diputuskan; koordinator ditetapkan; rencana disetujui atau direvisi. (Matriks skill dihapus dari kriteria atas keputusan tim.)
- **Penerimaan:** setiap peran punya anggota bernama ([01 §0](01-role-charters.md#0-penugasan-anggota-hd-01)). Setiap anggota membaca prompt perannya sebelum tugas pertamanya (dicek pemilik masing-masing; tidak bisa diverifikasi agen).

### G1 — Dataset feasibility (target D3)
- **Masuk:** A-P1-001…010, B-P1-001 selesai; unduhan terverifikasi checksum.
- **Artefak:** `docs/01-dataset/` (inventaris, data dictionary, profil, NRT vs SP + latensi, batas, aturan DQ, rekomendasi, laporan 12 bagian).
- **Keluar (keputusan):** OQ-05 periode final; OQ-07 sumber batas (+HD-08 lisensi); aturan tumpang tindih NRT/SP (P1-09); aturan DQ awal; pembaruan register asumsi A-05–A-11, A-26 lewat CR.
- **Penerimaan:** setiap angka di laporan dapat ditelusuri ke file profil; tidak ada klaim `AI-PRIOR` tanpa label.

### G2 — Requirements (target D5–D7)
- **Masuk:** G1 disetujui; D-P2-001…003, C-P2-001, A-P2-001, B-P2-001 selesai.
- **Keluar:** FR + AC, NFR berangka, semantik data (SEM-xx), Q-xx, MVP terkunci + urutan descoping; HD-12 (default confidence), HD-13 (target NFR).
- **Penerimaan:** matriks traceability fitur ↔ FR ↔ Q-xx lengkap; setiap NFR punya metode verifikasi.

### G3 — Spesifikasi & kontrak (target D6–D8)
- **Masuk:** G2 disetujui; A-P3-001/002, B-P3-001/002/003, C-P3-001/002, D-P3-001 selesai.
- **Keluar:** kontrak B, C, D, E versi 1.0.0 disetujui; skema CQL disetujui (keputusan skema & partisi); ADR-001/002 disetujui.
- **Penerimaan:** laporan konsistensi X-P3-901 menunjukkan 0 ketidakcocokan field lintas lapisan; setiap tabel ↔ Q-xx; tanpa `ALLOW FILTERING`/counter.
- **Catatan:** ADR-003/004 (deployment, keamanan) boleh disetujui terpisah, paling lambat **D12** (HD-16).

### G4 — Harness (target D6–D8)
- **Masuk:** C-P4-001/004/005, D-P4-001/002/003, A-P4-001/002, B-P4-001 selesai.
- **Keluar:** uji fresh clone oleh anggota bukan pemilik harness: `compose up` sehat, `pre-commit run --all-files` lulus, CI hijau; AGENTS.md lengkap disetujui.

### G5 — ETL + Cassandra (target D12, rencana D14)
- **Masuk:** A-P5-001…010, B-P5-001…007 selesai.
- **Keluar:** periode final termuat di Cassandra; poller incremental berjalan lokal; harness idempotensi lulus; test per Q-xx lulus; ukuran partisi nyata tercatat.
- **Checkpoint D10 (R-14):** bila belum ada data nyata di Cassandra, aktifkan kontingensi ([05 §7](05-project-schedule.md#7-kontingensi-dipicu-di-checkpoint)).

### G6 — Integrasi lokal (target D13, rencana D14)
- **Masuk:** C-P6-001…009, D-P6-001…007/009 selesai; G5 disetujui.
- **Keluar:** checklist mock-to-real ([06 §7](06-interface-contracts.md#7-checklist-mock-to-real)) lengkap; demo internal compose → ingest → dashboard berhasil.

### G7 — Test, eksperimen, cloud (target D19, rencana D18)
- **Masuk:** semua tugas Must P7 selesai; feature freeze (X-P7-901) dipatuhi.
- **Keluar:** idempotensi pada data nyata = 0 selisih; laporan eksperimen bucketing dengan hasil aktual; aplikasi di cloud via HTTPS; port Cassandra tertutup (bukti); poller cloud ≥3 poll berturut-turut; checklist keamanan lulus; 0 bug kritis terbuka.

### G8 — Penerimaan akhir (target D21, rencana D20)
- **Masuk:** semua tugas P8 selesai.
- **Keluar:** 8 kriteria keberhasilan [charter §7](../00-discovery/01-project-charter.md#7-kriteria-keberhasilan-proyek-tingkat-piagam) dicentang dengan bukti; fresh clone oleh anggota lain berhasil; laporan, presentasi, dan video (manusia) siap.

## 3. Definition of Ready & Definition of Done

**Definition of Ready.** Sebuah tugas boleh dimulai hanya bila:
1. ID dan pemilik ada di WBS.
2. Input tersedia, dan dependensi *hard*/*interface*/*human approval* sudah disetujui seorang manusia (`disetujui:` terisi). Dicek dengan `tools/task.py check <ID>`.
3. Output dan path file jelas serta berada di area pemilik.
4. Kriteria penerimaan dapat diuji.
5. Spesifikasi yang relevan sudah disetujui. Untuk tugas implementasi Fase 5–6: G3 dan G4.

**Definition of Done.** Sebuah tugas selesai hanya bila:
1. Implementasi atau dokumen selesai, **hanya** di file milik pemilik.
2. Semua kriteria penerimaan terpenuhi, dengan bukti berupa output perintah di PR.
3. Test otomatis yang relevan lulus di CI (setelah G4).
4. Dokumentasi yang terdampak diperbarui (README komponen, kontrak bila ada CR).
5. Seorang manusia (anggota tim mana pun) menyetujui. Review atau persetujuan dari peran lain **tidak wajib**. Review Codex boleh ditempel sebagai masukan.
6. Persetujuan manusia tercatat bila kolom *human approval* mensyaratkannya.
7. Tidak ada secret, MAP_KEY, atau data mentah di diff.
8. Baris tugas di [13-progress-tracker.md](13-progress-tracker.md) dicentang `[x]` dengan `bukti:` terisi, di PR yang sama (implementer). Tugas **Done** saat seorang manusia mengisi `disetujui:`.

> Tugas **tidak** dianggap Done hanya karena agen sudah membuat filenya atau mencentang barisnya.

## 4. Review kode oleh agen (ringkas)

Satu tugas = satu implementer. Default: Claude Code mengimplementasi, Codex me-review dengan prompt [codex-independent-reviewer](11-role-prompts/codex-independent-reviewer.md). Peran agen boleh dibalik per tugas, tetapi kedua agen tidak pernah mengimplementasi tugas yang sama. Temuan Codex bersifat masukan; keputusan merge tetap pada reviewer manusia.

## 5. Change management

**Wajib CR** untuk perubahan pada: requirements/MVP; canonical event; skema Cassandra; OpenAPI; perilaku UI di UI spec; infrastruktur/arsitektur (ADR); ruang lingkup; dokumen Fase 0.

**Format** `docs/change-requests/CR-xxx.md`:

| Field | Isi |
|---|---|
| ID, tanggal, pengusul | — |
| Alasan | Masalah yang ditemukan, beserta bukti |
| Artefak terdampak | Path + versi kontrak (sebelum → sesudah) |
| Peran terdampak | Pemilik + semua konsumen |
| Dampak dependensi | Task ID yang perlu dikerjakan ulang |
| Dampak test | Test yang berubah atau ditambah |
| Dampak jadwal | Jam PERT tambahan; jalankan ulang `build_plan.py` |
| Status persetujuan | Diusulkan / Disetujui (oleh siapa, tanggal) / Ditolak |

**Aturan:**
- CR besar (major contract, ruang lingkup, skema) disetujui tim.
- CR kecil (minor/patch) cukup disetujui pemilik + semua konsumen.
- Tidak ada perubahan berantai tanpa review: setiap CR turunan adalah CR terpisah.
- Pemilik artefak yang menerapkan perubahan.

**CR yang sudah diusulkan oleh rencana ini:**

| ID | Perubahan | Artefak | Status |
|---|---|---|---|
| CR-01 | Kepemilikan `docs/` dibagi per peran; R4 merakit `docs/08-delivery/` (charter §9 menyebut R4 memiliki seluruh `docs/`) | charter §9 | Disetujui tim 2026-11-19 (HD-04) |
| CR-02 | STATUS.md: koreksi lokasi dokumen Fase 0 (`main`, bukan hanya `docs/phase-0-discovery`); tambah tautan ke rencana eksekusi | STATUS.md | Disetujui tim 2026-11-19 (HD-04), diterapkan |
| CR-03 | Pembaruan register asumsi dari hasil verifikasi Fase 1 (A-P1-005) | 03-assumptions-register | Akan diusulkan di G1 |
| CR-04 | Jadwal charter §10: milestone baru dari 05-project-schedule | charter §10 | Disetujui tim 2026-11-19 (HD-04) |
