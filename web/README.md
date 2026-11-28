# web — Dashboard NusaFire (React + TypeScript + Leaflet)

Kerangka frontend (tugas D-P4-001, Role D). Saat ini hanya menampilkan **peta dasar statis dengan atribusi**. Data deteksi, filter, dan disclaimer final ditambahkan di Fase 6 setelah kontrak API (`openapi.yaml`) disetujui.

## Perintah

| Perintah                                  | Fungsi                                                         |
| ----------------------------------------- | -------------------------------------------------------------- |
| `npm install`                             | Pasang dependensi (diuji dengan Node.js v24.14.1, npm 11.11.0) |
| `npm run dev`                             | Jalankan server pengembangan (Vite)                            |
| `npm run lint`                            | ESLint (TypeScript + React hooks)                              |
| `npm test`                                | Vitest (jsdom + Testing Library)                               |
| `npm run build`                           | Cek tipe (`tsc -b`) dan build produksi ke `dist/`              |
| `npm run format` / `npm run format:check` | Prettier                                                       |

Kriteria penerimaan tugas: `npm run lint && npm test && npm run build` harus lulus.

## Keputusan yang dipakai

- **HD-14:** TypeScript + Vitest; Playwright untuk E2E menyusul di D-P7-001. Library chart dipilih di ADR-001 (belum diputuskan), jadi **belum ada library chart** di sini.
- **Basemap:** tile OpenStreetMap standar sebagai penyedia **sementara** (`ASSUMPTION`, lihat `src/constants.ts`). Penyedia final dan kebijakan pemakaian tile diputuskan tim sebelum aplikasi dipublikasikan.
- **Atribusi (FR-G5):** atribusi basemap sudah tampil. Atribusi NASA FIRMS dan BIG ditambahkan bersama lapisan datanya.

## Aturan

- Teks UI berbahasa Indonesia (OQ-20); pakai istilah "deteksi hotspot", tidak pernah "kebakaran" (FR-G1).
- Jangan membaca atau menulis `.env`; jangan menaruh kunci API di kode frontend.
