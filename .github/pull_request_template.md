## Task ID
<!-- Contoh: C-P4-001 -->

## Ringkasan
<!-- Apa yang berubah dan mengapa, 1–3 kalimat. -->

## File yang diubah
<!-- Semua harus di area pemilik tugas. File di luar area: jelaskan alasannya dan siapa pemiliknya. -->

## Kriteria penerimaan & bukti
<!-- Tempel OUTPUT PERSIS perintah verifikasi (task.py scope, build_plan.py, test, dll.). Jangan diringkas dari ingatan. -->

```
```

## Test yang dijalankan
<!-- Perintah + hasil. "Tidak ada" bila tugas dokumen. -->

## Dampak kontrak
- [ ] Tidak ada
- [ ] Ada, CR: <!-- CR-xx -->

## Review agen (Codex)
<!-- Opsional: tempel masukan. -->

## Checklist Definition of Done
Sumber: [10-phase-gates §3](../docs/10-execution-plan/10-phase-gates.md#3-definition-of-ready--definition-of-done)

- [ ] Implementasi/dokumen selesai, hanya di file milik pemilik (atau pengecualian dijelaskan di atas)
- [ ] Semua kriteria penerimaan terpenuhi, dengan bukti berupa output perintah di atas
- [ ] Test otomatis yang relevan lulus di CI (berlaku setelah G4)
- [ ] Dokumentasi terdampak diperbarui (README komponen, kontrak bila ada CR)
- [ ] Persetujuan manusia dicatat bila tugas mensyaratkannya (kolom *human approval*)
- [ ] Tidak ada secret, `FIRMS_MAP_KEY`, `.env`, atau data mentah di diff
- [ ] Baris tugas di `13-progress-tracker.md` dicentang `[x]` dengan `bukti:` di PR ini
- [ ] `disetujui:` TIDAK diisi oleh implementer; diisi seorang manusia setelah review
