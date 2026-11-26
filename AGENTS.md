# AGENTS.md — Protokol Wajib Agen AI

> Berlaku untuk **SEMUA** agen AI di repo ini (Claude Code, OpenAI Codex, dan agen apa pun), di **setiap sesi**, tanpa kecuali.
> Kata **WAJIB** dan **DILARANG** bersifat mutlak. Jika sebuah aturan tidak bisa dipatuhi: **STOP dan tanya manusia**. Jangan mencari jalan pintas.
> Coding standards per bahasa ditambahkan di tugas D-P4-003 (Fase 4). Protokol di bawah sudah berlaku sekarang.

## 1. Protokol sesi (WAJIB, berurutan, tidak boleh dilompati)

`T` = `python -I docs/10-execution-plan/tools/task.py` (read-only, tanpa API, membaca graf dependensi + tracker).

| # | Langkah | Perintah / bacaan | Lanjut hanya bila |
|---|---|---|---|
| 1 | Orientasi | Baca file ini dan [`docs/STATUS.md`](docs/STATUS.md). Jalankan `git status` dan `git branch --show-current`. | Working tree bersih atau perubahannya jelas milik tugasmu |
| 2 | Brief | `T brief --role <A\|B\|C\|D>`, yaitu peran manusia yang kamu bantu. Tanya bila belum tahu. | — |
| 3 | Pilih tugas | Manusia menyebut task ID → pakai itu. Tidak menyebut → usulkan **satu** tugas dari baris `USULAN`/`SIAP` di brief, lalu **tunggu konfirmasi**. **DILARANG** memilih sendiri lalu langsung bekerja. | Manusia mengonfirmasi task ID |
| 4 | Cek kesiapan (DoR) | `T check <ID>`: kartu tugas + status setiap dependensi dari graf | Exit `0` |
| 5 | Isolasi | `git worktree add .claude/worktrees/<ID> -b <peran>/<ID>-<slug>`, dijalankan dari checkout utama; worktree **WAJIB** di dalam repo (§3 aturan 7). Perintahnya dicetak oleh `check`. | Bekerja hanya di worktree itu |
| 6 | Kerjakan | Hanya **File tugas** di kartu. Kriteria penerimaan tidak boleh dilonggarkan. | — |
| 7 | Cek lingkup | `T scope <ID> --base <branch asal>` | Exit `0` |
| 8 | Catat progres | Di [13-progress-tracker.md](docs/10-execution-plan/13-progress-tracker.md), baris `<ID>` saja: `[x]` + `bukti:` bila semua kriteria terpenuhi. Bila belum, tetap `[ ]` dan tulis keadaannya di `bukti:`. Lalu `python -I docs/10-execution-plan/tools/build_plan.py`. | `ISSUES: 0` |
| 9 | Lapor & STOP | Format laporan di prompt peran. Commit/push/PR hanya bila diminta. | Tunggu manusia |

**Exit code `task.py`:** `0` lanjut · `1` **STOP** (terblokir, file di luar area, atau tugas sudah punya branch lain); laporkan ke manusia apa adanya · `2` **jangan dikerjakan** (selesai, menunggu persetujuan, atau tugas manusia saja) · `3` rencana tidak sinkron; jalankan `build_plan.py` lalu ulangi.

**Status di graf dan tracker:** ✅ selesai · ⏳ menunggu persetujuan · 🔧 berjalan · ▶ siap · ⛔ terblokir. **Selesai (✅) = seorang manusia, anggota tim mana pun, mengisi `disetujui:` di tracker.** Tidak ada review atau persetujuan wajib dari peran lain. Dependensi **Hard / Interface / Human approval** wajib ✅ sebelum mulai; **Soft** tidak memblokir (catat asumsinya di PR). Tugas terblokir hanya boleh dimulai bila manusia mengizinkan secara eksplisit; kutip izinnya (siapa, kapan) di PR.

**Sesi tanpa tugas.** Pertanyaan, penjelasan, dan pemeriksaan read-only cukup langkah 1. Perintah git/administratif yang diminta manusia secara eksplisit (merge, push, branch) dijalankan persis seperti diminta. **Setiap perubahan file WAJIB punya task ID yang lolos langkah 4**, kecuali manusia secara eksplisit menyebut file yang harus diubah. Dalam hal itu, tulis di laporan bahwa perubahannya di luar WBS.

## 2. Anggaran baca (WAJIB hemat)

Baca **hanya** yang dibutuhkan langkah saat ini. `task.py` menggantikan pembacaan file rencana yang besar.

| Kapan | Baca | Jangan |
|---|---|---|
| Setiap sesi | `AGENTS.md`, `docs/STATUS.md`, output `brief` | — |
| Setelah tugas dipilih | Output `check <ID>`; prompt perannya di [`11-role-prompts/`](docs/10-execution-plan/11-role-prompts/) (sekali per sesi); file di kolom **Input** dan **Spesifikasi** kartu | Dokumen lain "untuk jaga-jaga" |
| Butuh satu fakta/keputusan (`OQ-xx`, `A-xx`, `R-xx`, `HD-xx`, `CR-xx`) | Cari ID-nya (grep) dan baca bagian itu saja | Membaca register utuh |
| Butuh kontrak | Bagian peran terkait di [`06-interface-contracts.md`](docs/10-execution-plan/06-interface-contracts.md) | Seluruh folder `docs/10-execution-plan/` |

**DILARANG dibaca utuh** (pakai `task.py`, atau grep task ID): `02-work-breakdown-structure.md` (±151 KB), `02-work-breakdown-structure.csv` (±186 KB), `03-dependency-matrix.md`, `04-dependency-graph.mmd`, `05-project-schedule.md`. **DILARANG** memuat isi `data/` (data mentah) atau `.env` ke konteks. `docs/00-discovery/` hanya lewat pencarian ID.
Jika STATUS.md dan kartu tugas tidak cukup untuk memutuskan, **tanya manusia**, jangan membaca lebih banyak secara acak.

## 3. Aturan file (DILARANG mengubah file sembarangan)

1. Ubah hanya **File tugas** dari kartu `check`. File lain di area peran hanya bila perlu, dengan alasan di PR. File di luar area peran **DILARANG**: ajukan CR ([10 §5](docs/10-execution-plan/10-phase-gates.md#5-change-management)) atau minta pemiliknya ([07](docs/10-execution-plan/07-file-ownership-matrix.md)). `T scope` menegakkan aturan ini.
2. `docs/00-discovery/` beku; perubahan hanya lewat CR. File hasil generator (`02`, `03`, `04`, `05` di `docs/10-execution-plan/`) **DILARANG** diedit manual. Ubah `TASKS` di `tools/build_plan.py` (koordinator), lalu jalankan ulang.
3. Di `13-progress-tracker.md`, ubah hanya baris task ID-mu. **DILARANG** mengisi `disetujui:`, kecuali untuk mencatat persetujuan yang dinyatakan langsung oleh manusia (siapa, kapan, di mana). **DILARANG** mencentang tugas *manusia saja*.
4. Satu tugas = satu branch = satu implementer. Jika `check` melaporkan branch lain untuk tugas itu: STOP. **DILARANG** menulis di worktree agen lain atau mengganti branch di working directory yang sedang dipakai orang/agen lain.
5. Konflik merge di `13-progress-tracker.md`: pertahankan kedua sisi (setiap baris milik satu tugas). Konflik di `04-dependency-graph.mmd`: jangan diselesaikan manual; jalankan ulang `build_plan.py`.
6. Lihat isi file sebelum menghapus atau menimpanya. Operasi destruktif (hapus data, reset, force push, menghentikan proses orang lain) wajib persetujuan eksplisit.
7. **Lokasi worktree.** Setiap worktree **WAJIB** dibuat di `<root repo apiwowok>/.claude/worktrees/<nama>` (folder ini diabaikan Git). **DILARANG** membuat worktree di luar direktori repo (mis. `../apiwowok-<ID>`, `D:\...\apiwowok-<ID>`). Bila `git worktree list` menunjukkan worktree di luar `.claude/worktrees/`, jangan dipakai untuk tugas baru; laporkan ke manusia. Claude Code: pakai `EnterWorktree` dengan `name` (otomatis ke folder itu); `path` hanya untuk worktree yang sudah ada di folder itu.

## 4. Data, rahasia, integritas

- **DILARANG** membaca ke output, mencetak, men-commit, atau menyalin isi `.env` (berisi `FIRMS_MAP_KEY`) ke dokumen, log, URL, atau pesan.
- **DILARANG** mengarang data, statistik, kapabilitas API, atau hasil test/benchmark. Setiap angka harus berasal dari perintah yang benar-benar dijalankan. Beri label sesuai [legenda](docs/00-discovery/README.md#label-status-informasi) (`VERIFIED` / `ASSUMPTION` / `UNKNOWN` / …).
- Hotspot ≠ kebakaran terkonfirmasi. Jangan membandingkan jumlah deteksi antar sensor.
- API FIRMS hanya dipanggil bila tugas memintanya dan manusia mengizinkan; tidak pernah dari test atau CI.

## 5. Keputusan & git

- Kerjakan hanya fase/tugas yang diminta. Di akhir tugas atau fase: STOP dan tunggu persetujuan.
- Keputusan di daftar [STATUS §2 butir 4](docs/STATUS.md#2-aturan-kerja-wajib) (lingkup, produk, periode, kualitas data, skema, partisi, arsitektur, keamanan, …) hanya diambil manusia. Agen menyusun opsi → rekomendasi → bukti, lalu menunggu.
- Keputusan yang sudah disetujui hanya berubah lewat CR.
- Commit/push/PR/merge hanya bila diminta. Nama branch `<peran>/<ID>-<slug>`. Commit kecil, satu tujuan, pesan bahasa Inggris (`docs:`, `feat:`, `fix:`, …). **DILARANG** commit `.env` atau `data/`.
- `docs/STATUS.md` diperbarui (oleh koordinator) setiap kali gerbang dilewati atau ada keputusan baru.
- Dokumentasi berbahasa Indonesia; identifier kode, path API, dan konvensi teknis berbahasa Inggris.

## 6. STOP dan tanya manusia bila

- `check` atau `scope` keluar dengan kode ≠ 0 dan tidak bisa diperbaiki di area sendiri.
- Permintaan tidak cocok dengan task ID mana pun, atau cocok dengan beberapa task ID.
- Butuh keputusan kebijakan, perubahan kontrak, file di luar area, dependensi baru, atau operasi destruktif.
- Dokumen saling bertentangan. Dokumen sumber yang dirujuk mengalahkan `STATUS.md`, dan keduanya mengalahkan ingatan agen. Laporkan konfliknya.
- Ada perubahan asing di working tree, atau branch berganti tanpa sepengetahuanmu.
