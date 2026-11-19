# 07 — Catatan Spesifikasi Minimum: Eksperimen Cassandra 3 Node di Laptop

Status: **DRAFT** (2026-11-19). Keputusan tim: eksperimen 3 node **boleh** dijalankan di laptop. Dokumen ini menetapkan spesifikasi minimum dan cara memverifikasinya.

> Penting: dokumentasi resmi Cassandra **tidak** memberikan spesifikasi minimum untuk cluster pengembangan multi-node di satu mesin. Angka di bawah adalah **estimasi rekayasa** (`ASSUMPTION`). Angka ini wajib dibuktikan dengan *smoke test* (§4) sebelum eksperimen dijalankan. Hasil pengukuran nyata menggantikan estimasi ini.

## 1. Fakta dari sumber resmi (`VERIFIED`, dibaca 2026-11-19)

| Sumber | Fakta |
|---|---|
| Cassandra docs — *Hardware choices* | Cassandra dapat dijalankan di server kecil untuk testing/pengembangan, tetapi tidak ada angka minimum untuk dev. Server produksi minimal: **2 core dan 8 GB RAM** per node. Heap disarankan **tidak kurang dari 2 GB dan tidak lebih dari 50% RAM sistem**. Selain heap, Cassandra memakai memori off-heap dan page cache OS. |
| Cassandra docs — *cassandra-env.sh* | Opsi `cassandra.available_processors` tersedia karena pada deployment multi-instance setiap instance menganggap semua CPU tersedia untuknya. |
| Docker Hub — image resmi `cassandra` | Tag yang tersedia: `5.0.x`, `4.1.x`, `4.0.x`, juga `6.0-alpha`. Multi-node memakai `CASSANDRA_SEEDS` dan `CASSANDRA_CLUSTER_NAME` (harus sama di semua node). Halaman ini **tidak** mendokumentasikan pengaturan memori/heap. Ada peringatan bahwa container belum menerima koneksi sampai inisialisasi selesai, dan hal ini dapat bermasalah dengan Docker Compose yang menjalankan beberapa container bersamaan. |
| Microsoft Learn — `.wslconfig` | Default WSL2: memori **50% RAM Windows**, prosesor = semua logical processor, swap 25% RAM. Diatur di `%UserProfile%\.wslconfig` bagian `[wsl2]`. Perubahan berlaku setelah `wsl --shutdown`. |

## 2. Spesifikasi laptop untuk eksperimen 3 node

| Komponen | **Minimum** | Disarankan | Keterangan |
|---|---|---|---|
| RAM total | **16 GB** | 32 GB | Laptop 8 GB **tidak didukung** untuk 3 node (default WSL2 hanya 4 GB). Laptop 8 GB cukup untuk single-node. |
| Memori untuk Docker/WSL2 | **≥ 8 GB** dialokasikan | 12–16 GB | Pada laptop 16 GB, default WSL2 (50%) = 8 GB, tepat di batas minimum. |
| CPU | **4 core fisik** (≈8 thread) | 6–8 core | CPU dibatasi per node agar ketiga node tidak saling berebut CPU (§3). |
| Disk | **SSD, ≥ 20 GB kosong** | ≥ 40 GB | Untuk image, tiga volume data, dan dataset eksperimen. Ukuran nyata bergantung pada volume data hasil Fase 1. |
| Software | Docker Desktop (Windows/macOS) atau Docker Engine (Linux) dengan Docker Compose v2 | — | Di Windows: backend WSL2. |
| Kondisi saat eksperimen | Aplikasi berat lain ditutup (browser dengan banyak tab, IDE besar, game) | — | Mengurangi noise benchmark (R-16). |

Mengapa minimum 16 GB (estimasi, `ASSUMPTION`):
- Heap per node untuk eksperimen diperkecil ke sekitar **1 GB**. Ini **sengaja di bawah** panduan produksi (≥ 2 GB) dan harus dicatat sebagai keterbatasan eksperimen.
- Total memori per container diperkirakan **±1,5–2 GB** (heap + off-heap + overhead JVM), sehingga 3 node membutuhkan **±4,5–6 GB**.
- Ditambah overhead VM Docker/WSL2 serta Windows dan aplikasi lain, laptop 16 GB dengan alokasi WSL2 8 GB adalah batas bawah yang masuk akal.

## 3. Aturan konfigurasi eksperimen (dirinci di Fase 4/7)

1. **Heap per node dibatasi secara eksplisit.** Mekanismenya (mis. variabel environment yang dibaca `cassandra-env.sh`, atau file opsi JVM) **belum diverifikasi** untuk versi image yang dipilih. Hal ini diperiksa di Fase 4 dengan membaca file konfigurasi di dalam image.
2. **Batas memori dan CPU per container** di Docker Compose, plus `cassandra.available_processors` per node.
3. **Node dinyalakan berurutan.** Node 2 baru start setelah node 1 sehat; node 3 setelah node 2. Gunakan healthcheck + `depends_on: condition: service_healthy`, sesuai peringatan di halaman image resmi.
4. **Cluster 3 node adalah profil Compose terpisah**, bukan stack pengembangan harian. Pengembangan harian tetap single-node.
5. Spesifikasi laptop, versi image, alokasi WSL2, heap, dan batas container **dicatat di setiap laporan eksperimen**. Hasil dari laptop tidak boleh dibandingkan langsung dengan hasil dari cloud.

## 4. Smoke test kelayakan (wajib sebelum eksperimen)

Laptop dinyatakan layak bila semua butir terpenuhi:

- [ ] Ketiga node berstatus `UN` (Up/Normal) pada `nodetool status`.
- [ ] Penggunaan memori total ketiga container (`docker stats`) tetap di bawah alokasi WSL2/Docker, dengan sisa ruang ≥ 1 GB.
- [ ] Cluster stabil ≥ 10 menit di bawah beban tulis sampel, tanpa container di-restart atau di-*OOM-kill*.
- [ ] Mematikan satu node lalu menyalakannya kembali berhasil; node kembali `UN`.

Jika smoke test gagal pada konfigurasi minimum:
1. Kurangi beban data eksperimen.
2. Jalankan di laptop anggota lain yang lebih besar.
3. Gunakan cluster cloud berumur pendek (OQ-23/OQ-24).
4. Jika tetap tidak memungkinkan, jadikan eksperimen replikasi *Could* dan nyatakan sebagai keterbatasan.

## 5. Contoh pengaturan WSL2 (Windows, laptop 16 GB)

File `%UserProfile%\.wslconfig` (default-nya tidak ada):

```ini
[wsl2]
memory=10GB
processors=6
```

Setelah menyimpan file, jalankan `wsl --shutdown` lalu buka ulang Docker Desktop. Angka di atas adalah contoh; sesuaikan dengan laptop. Sisakan cukup memori untuk Windows.
