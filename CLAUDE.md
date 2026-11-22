# CLAUDE.md

Protokol wajib untuk semua agen ada di AGENTS.md (diimpor di bawah). Ikuti §1 langkah 1–9 di setiap sesi.

@AGENTS.md

## Khusus Claude Code (tambahan; tidak menggantikan AGENTS.md)

- Langkah 1–4 protokol harus selesai sebelum memakai Edit/Write pada file repo.
- Cari ID di dokumen besar dengan Grep. Pakai Read dengan `offset`/`limit` untuk satu bagian. **DILARANG** me-Read file di daftar "DILARANG dibaca utuh" (AGENTS.md §2).
- **DILARANG** memakai subagent untuk "membaca semua dokumen". Subagent hanya dipakai bila manusia memintanya.
- Satu worktree per tugas, dengan perintah dari `task.py check`. Jangan menjalankan `git checkout`/`switch` di working directory utama bila ada proses atau agen lain yang memakainya.
- Auto-memory bukan sumber kebenaran. Verifikasi dengan `docs/STATUS.md` dan `task.py` sebelum bertindak.
