# AGENTS.md — Instruksi Bersama untuk Semua Agen AI

> Berlaku untuk semua agen AI di repo ini (OpenAI Codex, Claude Code, dan agen lain).
> Versi lengkap (coding standards, branching, Definition of Done, protokol kolaborasi agen) akan disusun di **Fase 4**. Sampai saat itu, aturan minimum di bawah ini yang berlaku.

## WAJIB: mulai dari `docs/STATUS.md`

Sebelum melakukan apa pun di setiap sesi baru:

1. **Baca [`docs/STATUS.md`](docs/STATUS.md)** untuk mengetahui fase aktif, keputusan yang sudah disetujui, fakta terverifikasi, hal terbuka, dan aturan kerja.
2. Ikuti tautan di STATUS.md ke dokumen sumber kebenaran yang relevan dengan tugas (register di `docs/00-discovery/`, dst.).
3. Periksa `git status` dan branch aktif.

Jika STATUS.md bertentangan dengan dokumen yang dirujuknya, **dokumen yang dirujuk yang berlaku**. Laporkan konflik itu kepada manusia.

## Aturan minimum

- Kerjakan **hanya fase/tugas yang diminta manusia**. Di akhir fase: STOP dan tunggu persetujuan.
- Jangan mengubah keputusan yang sudah disetujui tanpa persetujuan manusia.
- Jangan mengarang data, statistik, kapabilitas API, atau hasil test/benchmark. Tandai informasi yang belum diverifikasi.
- **Jangan pernah** mencetak, men-commit, atau menyalin isi `.env` (berisi `FIRMS_MAP_KEY`).
- Commit/push hanya bila diminta. Jangan mengedit file yang sedang dikerjakan agen lain.
- Perbarui `docs/STATUS.md` setiap kali sebuah gerbang fase dilewati atau ada keputusan baru.
- **Catat progres setiap tugas** di [`docs/10-execution-plan/13-progress-tracker.md`](docs/10-execution-plan/13-progress-tracker.md). Saat tugas selesai, ubah baris task ID-mu dari `- [ ]` menjadi `- [x]` dan isi `bukti:` (PR/commit + tanggal), di commit yang sama. Jangan pernah mengisi `disetujui:`; kolom itu hanya untuk reviewer manusia. Lalu jalankan `python -I docs/10-execution-plan/tools/build_plan.py` (harus `ISSUES: 0`).
- Dokumentasi dalam bahasa Indonesia; identifier kode, path API, dan konvensi teknis dalam bahasa Inggris.
