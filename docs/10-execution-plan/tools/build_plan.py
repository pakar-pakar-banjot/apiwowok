"""NusaFire execution plan generator (planning tool, not application code).

Single source of truth for the Work Breakdown Structure (TASKS below).
Generates: 02-work-breakdown-structure.csv/.md, 03-dependency-matrix.md,
04-dependency-graph.mmd, 05-project-schedule.md, and runs consistency checks.

Usage:  python -I docs/10-execution-plan/tools/build_plan.py [--coord A|B|C|D]
Edit TASKS here, then regenerate. Do not hand-edit generated files.
Stdlib only.
"""
import csv, math, os, re, sys, pathlib, datetime as dt, collections

OUT = pathlib.Path(__file__).resolve().parents[1]
D1 = dt.date(2026, 11, 19)                 # A-22 (ASSUMPTION)
HOURS_PER_DAY = {"A": 4, "B": 4, "C": 4, "D": 4}   # OQ-03; confirm per member (HD-03)
LAST_DAY = 21
START_HOUR = 4                              # planning starts at D2 (D1 already used)
COORD = "B"                                 # RECOMMENDATION, see HD-02; override with --coord
if "--hours" in sys.argv:  # scenario only; generated files must use the default
    HOURS_PER_DAY = {r: float(sys.argv[sys.argv.index("--hours") + 1]) for r in HOURS_PER_DAY}
if "--coord" in sys.argv:
    COORD = sys.argv[sys.argv.index("--coord") + 1]
# HD-07 (b), approved at GATE-EP 2026-11-19: critical-chain members R1 and R3 work ~5 h/day on D9–D15
CAP_OVERRIDE = {} if ("--hours" in sys.argv or "--no-boost" in sys.argv) else \
    {(r, d): 5 for r in ("A", "C") for d in range(9, 16)}
SCENARIO = any(f in sys.argv for f in ("--hours", "--coord", "--no-boost"))  # scenario runs print only; no file is written


def hours_on(r, d):
    return CAP_OVERRIDE.get((r, d), HOURS_PER_DAY[r])


def advance(r, s, work):
    """Calendar time (4 slot-hours = 1 day) at which `work` person-hours started at slot `s` finish for role r."""
    while work > 1e-9:
        d = int(s // 4) + 1
        rate = hours_on(r, d) / 4
        room = (d * 4 - s) * rate
        if work <= room + 1e-9:
            return s + work / rate
        work -= room; s = d * 4
    return s


def wr(path, text):
    if not SCENARIO:
        path.write_text(text, encoding="utf-8")

ROLE = {
    "A": ("R1", "Data Engineering / ETL"),
    "B": ("R2", "Cassandra & Data Platform"),
    "C": ("R3", "Backend, Integration & DevOps"),
    "D": ("R4", "Frontend, Visualization & Delivery"),
}
ROLE_DIRS = {
    "A": ["pipeline/", "docs/01-dataset/", "docs/03-specs/data/", "docs/08-delivery/data.md", "scratch/phase1/", "data/ (lokal)",
          "ruff.toml", ".pre-commit-config.yaml"],
    "B": ["db/", "experiments/", "docs/03-specs/database/", "docs/08-delivery/database.md"],
    "C": ["api/", "deploy/", "docker-compose*.yml", ".github/", ".env.example", ".gitignore",
          "README.md", "docs/03-specs/api/", "docs/03-specs/architecture/",
          "docs/02-requirements/02-non-functional-requirements.md", "docs/08-delivery/api-deploy.md"],
    "D": ["web/", "AGENTS.md", "CLAUDE.md", "docs/02-requirements/ (kecuali file NFR)", "docs/03-specs/ui/", "docs/08-delivery/ (index, ui, acceptance, demo)"],
}
COORD_DIRS = ["docs/STATUS.md", "docs/10-execution-plan/", "docs/03-specs/README.md", "docs/change-requests/"]
ALWAYS_PROHIBITED = [".env", "docs/00-discovery/ (hanya lewat change request)"]
DEFAULT_REVIEWER = {"A": "B", "B": "A", "C": "D", "D": "C"}
DEP_TYPES = {"H": "Hard", "S": "Soft", "I": "Interface", "R": "Review", "HA": "Human approval"}
PHASES = {
    "P1": "Dataset Feasibility", "P2": "Requirements Engineering", "P3": "Architecture & Technical Specs",
    "P4": "Development Harness", "P5": "ETL & Cassandra Implementation", "P6": "Backend & Frontend Implementation",
    "P7": "Integration, Testing & Experiments", "P8": "Documentation & Final Delivery",
}
GATES = {  # gate id -> (phase, description)
    "GATE-EP": ("P1", "Persetujuan rencana eksekusi (dokumen ini) + penetapan anggota/peran"),
    "GATE-G1": ("P1", "G1 — dataset, periode (OQ-05), batas provinsi (OQ-07), aturan NRT/SP, aturan DQ"),
    "GATE-G2": ("P2", "G2 — requirements, NFR, semantik data, MVP terkunci"),
    "GATE-G3": ("P3", "G3 — kontrak canonical event, access patterns, model data, OpenAPI, UI spec, ADR"),
    "GATE-G4": ("P4", "G4 — harness: repo, AGENTS.md, Compose, CI hijau"),
    "GATE-G5": ("P5", "G5 — ETL dua mode + Cassandra berisi data nyata, test DB & ETL lulus"),
    "GATE-G6": ("P6", "G6 — API + dashboard berjalan di data nyata secara lokal (integrasi lokal pertama)"),
    "GATE-G7": ("P7", "G7 — test, idempotensi, eksperimen, deploy cloud, feature freeze dipatuhi"),
    "GATE-G8": ("P8", "G8 — dokumentasi teknis final, checklist penerimaan"),
}
GATE_DEPS = {}
TASKS = []


def t(id, title, est, deps="", rev=None, prio="Must", status="Belum mulai", collab="", obj="", why="", inputs="",
      outputs="", files="", steps=(), spec="", ac="", verify="", evidence="", approval="Tidak (review PR cukup)",
      handoff="", legacy="", nb=None, agent="Claude Code implementasi; Codex review"):
    TASKS.append(dict(id=id, title=title, est=est, deps=deps, rev=rev, prio=prio, status=status, collab=collab, obj=obj,
                      why=why, inputs=inputs, outputs=outputs, files=files, steps=list(steps), spec=spec, ac=ac,
                      verify=verify, evidence=evidence, approval=approval, handoff=handoff, legacy=legacy, nb=nb,
                      agent=agent))


def gate(gid, deps):
    GATE_DEPS[gid] = deps


X = "X"  # coordinator placeholder, resolved to COORD

# ---------------------------------------------------------------- PHASE 1
t("A-P1-001", "Review inventaris sumber FIRMS", (0.5, 1, 1.5), legacy="P1-01", status="Draf selesai (agen) — menunggu review",
  obj="Memastikan inventaris sumber, mekanisme akses, kuota, dan atribusi akurat.", why="Semua desain ekstraksi bergantung pada fakta akses FIRMS.",
  inputs="docs/01-dataset/01-source-inventory.md", outputs="Inventaris sumber tervalidasi", files="docs/01-dataset/01-source-inventory.md",
  steps=["Baca draf", "Cocokkan tiap klaim VERIFIED dengan sumber yang dirujuk", "Catat koreksi di PR"],
  spec="Label status per klaim (legenda Fase 0)", ac="Keempat source ID tercatat dengan rentang tanggal, biaya transaksi terukur, dan atribusi; tidak ada MAP_KEY di dokumen.",
  verify="grep pola MAP_KEY (32 hex) di docs/ → 0 hasil", approval="G1")
t("A-P1-002", "Unduh sampel nyata + checksum", (0.5, 1, 2), legacy="P1-02", status="Unduhan selesai (agen) — menunggu verifikasi checksum",
  obj="Menyimpan respons mentah FIRMS untuk periode kandidat beserta checksum.", why="Raw zone membuat profiling dan ETL bisa diulang tanpa memanggil API (R-04, R-20).",
  inputs="MAP_KEY di .env; rencana unduh di scratch/phase1/download.py", outputs="data/firms/raw/**, data/firms/manifest.csv",
  files="scratch/phase1/download.py, data/firms/", steps=["Tunggu unduhan selesai", "Hitung ulang SHA-256 dan cocokkan dengan manifest", "Catat request gagal (harus 0)"],
  spec="Area API, bbox 94,-11.5,141.5,6.5, DAY_RANGE 5", ac="Setiap file punya baris manifest dengan SHA-256 yang cocok; 0 request gagal; log tanpa MAP_KEY.",
  verify="Skrip verifikasi checksum (sha256 ulang vs manifest)", evidence="Output verifikasi checksum", approval="Tidak")
t("A-P1-003", "Data dictionary dari header & nilai nyata", (1, 1.5, 2.5), "A-P1-002:H", legacy="P1-03",
  obj="Mendokumentasikan setiap kolom per sumber dari data nyata.", why="Kontrak canonical event (A-P3-001) diturunkan dari sini.",
  inputs="data/firms/raw/**; halaman atribut resmi FIRMS", outputs="docs/01-dataset/02-data-dictionary.md", files="docs/01-dataset/02-data-dictionary.md",
  steps=["Kumpulkan header per sumber", "Isi tipe, contoh, rentang terukur, null, arti resmi + URL", "Tandai perbedaan SP vs NRT dan N20 vs N21"],
  spec="Satu baris per kolom per sumber; label VERIFIED/UNKNOWN", ac="Semua kolom di semua header tercakup; perbedaan `type` dan `version` antar produk tercatat dengan angka.",
  verify="Skrip membandingkan daftar kolom dokumen vs header file → selisih 0", approval="G1")
t("A-P1-004", "Laporan profiling dataset", (1, 2, 3), "A-P1-002:H, A-P1-006:S", legacy="P1-04", collab="B",
  obj="Mengukur baris, null, nilai di luar rentang, duplikat, cakupan temporal & geografis.", why="Aturan DQ, partisi, dan NFR membutuhkan angka nyata.",
  inputs="data/firms/raw/**, coord_assign.csv", outputs="docs/01-dataset/03-profiling-report.md, data/firms/profile/*", files="docs/01-dataset/03-profiling-report.md, scratch/phase1/profile_firms.py",
  steps=["Jalankan pip_assign.py lalu profile_firms.py", "Bandingkan hari kosong dengan tabel missing_data FIRMS", "Tulis laporan dengan angka hasil ukur saja"],
  spec="Minimal 2 kandidat natural key untuk analisis duplikat", ac="Setiap angka di laporan dapat ditelusuri ke file profil; hari kosong dijelaskan atau ditandai UNKNOWN.",
  verify="Jalankan ulang skrip → hash profile.json identik (deterministik)", evidence="Hash profile.json dua kali run", approval="G1")
t("A-P1-005", "Verifikasi asumsi AI-PRIOR A-06–A-09", (0.5, 1, 1.5), "A-P1-003:H", legacy="P1-05",
  obj="Menguji zona waktu acq_time, format confidence, field version dan type.", why="Asumsi salah merusak logika waktu dan dedup (R-03, R-07).",
  inputs="Data dictionary, dokumentasi atribut FIRMS", outputs="Tabel verifikasi A-05–A-09 + usulan pembaruan register (sebagai CR)",
  files="docs/01-dataset/02-data-dictionary.md (bagian verifikasi)", steps=["Uji tiap asumsi dengan data", "Kutip sumber resmi", "Tulis usulan CR untuk register Fase 0"],
  spec="Register Fase 0 tidak diedit langsung", ac="Setiap asumsi berstatus VALIDATED/INVALIDATED dengan bukti.", verify="Review manual", approval="G1")
t("A-P1-006", "Review evaluasi sumber batas provinsi", (0.5, 1, 1.5), legacy="P1-06", status="Draf selesai (agen) — menunggu review",
  obj="Memvalidasi rekomendasi BIG edisi Juni 2026 (38 provinsi).", why="OQ-07; batas 34 provinsi merusak ranking Papua.",
  inputs="docs/01-dataset/05-boundary-sources.md", outputs="Rekomendasi sumber batas tervalidasi", files="docs/01-dataset/05-boundary-sources.md",
  steps=["Cek jumlah provinsi dan edisi", "Nilai risiko lisensi", "Siapkan keputusan HD-08"], spec="Kriteria OQ-07",
  ac="Rekomendasi menyatakan lisensi UNKNOWN secara eksplisit beserta cadangan.", verify="Review manual", approval="G1 (OQ-07, HD-08)")
t("A-P1-007", "Perbandingan NRT vs SP + aturan tumpang tindih", (1, 1.5, 2.5), "A-P1-002:H", legacy="P1-09, P1-11", collab="B",
  obj="Membandingkan NOAA-21 NRT vs SP pada tanggal yang sama dan mengusulkan aturan presedensi.", why="Kunci dedup lintas sumber (R-06, C-15).",
  inputs="data/firms/raw/VIIRS_NOAA21_*", outputs="docs/01-dataset/04-nrt-vs-sp-and-latency.md (bagian perbandingan)",
  files="docs/01-dataset/04-nrt-vs-sp-and-latency.md, scratch/phase1/compare_nrt_sp.py",
  steps=["Jalankan compare_nrt_sp.py", "Ukur jarak posisi, selisih waktu, FRP, confidence", "Usulkan aturan: SP menggantikan NRT per tanggal"],
  spec="Aturan pencocokan tertulis (toleransi waktu & jarak)", ac="Proporsi match/unmatched dan sebaran selisih dilaporkan; aturan backfill diusulkan.",
  verify="Skrip deterministik", approval="G1 (P1-09)")
t("A-P1-008", "Pengamatan latensi NRT", (0.5, 1, 1.5), "A-P1-002:S", legacy="P1-10", status="Berjalan (poller 24 jam)",
  obj="Mengukur kapan data NRT muncul relatif terhadap acq_time dan apakah rekaman berubah.", why="Masukan interval polling (A-26, NFR).",
  inputs="data/firms/latency/*", outputs="docs/01-dataset/04-nrt-vs-sp-and-latency.md (bagian latensi)", files="scratch/phase1/latency_poller.py",
  steps=["Analisis observations.csv", "Hitung sebaran first_seen − acq_time", "Rekomendasikan interval polling"],
  spec="Hasil sementara ditandai PENDING bila < 24 jam", ac="Sebaran latensi dan jumlah rekaman berubah dilaporkan dengan periode pengamatan.",
  verify="Review manual", approval="Tidak (masukan G2)")
t("A-P1-009", "Aturan kualitas data awal", (1, 2, 3), "A-P1-004:H", legacy="—",
  obj="Menetapkan aturan validasi, penolakan, dan penandaan berbasis profil nyata.", why="Kebijakan kualitas data wajib disetujui manusia.",
  inputs="Laporan profiling", outputs="docs/01-dataset/06-data-quality-rules.md", files="docs/01-dataset/06-data-quality-rules.md",
  steps=["Turunkan aturan DQ-xx dari temuan", "Tentukan aksi: tolak / tandai / simpan", "Kaitkan setiap aturan ke reason code"],
  spec="Tiap aturan: ID, kondisi, aksi, reason code, jumlah baris terdampak (terukur)", ac="Setiap aturan punya angka dampak dari profil.",
  verify="Review manual", approval="G1 (kebijakan DQ)")
t("A-P1-010", "Rekomendasi dataset + laporan Fase 1 (12 bagian)", (1, 1.5, 2), "A-P1-004:H, A-P1-005:H, A-P1-007:H, A-P1-009:H, B-P1-001:S",
  obj="Merangkum rekomendasi periode final, produk, batas, dan aturan.", why="Paket keputusan G1.",
  inputs="Semua dokumen 01-dataset", outputs="docs/01-dataset/07-dataset-recommendation.md, docs/01-dataset/README.md",
  files="docs/01-dataset/README.md, docs/01-dataset/07-dataset-recommendation.md", steps=["Tulis rekomendasi", "Susun laporan 12 bagian", "Daftar keputusan untuk G1"],
  spec="Format 12 bagian (00-discovery/README.md)", ac="Semua keputusan G1 punya opsi + rekomendasi + bukti.", verify="Cek tautan relatif", approval="G1")
t("B-P1-001", "Estimasi volume per provinsi per hari/bulan", (1.5, 2, 3), "A-P1-004:H", legacy="P1-07", rev="A",
  obj="Mengukur baris per provinsi-hari dan provinsi-bulan (median, p99, maks).", why="Masukan ukuran partisi Fase 3 (R-05).",
  inputs="data/firms/profile/prov_day.csv, prov_month.csv", outputs="docs/03-specs/database/00-volume-estimates.md", files="docs/03-specs/database/00-volume-estimates.md",
  steps=["Hitung distribusi baris per kandidat kunci partisi", "Estimasi byte per baris dari ukuran CSV", "Tandai provinsi/bulan puncak"],
  spec="Hanya angka hasil ukur; proyeksi ditandai ASSUMPTION", ac="Tabel per kandidat partisi dengan p50/p99/maks baris dan perkiraan MB.",
  verify="Skrip analisis dapat dijalankan ulang", approval="Tidak (masukan G3)")
t("C-P1-001", "Inventaris toolchain & opsi cloud (NA-07)", (2, 3, 4), rev="B",
  obj="Mendaftar versi Python/Node/Cassandra/driver yang kompatibel dan opsi cloud tim.", why="Masukan ADR stack (C-P3-001) dan OQ-23 sebelum D12.",
  inputs="Charter §8, OQ-23–OQ-27, dokumen 07", outputs="docs/03-specs/architecture/00-toolchain-and-cloud-options.md",
  files="docs/03-specs/architecture/00-toolchain-and-cloud-options.md", steps=["Cek kompatibilitas versi dari dokumentasi resmi", "Kumpulkan opsi cloud/kredit dari anggota", "Bandingkan biaya & memori minimum Cassandra"],
  spec="Setiap versi diberi sumber resmi + tanggal baca", ac="Matriks versi terverifikasi + ≥2 opsi cloud dengan biaya/batas.", verify="Review manual",
  approval="Tidak (masukan HD-16)")
t("D-P1-001", "Draf user stories & FR dari charter", (2, 3, 4), rev="C", legacy="P1-08",
  obj="Menulis draf user story dan FR untuk 12 fitur MoSCoW.", why="Memulai Fase 2 paralel agar G2 tidak terlambat (R-02).",
  inputs="Charter §4–§7", outputs="docs/02-requirements/00-draft-user-stories.md", files="docs/02-requirements/00-draft-user-stories.md",
  steps=["Satu story per fitur Must/Should", "Kaitkan ke persona OQ-19", "Tandai hal yang menunggu data Fase 1"],
  spec="Format: Sebagai <persona>, saya ingin …, agar …", ac="Setiap fitur Must punya ≥1 story.", verify="Review manual", approval="Tidak (masukan G2)")
t("X-P1-901", "Tetapkan anggota↔peran, koordinator, ketersediaan; setujui rencana eksekusi", (1, 1.5, 2), rev="D",
  obj="Mengisi HD-01–HD-06 dan menyetujui docs/10-execution-plan/.", why="Tanpa pemilik nyata, tugas tidak bisa mulai.",
  inputs="docs/10-execution-plan/", outputs="12-human-decision-register.md terisi; catatan persetujuan", files="docs/10-execution-plan/12-human-decision-register.md",
  steps=["Rapat/obrolan tim 30–45 menit", "Isi matriks skill di 01-role-charters.md", "Catat keputusan"],
  spec="Mekanisme persetujuan HD-05", ac="HD-01–HD-06 berstatus DECIDED.", verify="Review manual", approval="Tim (GATE-EP)", agent="Manusia (agen hanya mencatat)")
t("X-P1-902", "Paket gerbang G1 + catat keputusan + perbarui STATUS", (0.5, 1, 1.5), "A-P1-010:H", rev="A",
  obj="Mengumpulkan keputusan G1 dan memperbarui docs/STATUS.md.", why="Fase 2/3 butuh keputusan dataset final.",
  inputs="Laporan Fase 1", outputs="Keputusan G1 tercatat; STATUS.md diperbarui", files="docs/STATUS.md",
  steps=["Bagikan paket", "Kumpulkan persetujuan", "Perbarui STATUS + register lewat CR"], spec="Checklist G1 (10-phase-gates)",
  ac="Setiap butir checklist G1 berstatus disetujui/ditolak.", verify="Review manual", approval="Tim (G1)", agent="Manusia + agen pencatat")
gate("GATE-EP", "X-P1-901:H")
gate("GATE-G1", "X-P1-902:H")

# ---------------------------------------------------------------- PHASE 2
t("D-P2-001", "Functional requirements final", (2.5, 3.5, 5), "D-P1-001:H, GATE-G1:HA",
  obj="Menulis FR bernomor untuk fitur Must/Should dengan data Fase 1.", why="Dasar query requirements dan UI spec.",
  inputs="Draf story, keputusan G1", outputs="docs/02-requirements/01-functional-requirements.md", files="docs/02-requirements/01-functional-requirements.md",
  steps=["Ubah story menjadi FR-xx", "Kaitkan ke fitur #1–#12", "Tandai MoSCoW"], spec="FR-xx: pernyataan, persona, prioritas, sumber",
  ac="Setiap fitur Must ↔ ≥1 FR; tidak ada FR tanpa fitur.", verify="Matriks traceability fitur↔FR lengkap", approval="G2")
t("D-P2-002", "Acceptance criteria per FR", (2, 3, 4), "D-P2-001:H",
  obj="Menulis kriteria Given/When/Then yang dapat diuji.", why="Dipakai test API/UI dan checklist G8.",
  inputs="FR", outputs="Bagian AC di 01-functional-requirements.md", files="docs/02-requirements/01-functional-requirements.md",
  steps=["≥1 AC per FR", "Sertakan kasus kosong/error", "Tandai AC yang butuh data nyata"], spec="Given/When/Then",
  ac="Setiap FR Must punya AC terukur.", verify="Review manual", approval="G2")
t("C-P2-001", "Non-functional requirements kuantitatif", (2, 3, 4), "GATE-G1:HA, B-P1-001:H, A-P1-008:S", rev="D", collab="A, B",
  obj="Menetapkan target latensi API, batas titik peta, kesegaran data, interval polling, keamanan, reproduksibilitas.", why="Charter menunda target angka ke Fase 2.",
  inputs="Volume terukur, latensi NRT", outputs="docs/02-requirements/02-non-functional-requirements.md", files="docs/02-requirements/02-non-functional-requirements.md",
  steps=["Usulkan angka dengan dasar terukur", "Tentukan cara ukur tiap NFR", "Tandai yang hanya berlaku di cloud"], spec="NFR-xx: target, metode ukur, alasan",
  ac="Setiap NFR punya angka dan metode verifikasi.", verify="Review manual", approval="G2")
t("A-P2-001", "Semantik data & aturan perhitungan", (2, 3, 4), "GATE-G1:HA", rev="D",
  obj="Menetapkan definisi 'jumlah deteksi': tanggal lokal, default confidence, titik luar provinsi, sumber statis, presedensi SP/NRT, penggabungan satelit.",
  why="Mencegah agregat yang salah tafsir (R-15) dan perbedaan antar lapisan.", inputs="Keputusan G1, OQ-08–OQ-12",
  outputs="docs/03-specs/data/01-data-semantics.md", files="docs/03-specs/data/01-data-semantics.md",
  steps=["Tulis aturan SEM-xx", "Beri contoh numerik", "Tandai keputusan yang butuh persetujuan"], spec="Mengikuti OQ-08–OQ-12",
  ac="Setiap angka di dashboard dapat dijelaskan oleh satu aturan SEM-xx.", verify="Review manual", approval="G2 (kebijakan data)")
t("B-P2-001", "Kebutuhan query aplikasi (Q-xx)", (2, 3, 4), "D-P2-001:H, A-P2-001:S", rev="C", collab="C, D",
  obj="Menerjemahkan setiap FR menjadi kebutuhan query: parameter, filter, urutan, kardinalitas, ukuran hasil.", why="Input access patterns; mencegah desain relasional (R-09).",
  inputs="FR, semantik data, volume", outputs="docs/03-specs/database/01-query-requirements.md", files="docs/03-specs/database/01-query-requirements.md",
  steps=["Satu Q-xx per kebutuhan baca", "Estimasi baris hasil dari volume", "Tandai query yang butuh pra-agregasi"], spec="Q-xx ↔ FR-xx",
  ac="Setiap FR yang membaca data ↔ ≥1 Q-xx.", verify="Matriks FR↔Q lengkap", approval="G2")
t("D-P2-003", "Kunci MVP + urutan pemotongan cakupan", (1, 1.5, 2.5), "D-P2-002:H, C-P2-001:H, B-P2-001:H", rev="C",
  obj="Mengunci daftar Must final dan urutan fitur yang dipotong bila terlambat.", why="Mitigasi scope creep (R-01).",
  inputs="FR, NFR, Q", outputs="docs/02-requirements/03-mvp-lock.md", files="docs/02-requirements/03-mvp-lock.md",
  steps=["Tulis daftar Must final", "Tulis urutan descoping", "Ajukan ke G2"], spec="Charter §6", ac="Daftar descoping berurutan disetujui tim.",
  verify="Review manual", approval="G2 (ruang lingkup)")
t("X-P2-901", "Paket gerbang G2", (0.5, 1, 1.5), "D-P2-003:H, A-P2-001:H", rev="D",
  obj="Mengumpulkan persetujuan G2.", why="Fase 3 tidak boleh mulai tanpa requirements.", inputs="Dokumen Fase 2", outputs="Keputusan G2; STATUS.md",
  files="docs/STATUS.md", steps=["Bagikan paket", "Catat keputusan"], spec="Checklist G2", ac="Checklist G2 lengkap.", verify="Review manual",
  approval="Tim (G2)", agent="Manusia + agen pencatat")
gate("GATE-G2", "X-P2-901:H")

# ---------------------------------------------------------------- PHASE 3
t("B-P3-001", "Access pattern matrix", (2, 3, 4), "GATE-G2:HA, B-P2-001:H", rev="C", collab="A",
  obj="Memetakan Q-xx ke tabel, kunci partisi, kunci clustering, dan estimasi ukuran partisi.", why="Skema hanya boleh mengikuti access pattern yang disetujui.",
  inputs="Q-xx, volume", outputs="docs/03-specs/database/02-access-patterns.md", files="docs/03-specs/database/02-access-patterns.md",
  steps=["Satu baris per Q-xx", "Pilih partisi + bucketing bila perlu", "Hitung ukuran partisi p99 dari volume"], spec="Tanpa ALLOW FILTERING/scan penuh",
  ac="Setiap Q-xx terpetakan ke tepat satu tabel/query; ukuran partisi p99 di bawah batas yang ditetapkan.", verify="Review silang C (konsumen)", approval="G3")
t("A-P3-001", "Kontrak canonical event v1 + sampel record", (2, 3, 5), "GATE-G2:HA, A-P1-003:H", collab="B",
  obj="Mendefinisikan field, tipe, nullability, identitas dedup, ID spasial, konvensi waktu, provenance.", why="Antarmuka ETL→Cassandra (kontrak B di 06).",
  inputs="Data dictionary, semantik data", outputs="docs/03-specs/data/02-canonical-event-contract.md, docs/03-specs/data/samples/canonical-events.sample.jsonl",
  files="docs/03-specs/data/02-canonical-event-contract.md, docs/03-specs/data/samples/", steps=["Tabel field", "Definisikan detection_id deterministik", "Hasilkan ≥20 contoh dari data nyata (termasuk luar provinsi & malam lintas tanggal)"],
  spec="Versi kontrak semver; perubahan lewat CR", ac="B mengonfirmasi tiap field dapat dipetakan ke CQL; contoh lolos validasi skema JSON.",
  verify="Validasi sampel terhadap JSON Schema", approval="G3 (kontrak antarmuka)")
t("A-P3-002", "Spesifikasi ETL (dua mode)", (3, 4, 5.5), "A-P3-001:S, A-P1-009:H", rev="C",
  obj="Menentukan tahap, mode backfill & incremental, checkpoint, run log, rejected records, semantik re-run, penjaga kuota.", why="Dasar implementasi Fase 5.",
  inputs="Aturan DQ, kontrak canonical", outputs="docs/03-specs/data/03-etl-spec.md", files="docs/03-specs/data/03-etl-spec.md",
  steps=["Diagram tahap", "Definisikan checkpoint per mode", "Definisikan reason code & run log"], spec="Source adapter (OQ-28)",
  ac="Setiap tahap punya input/output/kegagalan; idempotensi didefinisikan secara terukur.", verify="Review manual", approval="G3")
t("B-P3-002", "Model data logis & fisik + spesifikasi CQL", (3, 4.5, 6), "B-P3-001:H, A-P3-001:I", collab="C",
  obj="Menulis tabel, tipe, kunci, TTL (bila ada), dan file CQL spesifikasi (belum dieksekusi).", why="Kontrak Cassandra→backend.",
  inputs="Access patterns, kontrak canonical, volume", outputs="docs/03-specs/database/03-data-model.md, docs/03-specs/database/schema-v1.cql",
  files="docs/03-specs/database/", steps=["Logical model", "Physical model + bucketing", "CQL draft + contoh query per Q-xx"], spec="Tanpa counter table untuk agregat",
  ac="Setiap tabel ↔ ≥1 Q-xx; CQL valid secara sintaks (cqlsh di container dev).", verify="Parse CQL di Cassandra dev (setelah B-P4-001)", approval="G3 (skema)")
t("B-P3-003", "Strategi read model/agregat & rebuild", (2, 3, 4), "B-P3-002:H",
  obj="Mendefinisikan cara agregat dihitung ulang secara absolut per partisi dan prosedur rebuild.", why="Mencegah agregat ganda (R-10).",
  inputs="Model data", outputs="docs/03-specs/database/04-aggregates.md", files="docs/03-specs/database/04-aggregates.md",
  steps=["Pilih granularitas agregat", "Definisikan pemicu hitung ulang", "Definisikan rebuild penuh"], spec="Nilai absolut, bukan increment",
  ac="Re-run input yang sama menghasilkan agregat identik (dapat diuji).", verify="Review manual", approval="G3")
t("C-P3-001", "Arsitektur end-to-end + ADR stack", (3, 4, 5), "GATE-G2:HA, C-P1-001:S", rev="B",
  obj="Menulis arsitektur, diagram aliran data, dan ADR versi stack serta paritas lokal↔cloud.", why="Semua peran butuh gambaran komponen yang sama.",
  inputs="Charter, NFR, inventaris toolchain", outputs="docs/03-specs/architecture/01-architecture.md, docs/03-specs/architecture/adr/ADR-001..002",
  files="docs/03-specs/architecture/", steps=["Diagram komponen & aliran", "ADR-001 versi stack", "ADR-002 paritas lokal/cloud"], spec="Format ADR: konteks, keputusan, konsekuensi",
  ac="Setiap komponen punya pemilik dan antarmuka tertaut ke 06-interface-contracts.", verify="Review manual", approval="G3 (arsitektur)")
t("D-P3-001", "Spesifikasi UI + wireframe low-fi", (3, 4, 6), "D-P2-002:H, GATE-G2:HA", rev="C",
  obj="Inventaris halaman, wireframe, perilaku filter, drill-down, state loading/empty/error, indikator kesegaran, disclaimer.", why="Masukan kontrak API dan dasar implementasi UI.",
  inputs="FR + AC", outputs="docs/03-specs/ui/01-ui-spec.md, docs/03-specs/ui/wireframes/", files="docs/03-specs/ui/",
  steps=["Inventaris halaman", "Wireframe tiap halaman", "Tabel interaksi → kebutuhan data"], spec="Bahasa UI Indonesia (OQ-20)",
  ac="Setiap elemen data di wireframe ↔ field API yang diminta.", verify="Review silang C", approval="G3 (perilaku UI)")
t("C-P3-002", "Kontrak API v1 (OpenAPI)", (3, 4, 6), "B-P3-001:I, D-P3-001:S, C-P2-001:H", rev="D", collab="B",
  obj="Menulis openapi.yaml: endpoint, parameter, skema respons, skema error, contoh, batas jumlah titik.", why="Memungkinkan backend & frontend paralel dengan mock.",
  inputs="Access patterns, UI spec, NFR", outputs="docs/03-specs/api/openapi.yaml, docs/03-specs/api/01-api-notes.md", files="docs/03-specs/api/",
  steps=["Endpoint per kebutuhan UI", "Contoh respons dari sampel canonical", "Skema error seragam"], spec="OpenAPI 3.1; path bahasa Inggris",
  ac="openapi.yaml valid; setiap endpoint ↔ Q-xx; D menyetujui cakupan kebutuhan UI.", verify="Validator OpenAPI (CLI) → 0 error", approval="G3 (kontrak antarmuka)")
t("C-P3-003", "ADR deployment & keamanan (OQ-24–OQ-26)", (2, 3, 4), "C-P3-001:H", rev="B", nb=9,
  obj="Mengusulkan cara Cassandra & poller berjalan di cloud dan kontrol keamanan minimum, netral penyedia.", why="Cloud Must setelah D13; keputusan penyedia ≤ D12.",
  inputs="Opsi cloud, NFR", outputs="docs/03-specs/architecture/adr/ADR-003-deployment.md, ADR-004-security.md", files="docs/03-specs/architecture/adr/",
  steps=["Opsi + rekomendasi per OQ", "Kontrol keamanan minimum", "Kriteria pemilihan penyedia"], spec="R-23, R-25", ac="Setiap kontrol keamanan punya cara verifikasi.",
  verify="Review manual", approval="G3 + persetujuan keamanan (HD-16)")
t("B-P3-004", "Rencana eksperimen Cassandra", (2, 3, 4), "B-P3-002:S", rev="A", nb=9,
  obj="Hipotesis, variabel, metrik, protokol, lingkungan untuk eksperimen bucketing (Must) dan replikasi (Should).", why="O-E3; mencegah benchmark tidak valid (R-16).",
  inputs="Model data, dokumen 07", outputs="docs/03-specs/database/05-experiment-plan.md", files="docs/03-specs/database/05-experiment-plan.md",
  steps=["Hipotesis terukur", "Protokol warm-up & repetisi", "Lingkungan & versi dicatat"], spec="Tidak ada hasil sebelum dijalankan",
  ac="Rencana dapat dijalankan orang lain tanpa bertanya.", verify="Review manual", approval="G3")
t("X-P3-901", "Paket G3 + cek konsistensi lintas kontrak", (1, 2, 3), "A-P3-001:H, A-P3-002:H, B-P3-002:H, B-P3-003:H, C-P3-001:H, C-P3-002:H, C-P3-003:H, D-P3-001:H, B-P3-004:S", rev="C",
  obj="Memastikan nama field, tipe, dan semantik konsisten dari canonical → CQL → OpenAPI → UI.", why="Kesalahan integrasi paling murah dicegah di sini.",
  inputs="Semua spesifikasi Fase 3", outputs="Laporan konsistensi + keputusan G3", files="docs/03-specs/README.md, docs/STATUS.md",
  steps=["Tabel jejak field lintas lapisan", "Catat ketidakcocokan sebagai CR", "Kumpulkan persetujuan"], spec="06-interface-contracts.md",
  ac="0 ketidakcocokan terbuka saat G3 disetujui.", verify="Skrip cek nama field openapi vs CQL vs canonical (opsional)", approval="Tim (G3)", agent="Agen menyusun, manusia memutuskan")
gate("GATE-G3", "X-P3-901:H")

# ---------------------------------------------------------------- PHASE 4
t("C-P4-001", "Kerangka repo + CODEOWNERS + template PR", (2, 3, 4), "GATE-EP:HA", rev="B",
  obj="Membuat struktur direktori sesuai 07-file-ownership-matrix, CODEOWNERS, dan template PR.", why="Kepemilikan file ditegakkan oleh alat, bukan ingatan.",
  inputs="07-file-ownership-matrix.md", outputs="Direktori kosong ber-README, .github/CODEOWNERS, .github/pull_request_template.md", files=".github/, README.md",
  steps=["Buat direktori", "CODEOWNERS per direktori", "Template PR dengan checklist DoD"], spec="07-file-ownership-matrix", ac="CODEOWNERS mencakup semua direktori di matriks.",
  verify="Skrip cek setiap direktori di matriks ada di CODEOWNERS", approval="G4")
t("D-P4-003", "AGENTS.md & CLAUDE.md lengkap", (3, 4, 5), "GATE-EP:HA", rev="C", collab="A, B, C",
  obj="Menulis coding standards, git workflow, DoD, protokol Claude Code/Codex, aturan worktree.", why="OQ-18; mencegah konflik agen (R-13).",
  inputs="Dokumen 07, 08, 11 di rencana ini", outputs="AGENTS.md, CLAUDE.md", files="AGENTS.md, CLAUDE.md",
  steps=["Gabungkan aturan minimum saat ini", "Tambah standar per bahasa", "Tambah protokol agen & stop conditions"], spec="Tidak mengubah keputusan Fase 0",
  ac="Setiap prompt peran di 11-role-prompts konsisten dengan AGENTS.md.", verify="Review manual", approval="G4")
t("A-P4-002", "Tooling Python bersama (lint, format, test, pre-commit)", (2, 3, 4), "C-P4-001:H", rev="C",
  obj="Mengunci versi Python dan konfigurasi ruff/pytest/pre-commit.", why="Lingkungan heterogen (R-12).",
  inputs="ADR-001 (draf)", outputs="ruff.toml, .pre-commit-config.yaml, panduan venv", files="ruff.toml, .pre-commit-config.yaml",
  steps=["Pilih versi", "Konfigurasi lint/format", "Hook pre-commit: lint, deteksi secret"], spec="Tanpa alat yang tidak perlu",
  ac="`pre-commit run --all-files` lulus di repo bersih.", verify="pre-commit run --all-files", approval="G4")
t("C-P4-004", "Docker Compose dasar + validasi environment", (3, 4, 5), "C-P4-001:H, B-P4-001:I", rev="B",
  obj="Compose dengan service cassandra (fragmen B), api placeholder, web dev; healthcheck; .env.example; skrip cek env.", why="Kriteria keberhasilan #1.",
  inputs="Fragmen konfigurasi Cassandra dari B", outputs="docker-compose.yml, .env.example, deploy/scripts/check_env.*", files="docker-compose.yml, .env.example, deploy/",
  steps=["Service + healthcheck", "Variabel env terdokumentasi", "Skrip cek env tanpa mencetak nilai secret"], spec="Konfigurasi lewat env (A-24)",
  ac="`docker compose up` → semua service healthy di mesin bersih.", verify="docker compose ps (healthy) di CI atau mesin anggota", approval="G4")
t("C-P4-005", "CI: lint + unit test per komponen", (2, 3, 5), "A-P4-002:H, D-P4-001:S", rev="D",
  obj="Pipeline CI tanpa secret yang menjalankan lint dan unit test.", why="Gerbang mutu otomatis sebelum merge.",
  inputs="Tooling Python & web", outputs=".github/workflows/ci.yml", files=".github/workflows/",
  steps=["Job per komponen dengan path filter", "Cache dependensi", "Wajibkan status hijau sebelum merge"], spec="HD-15 (pemakaian GitHub Actions)",
  ac="PR contoh menunjukkan CI hijau; CI gagal bila test gagal.", verify="PR uji dengan test gagal sengaja", approval="G4")
t("B-P4-001", "Konfigurasi Cassandra single-node untuk dev", (2, 3, 5), "GATE-EP:HA", rev="C",
  obj="Image versi terkunci, heap terbatas, healthcheck, skrip tunggu-siap, keyspace dev (tanpa skema produksi).", why="Dasar semua pekerjaan DB.",
  inputs="ADR-001 (draf), dokumen 07", outputs="db/docker/, db/scripts/, db/README.md", files="db/",
  steps=["Pilih versi (ADR)", "Fragmen Compose untuk C", "Skrip readiness"], spec="Heap ±1 GB", ac="Cassandra siap < N menit dan lolos `cqlsh -e 'describe keyspaces'`.",
  verify="Skrip readiness exit 0", approval="Tidak")
t("B-P4-002", "Smoke test 3 node di laptop (dokumen 07 §4)", (2, 3, 4), "B-P4-001:H", rev="C", prio="Should",
  obj="Membuktikan laptop memenuhi spesifikasi 3 node untuk eksperimen replikasi.", why="Validasi A-25 sebelum B-P7-003.",
  inputs="Dokumen 07", outputs="experiments/env-3node/SMOKE.md", files="experiments/env-3node/",
  steps=["Jalankan 3 node", "nodetool status", "Catat hardware & waktu"], spec="Dokumen 07 §4", ac="3 node UN atau laporan kegagalan dengan bukti.",
  verify="Output nodetool status", approval="Tidak")
t("A-P4-001", "Skeleton paket pipeline + fixtures uji dari data nyata", (2, 3, 4), "C-P4-001:H, A-P1-004:S", rev="B",
  obj="pyproject, struktur modul, dan fixtures kecil (CSV nyata + golden output).", why="Test deterministik tanpa memanggil API.",
  inputs="Data mentah Fase 1", outputs="pipeline/pyproject.toml, pipeline/src/, pipeline/tests/fixtures/", files="pipeline/",
  steps=["Struktur modul per tahap ETL", "Pilih subset fixtures (≤1 MB) mencakup kasus tepi", "Test contoh lulus"], spec="Fixtures data FIRMS publik + atribusi",
  ac="`pytest pipeline` lulus; fixtures mencakup malam lintas tanggal, luar provinsi, NRT & SP.", verify="pytest pipeline", approval="Tidak")
t("D-P4-001", "Scaffold React + Leaflet + lint/test", (2, 3, 5), "C-P4-001:H", rev="C",
  obj="Proyek web (Vite), lint/format, test runner, peta dasar statis dengan atribusi.", why="Frontend dapat mulai tanpa backend.",
  inputs="ADR-001 (draf), HD-14", outputs="web/", files="web/", steps=["Scaffold", "Lint & test runner", "Halaman peta dasar"], spec="HD-14 (TypeScript, library chart)",
  ac="`npm run lint && npm test && npm run build` lulus.", verify="Perintah tersebut di CI", approval="Tidak")
t("D-P4-002", "Mock API dari contoh OpenAPI", (2, 3, 4), "C-P3-002:I, D-P4-001:H", rev="C",
  obj="Mock layer (mis. MSW) yang mengembalikan contoh openapi.yaml + toggle mock/real.", why="Frontend paralel dengan backend (OQ-27 opsi A).",
  inputs="openapi.yaml v1", outputs="web/src/mocks/", files="web/src/mocks/", steps=["Muat contoh dari openapi.yaml", "Handler per endpoint", "Flag env untuk mock/real"],
  spec="Tidak menambah field di luar kontrak", ac="Setiap endpoint di kontrak punya handler; flag mematikan mock.", verify="Test: respons mock lolos validasi skema OpenAPI", approval="Tidak")
t("X-P4-901", "Paket G4: uji fresh clone", (0.5, 1, 1.5), "D-P4-003:H, C-P4-004:H, C-P4-005:H, B-P4-001:H, A-P4-001:H, D-P4-001:H", rev="C",
  obj="Anggota yang bukan pemilik harness meng-clone ulang dan menjalankan semua cek.", why="Bukti reproduksibilitas sejak awal (O-E4).",
  inputs="Repo", outputs="Catatan uji fresh clone + keputusan G4", files="docs/STATUS.md", steps=["Clone bersih", "compose up + lint + test", "Catat hambatan"],
  spec="Checklist G4", ac="Semua cek lulus tanpa bantuan pemilik.", verify="Log perintah", approval="Tim (G4)", agent="Manusia")
gate("GATE-G4", "X-P4-901:H")

# ---------------------------------------------------------------- PHASE 5
t("A-P5-001", "Source adapter + extractor FIRMS (kuota, retry, raw zone)", (3, 4, 6), "GATE-G3:HA, GATE-G4:HA, A-P4-001:H", rev="C",
  obj="Antarmuka source adapter dan implementasi Area API dengan penjaga kuota, retry, manifest SHA-256.", why="OQ-28; raw zone (R-04).",
  inputs="ETL spec, inventaris sumber", outputs="pipeline/src/.../extract/", files="pipeline/", steps=["Interface adapter", "Extractor + manifest", "Test dengan respons tiruan (tanpa API)"],
  spec="03-etl-spec.md", ac="Test unit lulus tanpa jaringan; MAP_KEY tidak pernah muncul di log (test).", verify="pytest + test redaksi log", approval="Tidak")
t("A-P5-002", "Parsing & validasi + rejected records", (3, 4, 6), "A-P5-001:S, A-P3-002:H", rev="B",
  obj="Parser per sumber dan aturan DQ dengan reason code.", why="Kualitas data terukur (O-E1).", inputs="Aturan DQ, fixtures", outputs="pipeline/src/.../validate/",
  files="pipeline/", steps=["Parser per header", "Aturan DQ-xx", "Simpan rejected + alasan"], spec="06-data-quality-rules.md",
  ac="Setiap aturan DQ punya test positif & negatif.", verify="pytest", approval="Tidak")
t("A-P5-003", "Normalisasi waktu & atribut", (2, 3, 5), "A-P5-002:H", rev="B",
  obj="UTC timestamp, padding acq_time, tanggal lokal per provinsi, normalisasi confidence & processing level.", why="R-07; OQ-08.",
  inputs="Kontrak canonical, semantik data", outputs="pipeline/src/.../normalize/", files="pipeline/",
  steps=["Konversi waktu", "Tanggal lokal butuh provinsi → setelah enrichment", "Test kasus malam lintas tanggal"], spec="SEM-xx",
  ac="Test malam lintas tanggal WIB/WITA/WIT lulus.", verify="pytest", approval="Tidak")
t("A-P5-004", "Pengayaan spasial (provinsi, status luar provinsi)", (3, 4, 6), "A-P5-002:S", rev="B",
  obj="Assign provinsi (dan kab/kota bila Could disetujui) dari snapshot batas ber-checksum.", why="OQ-06, OQ-11.",
  inputs="Snapshot batas (HD-08)", outputs="pipeline/src/.../enrich/", files="pipeline/", steps=["Loader snapshot + checksum", "Point-in-polygon", "Status wilayah khusus"],
  spec="05-boundary-sources.md", ac="Hasil cocok dengan coord_assign Fase 1 pada fixtures (selisih 0 kecuali tepi yang terdokumentasi).", verify="pytest golden", approval="Tidak")
t("A-P5-005", "Deduplikasi & identitas deteksi", (3, 4, 6), "A-P5-003:H, A-P5-004:H", rev="B", collab="B",
  obj="detection_id deterministik dan aturan presedensi SP>NRT.", why="R-06 (skor 9).", inputs="Kontrak canonical, hasil A-P1-007",
  outputs="pipeline/src/.../dedup/", files="pipeline/", steps=["Implementasi kunci", "Presedensi sumber", "Property test: urutan input tidak mengubah hasil"],
  spec="02-canonical-event-contract.md", ac="Dua run dengan urutan input berbeda → set detection_id identik.", verify="pytest (property test)", approval="Tidak")
t("A-P5-006", "Mode backfill (checkpoint, resume, run log)", (3, 4, 5), "A-P5-005:H, B-P5-002:I, B-P5-004:I", rev="C",
  obj="CLI backfill rentang tanggal dengan checkpoint dan run log memakai writer B.", why="MVP kapabilitas 1.",
  inputs="Writer & run-log API dari B", outputs="pipeline/src/.../modes/backfill.py", files="pipeline/", steps=["CLI", "Checkpoint per chunk tanggal", "Run log"],
  spec="03-etl-spec.md", ac="Backfill terputus dapat dilanjutkan tanpa duplikat.", verify="Test integrasi dengan Cassandra container", approval="Tidak")
t("A-P5-007", "Mode incremental NRT (polling)", (3, 4, 6), "A-P5-006:H", rev="C",
  obj="Poller berkala dengan jendela overlap, checkpoint waktu, dan pencatatan kegagalan.", why="Fitur #12 Must; target berjalan ±D10.",
  inputs="NFR interval polling", outputs="pipeline/src/.../modes/incremental.py", files="pipeline/", steps=["Loop poll", "Overlap window", "Catat sukses/gagal ke run log"],
  spec="03-etl-spec.md, NFR", ac="Poll berulang pada jendela sama tidak menambah baris.", verify="Test integrasi: 2 poll tumpang tindih → jumlah sama", approval="Tidak")
t("A-P5-008", "Test ETL + harness idempotensi", (3, 4, 5), "A-P5-005:H", rev="B",
  obj="Test unit kasus tepi dan harness yang membandingkan dua run.", why="Kriteria keberhasilan #2.", inputs="Fixtures", outputs="pipeline/tests/",
  files="pipeline/tests/", steps=["Edge cases waktu/dedup", "Harness: run 2× → bandingkan jumlah & checksum", "Masuk CI"], spec="O-E1",
  ac="Harness gagal bila ada perbedaan; lulus pada kode saat ini.", verify="pytest di CI", approval="Tidak")
t("A-P5-009", "Publikasi batas provinsi tersederhanakan untuk web", (1, 2, 3), "A-P5-004:H", rev="D",
  obj="GeoJSON tersederhanakan kecil + atribusi untuk lapisan peta.", why="Dibutuhkan D-P6-004.", inputs="Snapshot batas",
  outputs="pipeline/resources/boundaries/provinces-simplified.geojson", files="pipeline/resources/",
  steps=["Simplify", "Ukur ukuran file", "Serahkan ke D"], spec="HD-08 (lisensi sebelum commit)", ac="Ukuran ≤ batas NFR; 38 provinsi.", verify="Skrip hitung fitur & ukuran", approval="HD-08")
t("A-P5-010", "Dokumentasi pipeline", (1, 2, 3), "A-P5-007:H", rev="C",
  obj="pipeline/README: instalasi, mode, konfigurasi, run log, rejected records.", why="O-E4.", inputs="Kode pipeline", outputs="pipeline/README.md",
  files="pipeline/README.md", steps=["Cara jalan per mode", "Variabel env", "Troubleshooting"], spec="—", ac="Anggota lain menjalankan backfill kecil hanya dari README.",
  verify="Uji oleh reviewer", approval="Tidak")
t("B-P5-001", "Implementasi skema CQL v1 + migrasi", (2, 3, 4), "GATE-G3:HA, B-P4-001:H", rev="A",
  obj="File migrasi bernomor dan skrip apply idempoten sesuai skema yang disetujui G3.", why="Skema versi terkontrol.",
  inputs="schema-v1.cql (G3)", outputs="db/migrations/0001_*.cql, db/scripts/migrate.*", files="db/",
  steps=["Salin skema disetujui ke migrasi", "Skrip apply (IF NOT EXISTS)", "Test apply 2×"], spec="Tanpa drop/truncate otomatis",
  ac="Apply 2× tanpa error; skema identik dengan spesifikasi.", verify="Test: describe schema vs spesifikasi", approval="Operasi destruktif butuh persetujuan manusia")
t("B-P5-002", "Writer adapter Cassandra (idempoten)", (3, 4, 6), "B-P5-001:H, A-P3-001:I", rev="A", collab="A",
  obj="Library penulis dengan prepared statements, upsert idempoten, batch per partisi, consistency level terdokumentasi.", why="Antarmuka ETL→Cassandra.",
  inputs="Kontrak canonical, skema", outputs="db/src/.../writer.py", files="db/", steps=["API write_events(events)", "Prepared statements", "Test tulis 2× → jumlah sama"],
  spec="06 kontrak B", ac="Menulis ulang event yang sama tidak menambah baris.", verify="Test integrasi container", approval="Tidak")
t("B-P5-003", "Builder read model/agregat", (3, 4, 6), "B-P5-002:H, B-P3-003:H", rev="A",
  obj="Hitung ulang agregat provinsi-hari/bulan secara absolut setelah load.", why="Ranking & timeline (fitur #1, #3, #4).",
  inputs="04-aggregates.md", outputs="db/src/.../aggregates.py", files="db/", steps=["Hitung per partisi terdampak", "Tulis nilai absolut", "Rebuild penuh"],
  spec="Tanpa counter", ac="Agregat = jumlah dari tabel detail untuk sampel provinsi/hari.", verify="Test konsistensi agregat vs detail", approval="Tidak")
t("B-P5-004", "Tabel run log & checkpoint + writer", (2, 3, 4), "B-P5-001:H", rev="C",
  obj="Tabel dan API untuk run log, checkpoint, status poll.", why="Monitoring (fitur #9) dan resume ETL.", inputs="ETL spec",
  outputs="db/src/.../runlog.py", files="db/", steps=["Tabel", "API tulis/baca", "Test"], spec="06 kontrak B/C", ac="Endpoint status (C) dapat membaca run terakhir dengan 1 query partisi.",
  verify="Test integrasi", approval="Tidak")
t("B-P5-005", "Test database per access pattern", (2, 3, 5), "B-P5-003:H", rev="C",
  obj="Smoke test setiap Q-xx dan pemeriksaan bahwa tidak ada ALLOW FILTERING.", why="O-E2.", inputs="Access patterns",
  outputs="db/tests/", files="db/tests/", steps=["Satu test per Q-xx", "Grep ALLOW FILTERING di repo → 0", "Masuk CI (job dengan Cassandra)"],
  spec="02-access-patterns.md", ac="Semua Q-xx lulus; 0 ALLOW FILTERING.", verify="pytest db + grep", approval="Tidak")
t("B-P5-006", "Load backfill penuh + inspeksi ukuran partisi", (2, 3, 5), "A-P5-006:H, B-P5-003:H", rev="A", collab="A",
  obj="Memuat periode final dan membandingkan ukuran partisi nyata dengan estimasi.", why="Validasi model (R-05) dan data untuk G5.",
  inputs="Pipeline backfill, data mentah", outputs="Catatan load + tabel ukuran partisi di db/README.md", files="db/README.md",
  steps=["Jalankan backfill", "nodetool tablestats/tablehistograms", "Bandingkan dengan 00-volume-estimates"], spec="—",
  ac="Jumlah baris di Cassandra = jumlah event lolos ETL; ukuran partisi maks tercatat.", verify="Query hitung vs run log", approval="Tidak")
t("B-P5-007", "Dokumentasi database", (1, 2, 3), "B-P5-005:H", rev="C",
  obj="db/README: setup, skema, contoh query, migrasi.", why="O-E4.", inputs="Kode db", outputs="db/README.md", files="db/README.md",
  steps=["Setup", "Contoh query per Q-xx", "Prosedur rebuild agregat"], spec="—", ac="Reviewer menjalankan contoh query dari README.", verify="Uji oleh reviewer", approval="Tidak")
t("X-P5-901", "Checkpoint D10 (R-14) + paket G5", (0.5, 1, 1.5), "A-P5-007:H, A-P5-008:H, B-P5-005:H, B-P5-006:H", rev="A",
  obj="Memastikan data nyata ada di Cassandra dan poller berjalan; aktifkan kontingensi bila tidak.", why="Titik kritis charter §10.",
  inputs="Hasil Fase 5", outputs="Keputusan G5", files="docs/STATUS.md", steps=["Cek kriteria", "Putuskan kontingensi", "Catat"], spec="Checklist G5",
  ac="Checklist G5 lengkap.", verify="Review manual", approval="Tim (G5)", agent="Manusia + agen pencatat")
gate("GATE-G5", "X-P5-901:H")

# ---------------------------------------------------------------- PHASE 6
t("C-P6-001", "Skeleton FastAPI (config, health, logging, error, CORS)", (2, 3, 4), "GATE-G3:HA, GATE-G4:HA", rev="D",
  obj="Aplikasi dasar dengan readiness yang memeriksa Cassandra, skema error seragam.", why="Dasar semua endpoint.", inputs="openapi.yaml, ADR-004",
  outputs="api/", files="api/", steps=["Struktur app", "Health/readiness", "Error handler sesuai skema"], spec="openapi.yaml",
  ac="GET /health 200; error mengikuti skema kontrak.", verify="pytest api", approval="Tidak")
t("C-P6-002", "Interface repository + fake dari contoh kontrak", (2, 3, 4), "C-P6-001:H, C-P3-002:I", rev="B",
  obj="Protokol repository per Q-xx dan implementasi fake in-memory.", why="Backend tidak menunggu Cassandra.", inputs="Access patterns, contoh OpenAPI",
  outputs="api/src/.../repositories/", files="api/", steps=["Interface", "Fake dari sampel canonical", "Dependency injection"], spec="06 kontrak C",
  ac="Semua endpoint dapat diuji dengan fake.", verify="pytest", approval="Tidak")
t("C-P6-003", "Endpoint ringkasan + timeline", (2, 3, 5), "C-P6-002:H", rev="D", obj="Endpoint fitur #1 & #3.", why="Must.",
  inputs="Kontrak", outputs="api/ endpoint", files="api/", steps=["Validasi parameter", "Service", "Test"], spec="openapi.yaml",
  ac="Respons lolos validasi skema; tanggal memakai aturan SEM.", verify="pytest + contract test", approval="Tidak")
t("C-P6-004", "Endpoint ranking + detail provinsi", (2, 3, 5), "C-P6-002:H", rev="D", obj="Endpoint fitur #4 & #8.", why="Must.",
  inputs="Kontrak", outputs="api/ endpoint", files="api/", steps=["Validasi", "Service (luar provinsi dikecualikan)", "Test"], spec="OQ-11",
  ac="Wilayah khusus tidak masuk ranking; lolos skema.", verify="pytest + contract test", approval="Tidak")
t("C-P6-005", "Endpoint titik peta (terbatas)", (2, 3, 5), "C-P6-002:H", rev="D", obj="Endpoint fitur #2 dengan batas jumlah titik.", why="C-10.",
  inputs="Kontrak, NFR batas titik", outputs="api/ endpoint", files="api/", steps=["Validasi rentang", "Batas + flag truncated", "Test"], spec="NFR",
  ac="Respons tidak pernah melebihi batas; flag truncated benar.", verify="pytest", approval="Tidak")
t("C-P6-006", "Endpoint status pipeline & kesegaran data", (1, 2, 3), "C-P6-002:H, B-P5-004:I", rev="D", obj="Fitur #9 dan waktu pembaruan terakhir.",
  why="R-27.", inputs="Kontrak run log", outputs="api/ endpoint", files="api/", steps=["Baca run terakhir", "Hitung umur data", "Test"], spec="OQ-22",
  ac="Poll gagal terakhir terlihat di respons.", verify="pytest", approval="Tidak")
t("C-P6-007", "Repository Cassandra nyata", (3, 4, 6), "C-P6-003:H, C-P6-004:H, C-P6-005:H, C-P6-006:H, B-P5-001:H, B-P5-003:I", rev="B",
  obj="Implementasi repository dengan prepared statements sesuai access patterns.", why="Mengganti fake dengan data nyata.",
  inputs="Skema, access patterns", outputs="api/src/.../repositories/cassandra.py", files="api/", steps=["Satu metode per Q-xx", "Prepared statements", "Test integrasi"],
  spec="06 kontrak C", ac="Hasil fake vs Cassandra konsisten untuk fixture yang sama.", verify="Test integrasi container", approval="Tidak")
t("C-P6-008", "Test API (unit, kontrak, integrasi)", (2, 3, 5), "C-P6-007:H", rev="B", obj="Suite test API di CI.", why="Kriteria mutu.",
  inputs="openapi.yaml", outputs="api/tests/", files="api/tests/", steps=["Contract test vs openapi.yaml", "Integrasi Cassandra", "CI"], spec="—",
  ac="Setiap endpoint punya test sukses + error.", verify="pytest di CI", approval="Tidak")
t("C-P6-009", "Dokumentasi API", (1, 1.5, 2), "C-P6-008:H", rev="D", obj="api/README + contoh curl.", why="O-E4.", inputs="Kode API",
  outputs="api/README.md", files="api/README.md", steps=["Cara jalan", "Contoh request", "Kode error"], spec="—", ac="Reviewer menjalankan contoh.", verify="Uji oleh reviewer", approval="Tidak")
t("C-P6-010", "Endpoint distribusi FRP (Should)", (2, 3, 4), "C-P6-007:H", rev="D", prio="Should", obj="Fitur #7.", why="Should.",
  inputs="Kontrak (bila disetujui)", outputs="api/ endpoint", files="api/", steps=["Bin FRP", "Test"], spec="Butuh CR bila belum ada di kontrak v1",
  ac="Lolos skema.", verify="pytest", approval="CR bila mengubah kontrak")
t("D-P6-001", "Layout, routing, state filter, klien API", (3, 4, 5), "GATE-G3:HA, GATE-G4:HA, D-P4-002:H", rev="C",
  obj="Kerangka aplikasi, filter global (tanggal, provinsi, confidence, satelit), klien API dari kontrak.", why="Dasar semua halaman.",
  inputs="UI spec, openapi.yaml", outputs="web/src/", files="web/", steps=["Routing", "State filter + sinkron URL", "Klien API bertipe"], spec="01-ui-spec.md",
  ac="Filter tercermin di URL; klien hanya memakai field kontrak.", verify="npm test", approval="Tidak")
t("D-P6-002", "Kartu KPI + timeline", (3, 4, 6), "D-P6-001:H", rev="C", obj="Fitur #1 & #3.", why="Must.", inputs="Mock API",
  outputs="web/src/features/summary/", files="web/", steps=["Komponen", "Format tanggal lokal", "Test"], spec="UI spec", ac="Sesuai wireframe; label 'deteksi hotspot'.",
  verify="npm test", approval="Tidak")
t("D-P6-003", "Ranking + drill-down provinsi", (3, 4, 6), "D-P6-001:H", rev="C", obj="Fitur #4 & #8.", why="Must.", inputs="Mock API",
  outputs="web/src/features/ranking/", files="web/", steps=["Tabel ranking", "Drill-down", "Test"], spec="UI spec", ac="Klik provinsi memfilter semua tampilan.",
  verify="npm test", approval="Tidak")
t("D-P6-004", "Peta Leaflet (titik, batas, popup, notice batas)", (3, 5, 6), "D-P6-001:H, A-P5-009:S", rev="C", obj="Fitur #2.", why="Must.",
  inputs="Mock API, GeoJSON batas", outputs="web/src/features/map/", files="web/", steps=["Lapisan titik", "Lapisan batas", "Notice truncated"], spec="UI spec",
  ac="Peta tetap responsif pada jumlah titik maksimum NFR.", verify="npm test + uji manual terukur", approval="Tidak")
t("D-P6-005", "Status pipeline + kesegaran + disclaimer + atribusi", (2, 3, 4), "D-P6-001:H", rev="A", obj="Fitur #9, disclaimer, atribusi FIRMS & BIG.",
  why="Kriteria keberhasilan #5, #7.", inputs="Mock API", outputs="web/src/features/status/", files="web/", steps=["Halaman status", "Indikator kesegaran global", "Footer disclaimer & atribusi"],
  spec="Charter §3", ac="Disclaimer & waktu pembaruan terlihat di semua halaman.", verify="npm test", approval="Teks disclaimer final: tim")
t("D-P6-006", "State loading/empty/error + aksesibilitas dasar", (2, 3, 4), "D-P6-002:H, D-P6-003:H, D-P6-004:H", rev="C", obj="Perilaku konsisten untuk semua state.",
  why="Kontrak E (frontend→pengguna).", inputs="UI spec", outputs="web/src/components/", files="web/", steps=["Komponen state", "Skenario error mock", "Cek kontras & keyboard"],
  spec="06 kontrak E", ac="Setiap halaman menangani 3 state.", verify="npm test dengan mock error", approval="Tidak")
t("D-P6-007", "Ganti mock → API nyata (lokal)", (1, 2, 4), "D-P6-006:H, C-P6-007:H", rev="C", collab="C",
  obj="Menjalankan dashboard pada API nyata dan menyelesaikan checklist mock-to-real.", why="Milestone integrasi D13.", inputs="API nyata lokal",
  outputs="Checklist mock-to-real terisi", files="web/", steps=["Matikan flag mock", "Bandingkan tiap halaman", "Laporkan ketidakcocokan sebagai CR"],
  spec="06 §mock-to-real", ac="Semua halaman Must berjalan di data nyata tanpa error konsol.", verify="Smoke manual + E2E lokal", approval="Tidak")
t("D-P6-008", "Histogram FRP + perbandingan periode (Should)", (3, 4, 6), "D-P6-007:H, C-P6-010:I", rev="C", prio="Should", obj="Fitur #5 & #7.",
  why="Should; hanya setelah semua Must berjalan.", inputs="Endpoint FRP", outputs="web/src/features/frp/", files="web/", steps=["Komponen", "Catatan metodologi", "Test"],
  spec="C-05", ac="Perbandingan hanya untuk produk/satelit sama.", verify="npm test", approval="Tidak")
t("D-P6-009", "Test frontend (unit/komponen)", (2, 3, 5), "D-P6-006:H", rev="C", obj="Test filter, format tanggal lokal, state.", why="Mutu.",
  inputs="Komponen", outputs="web/src/**/*.test.*", files="web/", steps=["Test filter", "Test format waktu", "CI"], spec="—", ac="Coverage komponen inti tercatat.", verify="npm test di CI", approval="Tidak")
t("X-P6-901", "Integrasi E2E lokal pertama (D13) + paket G6", (0.5, 1, 1.5), "D-P6-007:H, C-P6-008:H, X-P5-901:H", rev="D",
  obj="Demo internal end-to-end lokal; putuskan kontingensi R-14 bila gagal.", why="Titik kritis charter §10.", inputs="Stack lokal",
  outputs="Keputusan G6", files="docs/STATUS.md", steps=["compose up", "ingest", "dashboard"], spec="Checklist G6", ac="Checklist G6 lengkap.",
  verify="Log demo", approval="Tim (G6)", agent="Manusia")
gate("GATE-G6", "X-P6-901:H")

# ---------------------------------------------------------------- PHASE 7
t("C-P7-001", "Skrip smoke E2E stack penuh", (2, 3, 4), "GATE-G6:HA", rev="A", obj="Satu perintah: up → ingest fixture → cek API → cek UI.", why="Regresi integrasi.",
  inputs="Stack", outputs="deploy/scripts/smoke_e2e.*", files="deploy/", steps=["Skrip", "Asersi jumlah", "Dokumentasi"], spec="—",
  ac="Skrip exit 0 di stack sehat dan ≠0 bila komponen mati.", verify="Jalankan dengan service dimatikan sengaja", approval="Tidak")
t("A-P7-001", "Uji idempotensi pada data nyata", (2, 3, 5), "GATE-G5:HA, A-P5-008:H", rev="B", obj="Re-run backfill & poll tumpang tindih → jumlah & agregat identik.",
  why="Kriteria keberhasilan #2.", inputs="Cassandra berisi data", outputs="Laporan idempotensi di pipeline/README.md", files="pipeline/",
  steps=["Snapshot jumlah", "Re-run", "Bandingkan"], spec="O-E1", ac="Selisih 0 baris & 0 agregat.", verify="Harness idempotensi", approval="Tidak")
t("A-P7-002", "Laporan kualitas data per run", (1, 2, 3), "A-P7-001:H", rev="B", obj="Laporan DQ otomatis dari run log & rejected records.", why="Bukti engineering.",
  inputs="Run log", outputs="pipeline/src/.../reports/", files="pipeline/", steps=["Ringkasan per reason code", "Ekspor markdown", "Test"], spec="—",
  ac="Laporan dihasilkan untuk run terakhir.", verify="pytest", approval="Tidak")
t("A-P7-003", "Rekonsiliasi NRT→SP manual (Should)", (2, 3, 5), "A-P7-001:H", rev="B", prio="Should", obj="Perintah manual mengganti NRT dengan SP saat SP tersedia.",
  why="OQ-10 Should.", inputs="Aturan presedensi", outputs="pipeline/src/.../modes/reconcile.py", files="pipeline/", steps=["CLI", "Uji pada tanggal tumpang tindih", "Dokumentasi"],
  spec="A-P1-007", ac="Jumlah per tanggal setelah rekonsiliasi = jumlah SP.", verify="Test integrasi", approval="Operasi penghapusan NRT butuh persetujuan")
t("B-P7-001", "Eksekusi eksperimen bucketing (Must)", (3, 4, 6), "GATE-G5:HA, B-P3-004:H", rev="A", obj="Menjalankan eksperimen sesuai rencana dan menyimpan data mentah hasil.",
  why="O-E3.", inputs="Rencana eksperimen", outputs="experiments/bucketing/", files="experiments/", steps=["Siapkan varian skema di keyspace eksperimen", "Jalankan dengan repetisi", "Simpan hasil mentah"],
  spec="05-experiment-plan.md", ac="Hasil mentah + konfigurasi tersimpan dan dapat dijalankan ulang.", verify="Skrip eksperimen exit 0; hasil ber-timestamp", approval="Tidak")
t("B-P7-002", "Laporan eksperimen", (2, 3, 4), "B-P7-001:H", rev="A", obj="Hipotesis → hasil aktual → interpretasi → keterbatasan.", why="O-E3.",
  inputs="Hasil mentah", outputs="experiments/bucketing/REPORT.md", files="experiments/", steps=["Tabel/grafik dari hasil", "Interpretasi", "Keterbatasan"],
  spec="Tidak mengarang angka", ac="Setiap angka dapat ditelusuri ke file hasil.", verify="Review silang", approval="Kesimpulan analitis: tim")
t("B-P7-003", "Eksperimen replikasi/konsistensi/failure 3 node (Should)", (3, 5, 6), "B-P4-002:H, B-P7-002:S", rev="C", prio="Should",
  obj="Mengamati perilaku RF/CL saat node mati.", why="OQ-14 Should.", inputs="Lingkungan 3 node", outputs="experiments/replication/", files="experiments/",
  steps=["Skenario", "Jalankan", "Laporan"], spec="Dokumen 07", ac="Laporan dengan hasil aktual atau alasan dibatalkan.", verify="Log eksperimen", approval="Tidak")
t("C-P7-002", "Provisioning cloud + deploy pertama", (4, 5, 6), "GATE-G6:HA, C-P3-003:H", rev="B",
  obj="VM tunggal, image yang sama dengan lokal, HTTPS, Cassandra di jaringan privat.", why="Fitur #11 Must.", inputs="Keputusan penyedia (HD-16)",
  outputs="deploy/cloud/", files="deploy/", steps=["Provision", "Deploy compose", "HTTPS + firewall"], spec="ADR-003/004",
  ac="Aplikasi dapat diakses via HTTPS; port Cassandra tertutup dari internet.", verify="Port scan dari luar + curl HTTPS", approval="Persetujuan keamanan & biaya (tim)")
t("C-P7-003", "Poller di cloud + monitoring + restart", (2, 3, 5), "C-P7-002:H, A-P5-007:H", rev="A", obj="Poller berjalan terus, status terlihat, restart otomatis.",
  why="Kriteria keberhasilan #7.", inputs="Mode incremental", outputs="deploy/cloud/ (service poller)", files="deploy/", steps=["Service poller", "Restart policy", "Alarm sederhana via halaman status"],
  spec="R-27", ac="Poll baru tercatat ≥3× berturut-turut di cloud.", verify="Endpoint status", approval="Tidak")
t("C-P7-004", "Checklist keamanan + verifikasi", (2, 3, 4), "C-P7-002:H", rev="B", obj="Port, secret, CORS, rate limit, header.", why="R-25, OQ-26.",
  inputs="ADR-004", outputs="deploy/SECURITY-CHECKLIST.md", files="deploy/", steps=["Cek tiap kontrol", "Bukti", "Perbaikan"], spec="ADR-004",
  ac="Semua kontrol Must lulus dengan bukti.", verify="Port scan, cek header", approval="Tim (keamanan)")
t("D-P7-001", "E2E smoke test UI", (2, 3, 5), "GATE-G6:HA", rev="C", obj="Test otomatis alur utama di browser.", why="Regresi UI.",
  inputs="Stack lokal", outputs="web/e2e/", files="web/e2e/", steps=["Alur ringkasan→ranking→peta", "Filter", "CI opsional"], spec="HD-14 (alat E2E)",
  ac="Alur utama lulus pada stack lokal.", verify="Runner E2E", approval="Tidak")
t("D-P7-002", "Review terminologi ilmiah, disclaimer, aksesibilitas", (1, 2, 3), "GATE-G6:HA", rev="A", obj="Memastikan tidak ada kata 'kebakaran' untuk deteksi; atribusi lengkap.",
  why="R-15.", inputs="UI", outputs="Daftar perbaikan + perbaikan", files="web/", steps=["Grep teks UI", "Cek atribusi", "Perbaiki"], spec="Charter §3",
  ac="0 temuan terminologi terbuka.", verify="Grep string UI", approval="Teks final: tim")
t("A-P7-004", "Hardening & perbaikan bug data (time-box)", (2, 4, 6), "A-P7-001:S", rev="B", nb=17, obj="Perbaikan bug setelah feature freeze.", why="Buffer terencana.",
  inputs="Daftar bug", outputs="PR perbaikan", files="pipeline/", steps=["Triage", "Perbaiki", "Test regresi"], spec="—", ac="0 bug kritis terbuka di area data.",
  verify="CI", approval="Tidak")
t("B-P7-004", "Hardening & perbaikan bug DB (time-box)", (2, 4, 6), "B-P7-002:S", rev="A", nb=17, obj="Perbaikan bug setelah feature freeze.", why="Buffer terencana.",
  inputs="Daftar bug", outputs="PR perbaikan", files="db/", steps=["Triage", "Perbaiki", "Test regresi"], spec="—", ac="0 bug kritis terbuka di area DB.", verify="CI", approval="Tidak")
t("C-P7-005", "Hardening & perbaikan bug API/deploy (time-box)", (2, 4, 6), "C-P7-004:S", rev="D", nb=17, obj="Perbaikan bug setelah feature freeze.", why="Buffer terencana.",
  inputs="Daftar bug", outputs="PR perbaikan", files="api/, deploy/", steps=["Triage", "Perbaiki", "Test regresi"], spec="—", ac="0 bug kritis terbuka di API/deploy.", verify="CI", approval="Tidak")
t("D-P7-003", "Hardening & perbaikan bug UI (time-box)", (2, 4, 6), "D-P7-001:S", rev="C", nb=17, obj="Perbaikan bug setelah feature freeze.", why="Buffer terencana.",
  inputs="Daftar bug", outputs="PR perbaikan", files="web/", steps=["Triage", "Perbaiki", "Test regresi"], spec="—", ac="0 bug kritis terbuka di UI.", verify="CI", approval="Tidak")
t("X-P7-901", "Feature freeze D17", (0.5, 1, 1.5), "C-P7-002:H, C-P7-003:H, D-P7-001:H, A-P7-001:H, B-P7-002:H, C-P7-001:H", rev="C",
  obj="Memastikan semua Must berjalan di cloud; setelah ini hanya perbaikan bug.", why="Charter §10; kontingensi R-23.", inputs="Status Fase 7",
  outputs="Keputusan freeze", files="docs/STATUS.md", steps=["Cek Must di cloud", "Putuskan kontingensi", "Umumkan freeze"], spec="—",
  ac="Daftar Must di cloud: semua berjalan atau keputusan kontingensi tercatat.", verify="Review manual", approval="Tim", agent="Manusia")
t("X-P7-902", "Paket gerbang G7", (0.5, 1, 1.5), "X-P7-901:H, A-P7-004:H, B-P7-004:H, C-P7-005:H, D-P7-003:H, D-P7-002:H, A-P7-002:S", rev="D",
  obj="Mengumpulkan bukti test, eksperimen, deploy.", why="Gerbang ke Fase 8.", inputs="Bukti Fase 7", outputs="Keputusan G7", files="docs/STATUS.md",
  steps=["Kumpulkan bukti", "Persetujuan"], spec="Checklist G7", ac="Checklist G7 lengkap.", verify="Review manual", approval="Tim (G7)", agent="Manusia + agen pencatat")
gate("GATE-G7", "X-P7-902:H")

# ---------------------------------------------------------------- PHASE 8
t("C-P8-001", "Panduan instalasi & reproduksibilitas + uji fresh clone", (2, 3, 4), "GATE-G7:HA", rev="A", obj="README root lengkap; anggota lain menjalankan dari nol.",
  why="O-E4, kriteria #8.", inputs="Seluruh repo", outputs="README.md, docs/08-delivery/api-deploy.md", files="README.md",
  steps=["Tulis panduan", "Reviewer A menjalankan dari clone bersih", "Perbaiki"], spec="—", ac="Fresh clone → dashboard berjalan tanpa bantuan.",
  verify="Log fresh clone oleh reviewer", approval="G8")
t("A-P8-001", "Dokumentasi teknis data (pipeline, DQ, keterbatasan)", (1, 2, 3), "GATE-G7:HA", rev="B", obj="Bab data untuk laporan tim.", why="Kriteria #8.",
  inputs="docs/01-dataset, 03-specs/data, pipeline/", outputs="docs/08-delivery/data.md", files="docs/08-delivery/data.md", steps=["Ringkas", "Diagram", "Keterbatasan"],
  spec="—", ac="Setiap klaim tertaut ke bukti.", verify="Cek tautan", approval="G8")
t("B-P8-001", "Dokumentasi database + hasil eksperimen", (1, 2, 3), "GATE-G7:HA", rev="A", obj="Bab database & eksperimen.", why="Kriteria #8.",
  inputs="db/, experiments/", outputs="docs/08-delivery/database.md", files="docs/08-delivery/database.md", steps=["Model", "Eksperimen", "Keterbatasan"], spec="—",
  ac="Angka eksperimen = file hasil.", verify="Cek tautan", approval="G8")
t("C-P8-002", "Dokumentasi API, deployment, ADR final", (1, 2, 3), "GATE-G7:HA", rev="D", obj="Bab API & deployment.", why="Kriteria #8.",
  inputs="api/, deploy/, ADR", outputs="docs/08-delivery/api-deploy.md", files="docs/08-delivery/api-deploy.md", steps=["API", "Deploy", "Keamanan"], spec="—",
  ac="Tidak ada secret di dokumen.", verify="Grep pola secret", approval="G8")
t("D-P8-001", "Dokumentasi UI + skrip demo + screenshot", (2, 3, 4), "GATE-G7:HA", rev="C", obj="Bab UI dan skrip demo untuk video.", why="Bahan video & presentasi.",
  inputs="Aplikasi di cloud", outputs="docs/08-delivery/ui.md, docs/08-delivery/demo-script.md", files="docs/08-delivery/", steps=["Screenshot", "Skrip demo per fitur", "Catatan disclaimer"],
  spec="—", ac="Skrip demo ≤ durasi video yang disepakati.", verify="Uji baca skrip", approval="G8")
t("D-P8-002", "Checklist penerimaan final + indeks dokumentasi", (1.5, 2, 3), "C-P8-001:H, A-P8-001:H, B-P8-001:H, C-P8-002:H, D-P8-001:H", rev="C",
  obj="Mencentang 8 kriteria keberhasilan dengan bukti dan menyusun indeks dokumentasi.", why="G8.", inputs="Semua dokumen Fase 8",
  outputs="docs/08-delivery/index.md, docs/08-delivery/acceptance-checklist.md", files="docs/08-delivery/", steps=["Checklist", "Indeks", "Daftar keterbatasan"], spec="Charter §7",
  ac="Setiap kriteria punya bukti tertaut.", verify="Cek tautan", approval="G8")
t("X-P8-901", "Perakitan laporan proyek (manusia)", (2, 3, 5), "A-P8-001:S, B-P8-001:S, C-P8-002:S, D-P8-001:S", rev="D", obj="Merakit laporan dari bab tiap peran.",
  why="Deliverable 1; ditangani tim (OQ-01, A-23).", inputs="docs/08-delivery/", outputs="Laporan (di luar repo atau sesuai tim)", files="— (di luar ruang agen)",
  steps=["Kerangka laporan", "Tempel & sunting bab", "Proofread"], spec="Format dari dosen (UNKNOWN)", ac="Disetujui tim.", verify="Review tim", approval="Tim", agent="Manusia saja")
t("A-P8-002", "Perakitan presentasi ≤20 menit (manusia)", (2, 3, 5), "D-P8-001:S", rev="B", obj="Slide; tiap peran menyumbang 1–2 slide.", why="Deliverable 2.",
  inputs="Bab teknis, skrip demo", outputs="Presentasi", files="— (di luar ruang agen)", steps=["Alur cerita", "Slide per peran", "Latihan berwaktu"], spec="≤20 menit",
  ac="Latihan berwaktu ≤20 menit.", verify="Latihan", approval="Tim", agent="Manusia saja")
t("D-P8-003", "Rekam video demo (manusia)", (2, 3, 4), "D-P8-001:H", rev="A", obj="Merekam demo mengikuti skrip.", why="Deliverable 4.",
  inputs="Skrip demo, aplikasi cloud", outputs="Video demo", files="— (di luar ruang agen)", steps=["Rekam", "Sunting", "Cek disclaimer tampil"], spec="—",
  ac="Semua fitur Must terlihat; disclaimer terlihat.", verify="Tonton ulang tim", approval="Tim", agent="Manusia saja")
t("X-P8-902", "Gerbang G8 — penerimaan akhir", (0.5, 1, 1.5), "D-P8-002:H, X-P8-901:S, A-P8-002:S, D-P8-003:S", rev="C", obj="Persetujuan akhir.",
  why="Penutupan proyek.", inputs="Checklist", outputs="Keputusan G8; STATUS final", files="docs/STATUS.md", steps=["Review checklist", "Persetujuan"], spec="Checklist G8",
  ac="Checklist G8 lengkap.", verify="Review manual", approval="Tim (G8)", agent="Manusia")
gate("GATE-G8", "X-P8-902:H")


# ================================================================ REVISION 1 (self-review, 2026-11-19)
# First run: finish D28 > D21, load 80-87 h per role vs 80 h capacity. Causes: serial G1->G2->G3 chain
# (G3 at D12), Phase 1 review load on R1, Phase 3+4 load on R3. Changes below are deliberate and
# documented in 09-risk-capacity-plan.md section 1. Original values are kept in the t() calls above.
# (1) Phase 1 human effort = review/decision only (agent executes the analysis).
# (2) Phase 3 specs start from Phase 2 drafts (soft/hard on artifacts, not on GATE-G2); G3 still needs G2.
# (3) Implementation estimates assume the agent writes code and the human directs, reads and tests it
#     (ASSUMPTION A-EP-01, risk RC-01). (4) Python tooling moved from R3 to R1. (5) Docs tasks merged/smaller.
REV1_EST = {
    "A-P1-001": (0.25, 0.5, 1), "A-P1-002": (0.25, 0.5, 1), "A-P1-003": (0.5, 1, 1.5), "A-P1-004": (0.5, 1, 2),
    "A-P1-005": (0.25, 0.5, 1), "A-P1-006": (0.25, 0.5, 1), "A-P1-007": (0.5, 1, 1.5), "A-P1-008": (0.25, 0.5, 1),
    "A-P1-009": (0.5, 1, 2), "A-P1-010": (0.5, 1, 1.5), "C-P1-001": (1.5, 2, 3),
    "B-P3-002": (2.5, 3.5, 5), "B-P3-003": (1, 2, 3), "B-P3-004": (1.5, 2, 3), "C-P3-001": (2, 3, 4), "C-P3-003": (1.5, 2, 3),
    "C-P4-001": (2, 2.5, 3.5), "D-P4-003": (2, 3, 4), "C-P4-004": (2, 3, 4), "C-P4-005": (1.5, 2, 3), "A-P4-002": (1.5, 2, 3),
    "B-P4-001": (1.5, 2.5, 4), "D-P4-001": (1.5, 2.5, 4), "D-P4-002": (1.5, 2, 3), "A-P4-001": (1.5, 2, 3),
    "A-P5-001": (2, 3, 5), "A-P5-002": (2, 3, 5), "A-P5-003": (1.5, 2.5, 4), "A-P5-004": (2, 3, 5), "A-P5-005": (2, 3, 5),
    "A-P5-006": (2, 3, 4), "A-P5-007": (2, 3, 5), "A-P5-008": (2, 3, 4), "A-P5-009": (0.5, 1, 2), "A-P5-010": (0.5, 1, 1.5),
    "B-P5-001": (1.5, 2, 3), "B-P5-002": (2, 3, 5), "B-P5-003": (2, 3, 5), "B-P5-004": (1.5, 2, 3), "B-P5-005": (1.5, 2.5, 4),
    "B-P5-006": (1.5, 2.5, 4), "B-P5-007": (0.5, 1, 1.5),
    "C-P6-001": (1.5, 2.5, 3.5), "C-P6-002": (1.5, 2, 3), "C-P6-003": (2, 3, 4), "C-P6-004": (1.5, 2.5, 4), "C-P6-005": (2, 3, 4),
    "C-P6-006": (1, 1.5, 2), "C-P6-007": (2, 3.5, 5), "C-P6-008": (2, 3, 4), "C-P6-009": (0.5, 1, 1.5),
    "D-P6-001": (2, 3, 4), "D-P6-002": (2, 3, 5), "D-P6-003": (2, 3, 5), "D-P6-004": (3, 4, 6), "D-P6-005": (1.5, 2, 3),
    "D-P6-006": (1.5, 2, 3), "D-P6-007": (1, 2, 3), "D-P6-009": (1.5, 2.5, 4),
    "A-P7-001": (1.5, 2.5, 4), "A-P7-002": (1, 1.5, 2), "A-P7-003": (2, 3, 4), "B-P7-001": (2, 3.5, 5), "B-P7-002": (1.5, 2.5, 3.5),
    "B-P7-003": (3, 4, 6), "C-P7-001": (1.5, 2, 3), "C-P7-002": (3, 4, 6), "C-P7-003": (1.5, 2.5, 4), "C-P7-004": (1.5, 2, 3),
    "D-P7-001": (2, 3, 4), "D-P7-002": (1, 1.5, 2),
    "A-P7-004": (2, 3, 4), "B-P7-004": (2, 3, 4), "C-P7-005": (2, 3, 4), "D-P7-003": (2, 3, 4),
    "C-P8-001": (1.5, 2, 3), "A-P8-001": (1, 1.5, 2), "B-P8-001": (1, 1.5, 2), "C-P8-002": (1, 1.5, 2), "D-P8-001": (1.5, 2, 3),
    "D-P8-002": (1, 1.5, 2), "X-P8-901": (2, 3, 4), "A-P8-002": (2, 3, 4), "D-P8-003": (1.5, 2.5, 3.5),
}
REV1_DEPS = {
    "D-P2-001": "D-P1-001:H, GATE-G1:S",
    "D-P2-003": "D-P2-002:H, C-P2-001:H, B-P2-001:S",
    "X-P2-901": "D-P2-003:H, A-P2-001:H, B-P2-001:H",
    "C-P2-001": "B-P1-001:H, A-P1-008:S",
    "B-P3-001": "B-P2-001:H",
    "A-P3-001": "A-P1-003:H, A-P2-001:S",
    "C-P3-001": "C-P1-001:S, C-P2-001:S",
    "D-P3-001": "D-P2-001:H, D-P2-002:S",
    "A-P5-002": "A-P5-001:S, A-P3-002:H, GATE-G3:HA, GATE-G4:HA",
    "A-P5-004": "A-P5-002:S, GATE-G3:HA, GATE-G4:HA",
    "B-P5-001": "GATE-G3:HA, GATE-G4:HA, B-P4-001:H",
    "B-P7-003": "B-P4-002:H, B-P7-002:S, GATE-G5:HA",
    "A-P7-004": "A-P7-001:S, GATE-G6:HA", "B-P7-004": "B-P7-002:S, GATE-G6:HA",
    "C-P7-005": "C-P7-004:S, GATE-G6:HA", "D-P7-003": "D-P7-001:S, GATE-G6:HA",
    "A-P8-002": "D-P8-001:S, GATE-G6:HA",
    "X-P8-901": "A-P8-001:S, B-P8-001:S, C-P8-002:S, D-P8-001:S, GATE-G7:HA",
    "X-P3-901": "GATE-G2:HA, A-P3-001:H, A-P3-002:H, B-P3-002:H, B-P3-003:H, C-P3-001:H, C-P3-002:H, D-P3-001:H, B-P3-004:S, C-P3-003:S",
}
for T in TASKS:
    if T["id"] in REV1_EST:
        T["est_v0"] = T["est"]; T["est"] = REV1_EST[T["id"]]
    if T["id"] in REV1_DEPS:
        T["deps_v0"] = T["deps"]; T["deps"] = REV1_DEPS[T["id"]]


# ================================================================ derivations
def role_of(tid):
    r = tid.split("-")[0]
    return COORD if r == X else r


for T in TASKS:
    T["owner"] = role_of(T["id"])
    T["phase"] = T["id"].split("-")[1]
    if T["rev"] is None:
        T["rev"] = DEFAULT_REVIEWER[T["owner"]]
    if T["rev"] == T["owner"]:  # coordinator collision → next role
        T["rev"] = DEFAULT_REVIEWER[T["owner"]]
    o, m, p = T["est"]
    T["te"] = round((o + 4 * m + p) / 6, 2)
    T["var"] = ((p - o) / 6) ** 2
    T["dep_list"] = [tuple(x.strip().split(":")) for x in T["deps"].split(",") if x.strip()]
    T["xid"] = T["id"]  # IDs stay stable; X- = coordination task, owner = current coordinator

ID = {T["id"]: T for T in TASKS}
NODES = list(ID) + list(GATE_DEPS)
GDEPS = {g: [tuple(x.strip().split(":")) for x in d.split(",")] for g, d in GATE_DEPS.items()}


def deps_of(n):
    return ID[n]["dep_list"] if n in ID else GDEPS[n]


def disp(n):
    return ID[n]["xid"] if n in ID else n


# ================================================================ checks
issues = []
for n in NODES:
    for d, ty in deps_of(n):
        if d not in ID and d not in GDEPS:
            issues.append(f"{n}: dependency {d} does not exist")
        if ty not in DEP_TYPES:
            issues.append(f"{n}: bad dependency type {ty}")
for T in TASKS:
    o, m, p = T["est"]
    if not (o <= m <= p):
        issues.append(f"{T['id']}: estimates not ordered")
    if T["rev"] == T["owner"]:
        issues.append(f"{T['id']}: reviewer == owner")
    for f in ("ac", "outputs", "obj"):
        if not T[f]:
            issues.append(f"{T['id']}: missing {f}")
    if m > 6:
        issues.append(f"{T['id']}: most-likely > 6h")
# cycle check (topological order)
indeg = {n: 0 for n in NODES}
succ = collections.defaultdict(list)
for n in NODES:
    for d, ty in deps_of(n):
        succ[d].append((n, ty)); indeg[n] += 1
order, q = [], [n for n in NODES if indeg[n] == 0]
while q:
    n = q.pop(); order.append(n)
    for s, _ in succ[n]:
        indeg[s] -= 1
        if indeg[s] == 0:
            q.append(s)
if len(order) != len(NODES):
    issues.append("CYCLE detected: " + ", ".join(n for n in NODES if indeg[n] > 0))
    print("\n".join(issues)); sys.exit(1)

# ================================================================ PERT critical path (resource-free)
dur = {n: (ID[n]["te"] if n in ID else 0) for n in NODES}
ef = {}
for n in order:
    es = max([ef[d] for d, ty in deps_of(n) if ty != "R"] or [0])
    ef[n] = es + dur[n]


# ================================================================ resource-constrained schedule
def day_of(h):
    return int(h // 4) + 1


rank = {}
for n in reversed(order):
    rank[n] = dur[n] + max([rank[s] for s, ty in succ[n] if ty != "R"] or [0])
busy = {r: [] for r in ROLE}
start, finish, why_start = {}, {}, {}
done = set()
eligible = lambda n: all(d in done for d, _ in deps_of(n))
SHOULD = {T["id"] for T in TASKS if T["prio"] == "Should"}
for _pass in (0, 1):
  pending = set(n for n in NODES if (n in SHOULD) == bool(_pass))
  while pending:
      cand = sorted((n for n in pending if eligible(n)), key=lambda n: -rank[n])
      if not cand:
          sys.exit("DEADLOCK: a Must task depends on a Should task: " + ", ".join(sorted(pending)))
      n = cand[0]
      est, cause = START_HOUR, "start"
      for d, ty in deps_of(n):
          if ty in ("S", "R"):
              continue
          f = finish[d]
          if d in GDEPS or ty == "HA":
              f = math.ceil(f / 4 - 1e-9) * 4      # approval at end of day, successor starts next day
          if f > est:
              est, cause = f, d
      if n in ID and ID[n]["nb"]:
          nbh = (ID[n]["nb"] - 1) * 4
          if nbh > est:
              est, cause = nbh, f"not-before D{ID[n]['nb']}"
      if n in GDEPS:
          start[n] = finish[n] = est
      else:
          r, du = ID[n]["owner"], dur[n]
          s = est                                    # per-day capacity: hours_on(r, day)
          for (a, b) in sorted(busy[r]):
              if advance(r, s, du) <= a + 1e-9:
                  break
              if b > s:
                  if s < est + 1e-9 and b > est:
                      cause = f"resource {r}"
                  s = max(s, b)
          e = advance(r, s, du)
          busy[r].append((s, e)); start[n], finish[n] = s, e
      why_start[n] = cause
      done.add(n); pending.discard(n)

end_h = finish["GATE-G8"]
warnings = []
# gate ancestry: implementation/test/delivery phases must wait for their gates (via H/I/HA edges)
anc = {}
for n in order:
    st = set()
    for d, ty in deps_of(n):
        if ty in ("H", "I", "HA"):
            st |= {d} | anc[d]
    anc[n] = st
NEED = {"P5": [{"GATE-G3"}, {"GATE-G4"}], "P6": [{"GATE-G3"}, {"GATE-G4"}],
        "P7": [{"GATE-G5", "GATE-G6"}], "P8": [{"GATE-G6", "GATE-G7"}]}
for T in TASKS:
    for alts in NEED.get(T["phase"], []):
        if not (alts & anc[T["id"]]):
            issues.append(f"{T['id']}: does not wait for {'/'.join(sorted(alts))}")
    for d, ty in T["dep_list"]:
        if T["prio"] == "Must" and d in ID and ID[d]["prio"] == "Should":
            issues.append(f"{T['id']}: Must depends on Should {d}")
for T in TASKS:
    if T["prio"] == "Should":
        dl = 16 if T["phase"] in ("P4", "P5", "P6") else 19
        f_day = int((finish[T["id"]] - 1e-9) // 4) + 1
        if f_day > dl:
            warnings.append(f"{T['id']} (Should) selesai D{f_day} > D{dl}: kandidat pertama untuk dipotong")
for T in TASKS:
    n = T["id"]
    T["s_day"], T["f_day"] = day_of(start[n]), day_of(finish[n] - 1e-9)
    T["s_date"] = (D1 + dt.timedelta(days=T["s_day"] - 1)).isoformat()
    T["f_date"] = (D1 + dt.timedelta(days=T["f_day"] - 1)).isoformat()
    if T["f_day"] > LAST_DAY and T["prio"] == "Must":
        issues.append(f"{n}: finishes D{T['f_day']} > D{LAST_DAY}")
    if T["prio"] == "Must" and T["phase"] in ("P5", "P6") and T["f_day"] > 16:
        issues.append(f"{n}: Must feature task finishes after D16 (freeze D17)")

# critical chain (resource-constrained): backtrack causes
chain, n = [], "GATE-G8"
while n and n != "start":
    chain.append(n)
    c = why_start[n]
    if c.startswith("resource"):
        r = c.split()[1]
        prev = [m for m in ID if ID[m]["owner"] == r and abs(finish[m] - start[n]) < 1e-6]
        n = prev[0] if prev else None
    elif c.startswith("not-before") or c == "start":
        chain.append(c); n = None
    else:
        n = c
chain = list(reversed(chain))
crit = set(chain)
cp_tasks = [c for c in chain if c in ID]
sigma = math.sqrt(sum(ID[c]["var"] for c in cp_tasks))

# file ownership conflict check: task 'files' must lie in its owner's dirs
def owned(path, r):
    dirs = ROLE_DIRS[r] + (COORD_DIRS if r == COORD else [])
    p = path.strip().split(" ")[0]
    if p.startswith("—") or p.startswith("data/"):
        return True
    for d in dirs:
        dd = d.split(" ")[0]
        if dd.endswith("*.yml") and p.startswith("docker-compose"):
            return True
        if p == dd or p.startswith(dd.rstrip("/") + "/") or (dd.endswith("/") and p.startswith(dd)):
            return True
    return False

for T in TASKS:
    for f in T["files"].split(","):
        if f.strip() and not owned(f, T["owner"]):
            issues.append(f"{T['id']}: file '{f.strip()}' outside owner {T['owner']} area")

# ================================================================ outputs
FIELDS = ["task_id", "legacy_id", "phase_id", "phase_name", "title", "objective", "reason", "primary_owner", "owner_role_code",
          "accountable_owner", "responsible_executor", "required_approver",
          "reviewer", "collaborating_roles", "priority", "status", "effort_optimistic_h", "effort_most_likely_h", "effort_pessimistic_h",
          "effort_pert_h", "required_inputs", "dependencies", "expected_outputs", "files_owned", "files_allowed_to_modify",
          "files_must_not_modify", "execution_steps", "technical_specification", "acceptance_criteria", "automated_verification",
          "required_test_evidence", "human_approval", "handoff_requirements", "definition_of_done", "agent_mode",
          "planned_start", "planned_finish", "on_critical_chain"]


def handoff_text(T):
    outs = [s for s, ty in succ[T["id"]] if s in ID and ID[s]["owner"] != T["owner"]]
    if T["handoff"]:
        return T["handoff"]
    if not outs:
        return "Tidak ada serah-terima lintas peran (konsumen internal peran sendiri)."
    who = sorted({ID[s]["owner"] for s in outs})
    return (f"Serahkan '{T['outputs']}' ke {', '.join(ROLE[w][0] for w in who)} untuk {', '.join(disp(s) for s in outs)}. "
            "Diterima bila PR disetujui reviewer DAN konsumen mengonfirmasi artefak cukup (lihat 03-dependency-matrix.md).")


def allowed(T):
    r = T["owner"]
    return "; ".join(ROLE_DIRS[r] + (COORD_DIRS if r == COORD else []))


def prohibited(T):
    r = T["owner"]
    other = [d for k, v in ROLE_DIRS.items() if k != r for d in v if not d.startswith("data/")]
    if r != COORD:
        other += COORD_DIRS
    return "; ".join(ALWAYS_PROHIBITED + other)


rows = []
for T in TASKS:
    deps = "; ".join(f"{disp(d)} ({DEP_TYPES[ty]})" for d, ty in T["dep_list"]) or "—"
    rows.append({
        "task_id": T["xid"], "legacy_id": T["legacy"], "phase_id": T["phase"], "phase_name": PHASES[T["phase"]], "title": T["title"],
        "objective": T["obj"], "reason": T["why"], "primary_owner": f"Role {T['owner']}", "owner_role_code": ROLE[T["owner"]][0],
        "accountable_owner": f"Role {T['owner']} ({ROLE[T['owner']][0]})", "responsible_executor": f"Anggota pemegang {ROLE[T['owner']][0]} — {T['agent']}",
        "required_approver": T["approval"] if T["approval"] not in ("Tidak", "Tidak (review PR cukup)") else f"Reviewer Role {T['rev']} (persetujuan PR)",
        "reviewer": f"Role {T['rev']} ({ROLE[T['rev']][0]})", "collaborating_roles": T["collab"] or "—", "priority": T["prio"], "status": T["status"],
        "effort_optimistic_h": T["est"][0], "effort_most_likely_h": T["est"][1], "effort_pessimistic_h": T["est"][2], "effort_pert_h": T["te"],
        "required_inputs": T["inputs"], "dependencies": deps, "expected_outputs": T["outputs"], "files_owned": T["files"],
        "files_allowed_to_modify": allowed(T), "files_must_not_modify": prohibited(T), "execution_steps": " | ".join(f"{i+1}. {s}" for i, s in enumerate(T["steps"])),
        "technical_specification": T["spec"], "acceptance_criteria": T["ac"], "automated_verification": T["verify"] or "Review manual",
        "required_test_evidence": T["evidence"] or "Output perintah verifikasi ditempel di deskripsi PR + tautan review",
        "human_approval": T["approval"], "handoff_requirements": handoff_text(T),
        "definition_of_done": "DoD umum (10-phase-gates.md §3) + kriteria penerimaan tugas ini terpenuhi dengan bukti",
        "agent_mode": T["agent"], "planned_start": f"D{T['s_day']} ({T['s_date']})", "planned_finish": f"D{T['f_day']} ({T['f_date']})",
        "on_critical_chain": "yes" if T["id"] in crit else "no",
    })
with open(os.devnull if SCENARIO else OUT / "02-work-breakdown-structure.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)

HDR = ("> **File hasil generator** — jangan diedit manual. Sumber: `tools/build_plan.py`. "
       f"Koordinator integrasi yang dipakai: Role {COORD} ({ROLE[COORD][0]}) (HD-02, disetujui GATE-EP 2026-11-19). Kapasitas: HD-03 + HD-07(b).\n")

# ---- 02 md
L = ["# 02 — Work Breakdown Structure", "", HDR,
     "Status: `RECOMMENDATION` — menunggu GATE-EP. Estimasi dalam **jam kerja manusia** (termasuk mengarahkan dan me-review agen). "
     "PERT = (O + 4M + P) / 6. Tanggal = hasil penjadwalan berkapasitas (05-project-schedule.md).", "",
     "Kode peran: **A = R1** Data/ETL · **B = R2** Cassandra · **C = R3** Backend & DevOps · **D = R4** Frontend & Delivery. "
     f"Tugas bernomor 9xx adalah tugas koordinasi (saat ini Role {COORD}).", "",
     "Kolom yang sama untuk semua tugas dan tidak diulang di detail: *files allowed to modify* = area peran pemilik "
     "(07-file-ownership-matrix.md); *files must not modify* = area peran lain + `.env` + `docs/00-discovery/`; "
     "*Definition of Done* = DoD umum (10-phase-gates.md §3). Versi lengkap per tugas ada di CSV.", ""]
for ph, name in PHASES.items():
    ts = [T for T in TASKS if T["phase"] == ph]
    L += [f"## {ph} — {name}", "", "| ID | Judul | Pemilik | Reviewer | Prio | O/M/P → PERT (j) | Dependensi | Rencana | Status |", "|---|---|---|---|---|---|---|---|---|"]
    for T in ts:
        deps = ", ".join(f"{disp(d)}·{ty}" for d, ty in T["dep_list"]) or "—"
        cc = " ⚑" if T["id"] in crit else ""
        L.append(f"| **{T['xid']}**{cc} | {T['title']} | {T['owner']} ({ROLE[T['owner']][0]}) | {T['rev']} | {T['prio']} | "
                 f"{T['est'][0]}/{T['est'][1]}/{T['est'][2]} → {T['te']} | {deps} | D{T['s_day']}–D{T['f_day']} | {T['status']} |")
    L += ["", "⚑ = berada di rantai kritis.", ""]
    for T in ts:
        L += [f"### {T['xid']} — {T['title']}", "",
              f"- **Fase / prioritas / status:** {ph} · {T['prio']} · {T['status']}" + (f" · ID lama {T['legacy']}" if T["legacy"] else ""),
              f"- **Tujuan:** {T['obj']}", f"- **Alasan:** {T['why']}",
              f"- **Pemilik (A) & pelaksana (R):** Role {T['owner']} ({ROLE[T['owner']][0]}) · **Reviewer:** Role {T['rev']} · **Kolaborator (C):** {T['collab'] or '—'}",
              f"- **Estimasi:** O {T['est'][0]} / M {T['est'][1]} / P {T['est'][2]} → PERT {T['te']} jam · **Rencana:** D{T['s_day']} ({T['s_date']}) – D{T['f_day']} ({T['f_date']})",
              f"- **Input:** {T['inputs'] or '—'}",
              f"- **Dependensi:** " + ("; ".join(f"{disp(d)} ({DEP_TYPES[ty]})" for d, ty in T['dep_list']) or "—"),
              f"- **Output:** {T['outputs']}", f"- **File dimiliki:** `{T['files']}`",
              "- **Langkah:** " + " → ".join(T["steps"]),
              f"- **Spesifikasi teknis:** {T['spec'] or '—'}", f"- **Kriteria penerimaan:** {T['ac']}",
              f"- **Verifikasi otomatis:** {T['verify'] or 'Review manual'}", f"- **Bukti test:** {T['evidence'] or 'Output verifikasi di PR + tautan review'}",
              f"- **Persetujuan manusia:** {T['approval']}", f"- **Serah-terima:** {handoff_text(T)}", f"- **Mode agen:** {T['agent']}", ""]
wr(OUT / "02-work-breakdown-structure.md", "\n".join(L))

# ---- 03 dependency matrix
FALLBACK = {
    "H": "Pemilik prasyarat memberi tahu koordinator di standup; koordinator memutuskan realokasi atau pemotongan Should. Tugas dependen TIDAK dimulai.",
    "S": "Lanjut dengan asumsi/mock terdokumentasi; catat asumsi di PR; validasi ulang saat prasyarat selesai.",
    "I": "Lanjut memakai versi kontrak terakhir yang disetujui + mock; perubahan kontrak hanya lewat change request.",
    "R": "Pekerjaan boleh lanjut, tetapi tidak boleh di-merge/diterima sebelum review.",
    "HA": "STOP. Tunggu keputusan tim; koordinator menagih keputusan paling lambat akhir hari.",
}
L = ["# 03 — Dependency Matrix", "", HDR,
     "Jenis: **Hard** (tidak bisa jalan), **Soft** (boleh jalan dengan asumsi/mock), **Interface** (boleh jalan setelah kontrak disetujui), "
     "**Review** (boleh jalan, tidak boleh diterima sebelum review), **Human approval** (berhenti sampai tim memutuskan).", "",
     "Aturan umum *dependency satisfied*: tugas prasyarat memenuhi DoD (PR di-merge setelah review) — untuk Interface: kontrak versi tersebut disetujui di gerbang; "
     "untuk gerbang: keputusan tim tercatat di STATUS.md.", "",
     "## 1. Gerbang fase", "", "| Gerbang | Deskripsi | Prasyarat |", "|---|---|---|"]
for g, (ph, desc) in GATES.items():
    L.append(f"| {g} | {desc} | {', '.join(disp(d) for d, _ in GDEPS[g])} |")
L += ["", "## 2. Dependensi lintas peran (handoff)", "",
      "| Dari (prasyarat) | Pemilik | Ke (dependen) | Pemilik | Jenis | Artefak yang diserahkan | Validator | Jika terlambat |", "|---|---|---|---|---|---|---|---|"]
for T in TASKS:
    for d, ty in T["dep_list"]:
        if d in ID and ID[d]["owner"] != T["owner"]:
            P = ID[d]
            L.append(f"| {P['xid']} | {P['owner']} | {T['xid']} | {T['owner']} | {DEP_TYPES[ty]} | {P['outputs']} | Role {T['owner']} (konsumen) + reviewer {P['rev']} | {FALLBACK[ty]} |")
L += ["", "## 3. Dependensi dalam peran yang sama", "", "| Dari | Ke | Peran | Jenis |", "|---|---|---|---|"]
for T in TASKS:
    for d, ty in T["dep_list"]:
        if d in ID and ID[d]["owner"] == T["owner"]:
            L.append(f"| {ID[d]['xid']} | {T['xid']} | {T['owner']} | {DEP_TYPES[ty]} |")
L += ["", "## 4. Dependensi ke gerbang (blocking)", "", "| Gerbang | Tugas yang menunggu |", "|---|---|"]
for g in GATES:
    w = [disp(s) for s, ty in succ[g]]
    L.append(f"| {g} | {', '.join(w) or '—'} |")
L += ["", "## 5. Perlakuan bila dependensi terlambat (default per jenis)", "", "| Jenis | Tindakan |", "|---|---|"]
L += [f"| {DEP_TYPES[k]} | {v} |" for k, v in FALLBACK.items()]
wr(OUT / "03-dependency-matrix.md", "\n".join(L) + "\n")

# ---- 04 mermaid
M = ["%% NusaFire dependency graph — generated by tools/build_plan.py (do not edit)",
     "%% Edges: --> hard, -.-> soft/review, ==> interface, --o human approval (gate). Red nodes = critical chain.",
     "flowchart LR"]
for ph, name in PHASES.items():
    M.append(f'  subgraph {ph}["{ph} {name}"]')
    M.append("    direction TB")
    for T in TASKS:
        if T["phase"] == ph:
            M.append(f'    {T["id"].replace("-", "_")}["{T["xid"]}<br/>{T["title"][:38]}"]:::r{T["owner"]}')
    for g, (gph, _) in GATES.items():
        if gph == ph:
            M.append(f'    {g.replace("-", "_")}{{{{"{g}"}}}}:::gate')
    M.append("  end")
arrow = {"H": "-->", "S": "-.->", "R": "-.->", "I": "==>", "HA": "--o"}
for n in NODES:
    for d, ty in deps_of(n):
        M.append(f"  {d.replace('-', '_')} {arrow[ty]} {n.replace('-', '_')}")
M += ["  classDef rA fill:#dbeafe,stroke:#1d4ed8,color:#111", "  classDef rB fill:#dcfce7,stroke:#15803d,color:#111",
      "  classDef rC fill:#fef3c7,stroke:#b45309,color:#111", "  classDef rD fill:#fce7f3,stroke:#be185d,color:#111",
      "  classDef gate fill:#e5e7eb,stroke:#374151,color:#111", "  classDef crit stroke:#dc2626,stroke-width:3px"]
M.append("  class " + ",".join(c.replace("-", "_") for c in chain if c in ID or c in GDEPS) + " crit")
wr(OUT / "04-dependency-graph.mmd", "\n".join(M) + "\n")

# ---- 05 schedule
load = {r: collections.Counter() for r in ROLE}
for T in TASKS:
    load[T["owner"]][T["phase"]] += T["te"]
capacity = {r: sum(hours_on(r, d) for d in range(START_HOUR // 4 + 1, LAST_DAY + 1)) for r in ROLE}
L = ["# 05 — Project Schedule", "", HDR,
     f"Kalender: D1 = {D1} … D{LAST_DAY} = {D1 + dt.timedelta(days=LAST_DAY - 1)} (A-22, `ASSUMPTION`). Penjadwalan mulai **D2**; D1 dipakai untuk Fase 0 dan awal Fase 1 (dikerjakan agen).",
     "Kapasitas (GATE-EP, HD-03 + HD-07b): 4 jam/hari/orang setiap hari termasuk akhir pekan; **R1 dan R3 ±5 jam/hari pada D9–D15** (rantai kritis). Opsi (c) potong *Should* tetap menjadi cadangan.",
     "Metode: penjadwalan berbasis sumber daya (satu orang per peran, 4 jam kerja = 1 hari), prioritas = jalur terpanjang ke akhir, durasi = PERT. "
     "Persetujuan gerbang dianggap selesai di akhir hari; tugas yang menunggu gerbang mulai keesokan harinya.", "",
     "## 1. Milestone", "", "| Milestone | Rencana (hasil jadwal) | Target charter |", "|---|---|---|"]
targets = {"GATE-EP": "D2", "GATE-G1": "D2–D3", "GATE-G2": "D3–D5", "GATE-G3": "D5", "GATE-G4": "D5", "GATE-G5": "D10–D12",
           "GATE-G6": "D13 (integrasi lokal pertama)", "GATE-G7": "D19", "GATE-G8": "D21"}
for g in GATES:
    dday = day_of(finish[g] - 1e-9) if finish[g] > 0 else 1
    L.append(f"| {g} — {GATES[g][1]} | D{dday} ({(D1 + dt.timedelta(days=dday - 1)).isoformat()}) | {targets[g]} |")
fz = [T for T in TASKS if T["id"] == "X-P7-901"][0]
L += [f"| Feature freeze (X-P7-901) | D{fz['f_day']} | D17 |", "",
      "## 2. Beban kerja per peran (jam PERT)", "", "| Peran | " + " | ".join(PHASES) + " | Total | Kapasitas D2–D21 | Utilisasi |", "|---|" + "---|" * (len(PHASES) + 3)]
for r in ROLE:
    tot = sum(load[r].values())
    L.append(f"| {r} ({ROLE[r][0]}){' + koordinator' if r == COORD else ''} | " + " | ".join(f"{load[r][p]:.1f}" for p in PHASES) +
             f" | **{tot:.1f}** | {capacity[r]} | {tot / capacity[r] * 100:.0f}% |")
tot_all = sum(sum(v.values()) for v in load.values())
L += [f"| **Tim** | " + " | ".join(f"{sum(load[r][p] for r in ROLE):.1f}" for p in PHASES) + f" | **{tot_all:.1f}** | {sum(capacity.values())} | {tot_all / sum(capacity.values()) * 100:.0f}% |", "",
      "Sisa kapasitas = **buffer** (lihat §6). Angka ini termasuk tugas *Should*; tanpa Should, beban turun sebesar kolom Should di §6.", ""]
should = {r: sum(T["te"] for T in TASKS if T["owner"] == r and T["prio"] == "Should") for r in ROLE}
L += ["## 3. Rantai kritis (resource-constrained)", "",
      "Rantai di bawah ditelusuri mundur dari GATE-G8: setiap langkah adalah prasyarat atau pekerjaan sebelumnya pada orang yang sama yang menentukan waktu mulai.", ""]
L += ["```text", " → ".join(disp(c) for c in chain), "```", "",
      f"Selesai rencana: **D{day_of(end_h - 1e-9)}**. Simpangan baku PERT gabungan rantai kritis ≈ **{sigma:.1f} jam** (≈ {sigma / 4:.1f} hari kerja satu orang).",
      f"Jalur terpanjang tanpa batas sumber daya (dependensi murni): {max(ef.values()):.1f} jam kerja berurutan.", "",
      "## 4. Gantt (Mermaid)", "", "```mermaid", "gantt", "  title NusaFire — rencana per peran (PROVISIONAL)", "  dateFormat YYYY-MM-DD", "  axisFormat %d/%m",
      ]
for r in ROLE:
    L.append(f"  section {r} {ROLE[r][0]}")
    for T in sorted((T for T in TASKS if T["owner"] == r), key=lambda T: start[T["id"]]):
        tag = "crit, " if T["id"] in crit else ""
        days = T["f_day"] - T["s_day"] + 1
        nm = "".join(ch for ch in T['title'][:28] if ch not in ':;,#')
        L.append(f"  {T['xid']} {nm} :{tag}{T['id'].replace('-', '')}, {T['s_date']}, {days}d")
L += ["  section Gerbang"]
for g in GATES:
    dday = max(1, day_of(finish[g] - 1e-9))
    L.append(f"  {g} :milestone, {g.replace('-', '')}, {(D1 + dt.timedelta(days=dday - 1)).isoformat()}, 0d")
L += ["```", "", "## 5. Jadwal harian per peran", "", "| Hari | Tanggal | A (R1) | B (R2) | C (R3) | D (R4) | Gerbang |", "|---|---|---|---|---|---|---|"]
for d in range(1, LAST_DAY + 1):
    cells = []
    for r in ROLE:
        ts = [T["xid"] for T in TASKS if T["owner"] == r and T["s_day"] <= d <= T["f_day"]]
        cells.append(", ".join(ts) or "*(buffer)*")
    gs = [g for g in GATES if max(1, day_of(finish[g] - 1e-9)) == d]
    L.append(f"| D{d} | {(D1 + dt.timedelta(days=d - 1)).isoformat()} | " + " | ".join(cells) + f" | {', '.join(gs) or ''} |")
L += ["", "## 6. Buffer", "", "| Peran | Beban total | Di antaranya Should | Buffer (kapasitas − beban) |", "|---|---|---|---|"]
for r in ROLE:
    tot = sum(load[r].values())
    L.append(f"| {r} | {tot:.1f} | {should[r]:.1f} | {capacity[r] - tot:.1f} |")
L += ["", "Tugas *Should* yang tidak muat sebelum batasnya (lintasan kedua, hanya mengisi celah):", ""] + [f"- {w}" for w in warnings] + ["", "Buffer eksplisit tambahan: tugas *hardening* time-box D17–D19 (A-P7-004, B-P7-004, C-P7-005, D-P7-003).", "",
      "## 7. Kontingensi (dipicu di checkpoint)", "",
      "| Checkpoint | Pemicu | Tindakan (urutan) |", "|---|---|---|",
      "| D3 | G1 belum disetujui | Fase 2 lanjut dengan asumsi periode 1 tahun; Fase 4 tetap jalan (tidak bergantung dataset). |",
      "| D6 | G3 belum disetujui | Fase 5/6 hanya mengerjakan bagian yang kontraknya sudah disetujui; sisanya tunggu. Potong B-P4-002 (Should). |",
      "| D10 | Belum ada data nyata di Cassandra (R-14) | Aktifkan kontingensi R-14: pairing A+B pada loader; C/D tetap di mock; potong semua Should Fase 6. |",
      "| D13 | Integrasi lokal gagal | Freeze fitur Should; C membantu integrasi; deploy cloud mundur maksimal ke D15. |",
      "| D17 | Deploy cloud belum berhasil (R-23) | Kontingensi R-23: demo lokal + rekaman; cloud jadi upaya terbaik sampai D19. |",
      "| Kapan saja | Anggota tidak tersedia >1 hari (R-18) | Reviewer peran tersebut mengambil alih tugas di jalur kritis; urutan pemotongan sesuai D-P2-003. |", ""]
wr(OUT / "05-project-schedule.md", "\n".join(L) + "\n")

# ---- prompt consistency: every task ID of a role appears in that role's prompt (ranges "X-P5-001…X-P5-010" expand)
import re
PROMPTS = {"A": "role-a-data-engineering.md", "B": "role-b-cassandra-engineering.md",
           "C": "role-c-backend-engineering.md", "D": "role-d-frontend-delivery.md"}
for r, fn in PROMPTS.items():
    fp = OUT / "11-role-prompts" / fn
    if not fp.exists():
        issues.append(f"prompt missing: {fn}"); continue
    txt = fp.read_text(encoding="utf-8")
    ids = set(re.findall(r"\b[ABCDX]-P\d-\d{3}\b", txt))
    for m in re.finditer(r"\b([ABCDX])-P(\d)-(\d{3})…\1-P\2-(\d{3})\b", txt):
        for k in range(int(m.group(3)), int(m.group(4)) + 1):
            ids.add(f"{m.group(1)}-P{m.group(2)}-{k:03d}")
    own = {T["id"] for T in TASKS if T["owner"] == r and not T["id"].startswith("X-")}
    if r == COORD:
        own |= {T["id"] for T in TASKS if T["id"].startswith("X-")}
    for tid in sorted(own - ids):
        issues.append(f"prompt {fn}: missing own task {tid}")
    for tid in sorted(i for i in ids if i.startswith(r + "-") and i not in ID):
        issues.append(f"prompt {fn}: unknown task {tid}")

# ---- 13 progress tracker. Structure is generated once; checkbox state and the "bukti"/"disetujui" fields are edited
# by people and agents and are never overwritten. Each run only rewrites the summary between the markers and checks it.
TRACKER = OUT / "13-progress-tracker.md"
S_START, S_END = "<!-- progress:summary:start -->", "<!-- progress:summary:end -->"
LINE_RE = re.compile(r"^- \[( |x|X)\] \*\*([ABCDX]-P\d-\d{3}|GATE-[A-Z0-9]+)\*\*(.*)$")
EMPTY = {"", "—", "-"}


def owner_label(T):
    return f"Koordinator ({ROLE[T['owner']][0]})" if T["id"].startswith("X-") else ROLE[T["owner"]][0]


def tracker_line(n):
    if n in GATES:
        return f"- [ ] **{n}** {GATES[n][1]} · bukti: — · disetujui: —"
    T = ID[n]
    extra = (" (Should)" if T["prio"] == "Should" else "") + (" · *manusia saja*" if T["agent"] == "Manusia saja" else "")
    return f"- [ ] **{n}** {T['title']}{extra} · {owner_label(T)} → review {ROLE[T['rev']][0]} · bukti: — · disetujui: —"


SECTIONS = [(f"Role {r} ({ROLE[r][0]})", [T for T in TASKS if T["id"].startswith(r + "-")]) for r in "ABCD"]
SECTIONS.append(("Koordinator integrasi (tugas X-)", [T for T in TASKS if T["id"].startswith("X-")]))

if not TRACKER.exists():
    L = ["# 13 — Progress Tracker", "",
         "> Catatan progres **hidup** untuk setiap task ID di [WBS](02-work-breakdown-structure.md) dan setiap gerbang.",
         "> Kolom `status` di WBS adalah potret saat rencana disusun (D1); untuk progres, file ini yang berlaku.",
         "> Struktur dibuat oleh `tools/build_plan.py`. Setiap run hanya memperbarui blok **Ringkasan** dan memeriksa",
         "> konsistensi; centang dan isian di baris tugas tidak pernah ditimpa.", "",
         "## Cara memakai", "",
         "| Tanda | Arti | Siapa yang mengisi |", "|---|---|---|",
         "| `- [x]` | Pekerjaan implementer selesai: kriteria penerimaan terpenuhi, bukti ada, PR dibuka (DoD 1–4) | Implementer (agen atau manusia), **di PR tugas itu sendiri** |",
         "| `bukti: …` | Link PR / hash commit / path artefak + tanggal, mis. `PR #12, 2026-11-21` | Implementer |",
         "| `disetujui: …` | Reviewer manusia menyetujui → tugas **Done** (DoD lengkap), mis. `Member 2, 2026-11-22` | **Hanya manusia** (reviewer/tim) |",
         "",
         "Aturan:",
         "1. Ubah **hanya baris tugasmu sendiri**. Jangan mengubah teks judul, ID, urutan, atau baris peran lain.",
         "2. Agen **tidak pernah** menyetujui sendiri dan tidak mencentang tugas *manusia saja*. Agen hanya boleh mengisi `disetujui:` untuk mencatat persetujuan yang dinyatakan langsung oleh manusia, dengan menyebut siapa, kapan, dan di mana.",
         "3. Baris gerbang: `[x]` = paket gerbang siap (koordinator); `disetujui:` = keputusan tim + tautan ke STATUS.md.",
         "4. Bila PR ditolak dan pekerjaan dibuka kembali, hapus centang dan tulis alasannya di `bukti:`.",
         "5. Konflik merge di file ini: pertahankan kedua perubahan (setiap baris milik satu tugas).",
         "6. Setelah mengubah file ini, jalankan `python -I docs/10-execution-plan/tools/build_plan.py` (harus `ISSUES: 0`).",
         "", "## Ringkasan", "", S_START, S_END, "", "## Gerbang", ""]
    L += [tracker_line(g) for g in GATES]
    for title, ts in SECTIONS:
        L += ["", f"## {title}"]
        for ph in PHASES:
            sub = [T for T in ts if T["phase"] == ph]
            if sub:
                L += ["", f"### {ph} — {PHASES[ph]}", ""] + [tracker_line(T["id"]) for T in sub]
    wr(TRACKER, "\n".join(L) + "\n")

if TRACKER.exists():
    text = TRACKER.read_text(encoding="utf-8")
    state, seen = {}, collections.Counter()
    for ln in text.splitlines():
        m = LINE_RE.match(ln)
        if not m:
            continue
        n, rest = m.group(2), m.group(3)
        seen[n] += 1
        fm = re.search(r"· bukti: (.*?) · disetujui: (.*)$", rest)
        if not fm:
            issues.append(f"tracker {n}: baris tidak berformat '· bukti: … · disetujui: …'")
            continue
        state[n] = dict(done=m.group(1) != " ", ev=fm.group(1).strip(), ok=fm.group(2).strip() not in EMPTY)
    missing = [n for n in list(GATES) + [T["id"] for T in TASKS] if n not in seen]
    for n, c in seen.items():
        if n not in ID and n not in GATES:
            issues.append(f"tracker: ID tidak dikenal di WBS: {n}")
        elif c > 1:
            issues.append(f"tracker: {n} muncul {c}x")
    for n, st in state.items():
        if st["ok"] and not st["done"]:
            issues.append(f"tracker {n}: 'disetujui' terisi tetapi belum dicentang")
        if st["done"] and st["ev"] in EMPTY:
            warnings.append(f"tracker {n}: dicentang tanpa bukti")
    if missing:  # new WBS tasks are appended so nothing is lost; coordinator moves them into place
        hdr = "## Belum ditempatkan (pindahkan ke bagian perannya)"
        text = (text.rstrip("\n") + ("\n" if hdr in text else f"\n\n{hdr}\n\n")
                + "\n".join(tracker_line(n) for n in missing) + "\n")
        warnings.append(f"tracker: {len(missing)} ID baru ditambahkan di bagian 'Belum ditempatkan'")
        for n in missing:
            state[n] = dict(done=False, ev="—", ok=False)

    def cnt(ns):
        ns = list(ns)
        ok = sum(state.get(n, {}).get("ok", False) and state.get(n, {}).get("done", False) for n in ns)
        done = sum(state.get(n, {}).get("done", False) for n in ns)
        return f"{ok} / {done} / {len(ns)}"

    S = ["Format sel: **disetujui (Done) / dicentang / total**. Diperbarui otomatis oleh `tools/build_plan.py`.", "",
         "| Bagian | " + " | ".join(PHASES) + " | Semua |", "|---" * (len(PHASES) + 2) + "|"]
    for title, ts in SECTIONS:
        cells = [cnt(T["id"] for T in ts if T["phase"] == ph) if any(T["phase"] == ph for T in ts) else "·"
                 for ph in PHASES]
        S.append(f"| {title} | " + " | ".join(cells) + f" | **{cnt(T['id'] for T in ts)}** |")
    S.append("| **Tim** | " + " | ".join(cnt(T["id"] for T in TASKS if T["phase"] == ph) for ph in PHASES)
             + f" | **{cnt(ID)}** |")
    S += ["", "Gerbang disetujui: " + (", ".join(g for g in GATES if state.get(g, {}).get("ok") and state.get(g, {}).get("done")) or "belum ada") + "."]
    wait = [n for n in ID if state.get(n, {}).get("done") and not state.get(n, {}).get("ok")]
    S.append("Menunggu review manusia: " + (", ".join(wait) if wait else "tidak ada") + ".")
    if S_START in text and S_END in text:
        i, j = text.index(S_START) + len(S_START), text.index(S_END)
        wr(TRACKER, text[:i] + "\n" + "\n".join(S) + "\n" + text[j:])
    else:
        issues.append("tracker: penanda ringkasan hilang")
    print("progress (disetujui/dicentang/total):", cnt(ID))

# ---- console summary
print("tasks", len(TASKS), "gates", len(GATES), "edges", sum(len(deps_of(n)) for n in NODES))
for r in ROLE:
    print(r, ROLE[r][0], "load %.1f" % sum(load[r].values()), {p: round(v, 1) for p, v in load[r].items()}, "should %.1f" % should[r])
for g in GATES:
    print(g, "D%d" % max(1, day_of(finish[g] - 1e-9)))
print("end D%d" % day_of(end_h - 1e-9), "sigma_h %.1f" % sigma)
print("chain:", " -> ".join(disp(c) for c in chain))
print("WARNINGS:", len(warnings)); print("\n".join(warnings))
print("ISSUES:", len(issues)); print("\n".join(issues))
