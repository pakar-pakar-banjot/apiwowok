"""NusaFire agent task CLI: pick a task, check it against the dependency graph, and check the files touched.

Run it instead of reading the large plan files. Read-only: it never writes a file and never calls an API.

  python -I docs/10-execution-plan/tools/task.py brief [--role A|B|C|D]   # session start: what is ready / blocked
  python -I docs/10-execution-plan/tools/task.py check <TASK-ID>          # task card + Definition of Ready verdict
  python -I docs/10-execution-plan/tools/task.py scope <TASK-ID> [--base REF]   # before reporting: files touched (default base: origin/<phase branch>)

Inputs: 04-dependency-graph.mmd (edges, the graph the team reads), 02-work-breakdown-structure.csv (task card),
13-progress-tracker.md (status), git branches (who is already working on a task). Rules: plan_status.py.

Exit codes: 0 = OK / READY · 1 = STOP (blocked, file outside the area, task already has another branch)
            2 = do not work on it (done, in review, human-only) · 3 = usage error or plan files out of sync
Stdlib only.
"""
import csv, fnmatch, pathlib, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles default to cp1252
TOOLS = pathlib.Path(__file__).resolve().parent
PLAN = TOOLS.parent
ROOT = PLAN.parents[1]
sys.path.insert(0, str(TOOLS))  # `python -I` does not add the script dir
import plan_status as PS

GRAPH, WBS, TRACKER = PLAN / "04-dependency-graph.mmd", PLAN / "02-work-breakdown-structure.csv", PLAN / "13-progress-tracker.md"
REL_TRACKER, REL_GRAPH = "docs/10-execution-plan/13-progress-tracker.md", "docs/10-execution-plan/04-dependency-graph.mmd"
ROLE_CODE = {"A": "R1", "B": "R2", "C": "R3", "D": "R4"}
# AGENTS.md §5a: every task branch starts from, and every task PR targets, the branch of its own phase.
PHASE_BRANCH = {"P1": "phase/p1-dataset-feasibility", "P2": "phase/p2-requirements", "P3": "phase/p3-specs",
                "P4": "phase/p4-harness", "P5": "phase/p5-etl-cassandra", "P6": "phase/p6-backend-frontend",
                "P7": "phase/p7-integration-testing", "P8": "phase/p8-final-delivery"}
TYPE_OF_NAME = {v: k for k, v in PS.DEP_NAMES.items()}
ARROW = {"-->": "H", "==>": "I", "--o": "HA", "-.->": "S"}  # -.-> is Soft or Review; neither blocks a start
EDGE_RE = re.compile(r"^\s+([A-Z][A-Z0-9_]*) (-->|-\.->|==>|--o) ([A-Z][A-Z0-9_]*)\s*$")
TASK_ID_RE = re.compile(r"[ABCDX]-P\d-\d{3}", re.I)
HUMAN_ONLY = {"Manusia saja", "Manusia"}
RECORDER = {"Manusia (agen hanya mencatat)", "Manusia + agen pencatat"}


def die(msg, code=3):
    print(msg)
    sys.exit(code)


def node_id(mermaid_id):
    return mermaid_id.replace("_", "-")


def day(s):
    m = re.match(r"D(\d+)", s or "")
    return int(m.group(1)) if m else 99


# ------------------------------------------------------------------ load
for f in (GRAPH, WBS, TRACKER):
    if not f.exists():
        die(f"File rencana tidak ada: {f.relative_to(ROOT)}. Jalankan tools/build_plan.py.")
TASK = {r["task_id"]: r for r in csv.DictReader(WBS.open(encoding="utf-8-sig"))}
EDGES = {}  # node -> [(dep, type)] from the graph
for ln in GRAPH.read_text(encoding="utf-8").splitlines():
    m = EDGE_RE.match(ln)
    if m:
        EDGES.setdefault(node_id(m.group(3)), []).append((node_id(m.group(1)), ARROW[m.group(2)]))
GATES = sorted({n for n in EDGES if n.startswith("GATE-")} | {d for v in EDGES.values() for d, _ in v if d.startswith("GATE-")},
               key=lambda g: (g != "GATE-EP", g))
NODES = list(TASK) + GATES


def csv_deps(tid):
    out = []
    for part in TASK[tid]["dependencies"].split(";"):
        m = re.match(r"\s*(\S+) \((.+)\)\s*$", part)
        if m:
            out.append((m.group(1), TYPE_OF_NAME[m.group(2)]))
    return out


# the graph is what the team reads: refuse to answer if it disagrees with the WBS (someone skipped build_plan.py)
drift = []
for tid in TASK:
    g = {(d, ty in PS.BLOCKING) for d, ty in EDGES.get(tid, [])}
    c = {(d, ty in PS.BLOCKING) for d, ty in csv_deps(tid)}
    if g != c:
        drift.append(tid)
if drift:
    die("Graf 04-dependency-graph.mmd tidak cocok dengan WBS untuk: " + ", ".join(drift[:10])
        + "\nJalankan `python -I docs/10-execution-plan/tools/build_plan.py` (harus ISSUES: 0), lalu ulangi.")


def deps_of(n):
    return csv_deps(n) if n in TASK else EDGES.get(n, [])  # tasks: exact type from WBS (graph verified equal)


STATE = PS.parse_tracker(TRACKER.read_text(encoding="utf-8"))
STATUS = PS.classify(NODES, deps_of, STATE)
SUCC = {}
for n in NODES:
    for d, _ in deps_of(n):
        SUCC.setdefault(d, []).append(n)


def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
    except OSError:
        return ""


CURRENT = git("branch", "--show-current").strip()
BRANCHES = {}
for b in git("for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes").split():
    for tid in {x.upper() for x in TASK_ID_RE.findall(b)}:
        BRANCHES.setdefault(tid, set()).add(b.removeprefix("origin/"))


def icon(n):
    return PS.ICON[STATUS[n][0]]


def mode(tid):
    m = TASK[tid]["agent_mode"]
    return "HUMAN" if m in HUMAN_ONLY else "RECORDER" if m in RECORDER else "AGENT"


def order(ids):
    return sorted(ids, key=lambda t: (day(TASK[t]["planned_start"]), TASK[t]["on_critical_chain"] != "yes", t))


def short(tid, w=46):
    t = TASK[tid]["title"]
    return t if len(t) <= w else t[: w - 1] + "…"


def tag(tid):
    bits = [TASK[tid]["planned_start"].split(" ")[0]]
    if TASK[tid]["on_critical_chain"] == "yes":
        bits.append("kritis")
    if TASK[tid]["priority"] != "Must":
        bits.append(TASK[tid]["priority"])
    if mode(tid) == "HUMAN":
        bits.append("manusia saja")
    elif mode(tid) == "RECORDER":
        bits.append("agen hanya mencatat")
    other = BRANCHES.get(tid, set()) - {CURRENT}
    if other:
        bits.append("branch: " + ", ".join(sorted(other)))
    return "[" + " · ".join(bits) + "]"


# ------------------------------------------------------------------ brief
def brief(role):
    print(f"NusaFire · brief agen · branch aktif: {CURRENT or '(detached)'}")
    print("Sumber: 04-dependency-graph.mmd + 13-progress-tracker.md + branch git. "
          + " ".join(f"{PS.ICON[k]}={PS.LABEL[k].lower()}" for k in PS.ICON))
    print("Gerbang: " + " · ".join(f"{icon(g)} {g}" for g in GATES))
    nxt = next((g for g in GATES if STATUS[g][0] != "DONE"), None)
    if nxt:
        print(f"Gerbang berikutnya {nxt} menunggu: "
              + (", ".join(f"{d} {PS.ICON[s]}" for d, _, s in STATUS[nxt][1]) or "keputusan tim"))
    open_phases = sorted({TASK[t]["phase_id"] for t in TASK if STATUS[t][0] != "DONE"})
    print(f"Fase aktif (fase terendah yang belum selesai): {open_phases[0] if open_phases else '—'}")
    roles = [role] if role else list(ROLE_CODE)
    suggestion = None
    for r in roles:
        mine = [t for t in TASK if TASK[t]["owner_role_code"] == ROLE_CODE[r]]
        cnt = {k: sum(STATUS[t][0] == k for t in mine) for k in PS.ICON}
        print(f"\nPeran {r} ({ROLE_CODE[r]}) — {len(mine)} tugas: " + " ".join(f"{PS.ICON[k]}{cnt[k]}" for k in PS.ICON))
        ready = order(t for t in mine if STATUS[t][0] == "READY")
        active = order(t for t in mine if STATUS[t][0] == "ACTIVE")
        review = order(t for t in mine if STATUS[t][0] == "REVIEW")
        near = order(t for t in mine if STATUS[t][0] == "BLOCKED" and all(s != "BLOCKED" for _, _, s in STATUS[t][1]))
        for label, ids in ((f"{PS.ICON['READY']} SIAP", ready), (f"{PS.ICON['ACTIVE']} BERJALAN", active)):
            print(f"  {label}:" + ("" if ids else " —"))
            for t in ids[: 8 if role else 4]:
                print(f"    {t} {short(t)} {tag(t)}")
        print(f"  {PS.ICON['REVIEW']} MENUNGGU PERSETUJUAN: " + (", ".join(review) or "—"))
        print(f"  {PS.ICON['BLOCKED']} terblokir terdekat: " + ("; ".join(
            f"{t} ← " + ", ".join(f"{d} {PS.ICON[s]}" for d, _, s in STATUS[t][1]) for t in near[:5]) or "—"))
        pick = [t for t in ready + active if mode(t) != "HUMAN" and not (BRANCHES.get(t, set()) - {CURRENT})]
        if role and pick:
            suggestion = pick[0]
    print()
    if suggestion:
        print(f"USULAN untuk manusia: {suggestion} — {TASK[suggestion]['title']}")
    print("Agen: usulkan 1 tugas (SIAP, atau BERJALAN untuk dilanjutkan) dan TUNGGU konfirmasi manusia; lalu `task.py check <ID>`.")


# ------------------------------------------------------------------ check
def check(tid):
    tid = tid.upper()
    if tid not in TASK:
        die(f"{tid}: tidak ada di WBS. Jangan mengerjakan pekerjaan tanpa task ID; tanya manusia/koordinator (CR atau tugas baru).")
    T, (st, blockers) = TASK[tid], STATUS[tid]
    print(f"{tid} — {T['title']}")
    print(f"Status: {PS.ICON[st]} {PS.LABEL[st]} · bukti tracker: {STATE.get(tid, {}).get('ev', '—')}")
    print(f"Pemilik: {T['primary_owner']} ({T['owner_role_code']}) · {T['priority']} · "
          f"mode: {T['agent_mode']} · rencana {T['planned_start']} → {T['planned_finish']} · rantai kritis: {T['on_critical_chain']}")
    for label, key in (("Persetujuan manusia", "human_approval"), ("Tujuan", "objective"), ("Input", "required_inputs"),
                       ("Output", "expected_outputs"), ("File tugas", "files_owned"), ("Langkah", "execution_steps"),
                       ("Spesifikasi", "technical_specification"), ("Kriteria penerimaan", "acceptance_criteria"),
                       ("Verifikasi", "automated_verification"), ("Bukti wajib", "required_test_evidence"),
                       ("Serah-terima", "handoff_requirements"), ("Area boleh diubah", "files_allowed_to_modify")):
        print(f"{label}: {T[key]}")
    print("DILARANG diubah: area peran lain + .env + docs/00-discovery/ (lengkapnya: `task.py scope` menegakkannya)")
    print("Dependensi (dari graf):" + ("" if deps_of(tid) else " —"))
    for d, ty in deps_of(tid):
        s = STATUS[d][0]
        need = "wajib selesai" if ty in PS.BLOCKING else "tidak memblokir"
        print(f"  {PS.ICON[s]} {d:<9} {PS.DEP_NAMES[ty]:<14} {PS.LABEL[s]:<15} ({need})")
    print("Dependen (menunggu tugas ini): " + (", ".join(SUCC.get(tid, [])) or "—"))
    other = sorted(BRANCHES.get(tid, set()) - {CURRENT})
    print("Branch lain untuk tugas ini: " + (", ".join(other) or "—"))

    def verdict(code, msg):
        print(f"\nVERDIKT: {msg}")
        sys.exit(code)

    if mode(tid) == "HUMAN":
        verdict(2, "TUGAS MANUSIA SAJA — agen DILARANG mengerjakannya (boleh menjawab pertanyaan bila diminta).")
    if st == "DONE":
        verdict(2, "SUDAH SELESAI (disetujui manusia). Jangan diubah lagi tanpa CR atau permintaan manusia.")
    if st == "REVIEW":
        verdict(2, "MENUNGGU PERSETUJUAN manusia (anggota tim mana pun mengisi `disetujui:`). Jangan dikerjakan ulang; ubah hanya bila manusia meminta.")
    if st == "BLOCKED":
        verdict(1, "TERBLOKIR — STOP. Laporkan ke manusia: " + "; ".join(
            f"{d} ({PS.DEP_NAMES[ty]}) masih {PS.LABEL[s]}" for d, ty, s in blockers)
            + ". Mulai hanya bila manusia mengizinkan secara eksplisit; kutip izinnya (siapa, kapan) di PR.")
    if other:
        verdict(1, f"SUDAH ADA BRANCH {', '.join(other)} — kemungkinan sedang dikerjakan orang/agen lain. STOP; konfirmasi manusia.")
    soft = [d for d, ty in deps_of(tid) if ty not in PS.BLOCKING and STATUS[d][0] != "DONE"]
    if soft:
        print("Catatan: dependensi Soft belum selesai (" + ", ".join(soft) + "): lanjut dengan asumsi tertulis di PR.")
    if mode(tid) == "RECORDER":
        print("Catatan: agen HANYA mencatat keputusan yang dinyatakan manusia; jangan memutuskan atau menyetujui.")
    prefix = "x" if tid.startswith("X-") else tid[0].lower()
    pb = PHASE_BRANCH[T["phase_id"]]
    pb_ok = bool(git("rev-parse", "--verify", "--quiet", "origin/" + pb).strip())
    print(f"Branch fase (AGENTS.md §5a): {pb}" + ("" if pb_ok else
          " — BELUM ADA di origin. Minta koordinator membuatnya dari main dan membuka PR fase (draft) dulu."))
    print(f"PR tugas: base {pb}, judul `<type>({tid}): <ringkasan>`")
    if tid not in CURRENT.upper():
        common = git("rev-parse", "--path-format=absolute", "--git-common-dir").strip()
        main_root = pathlib.Path(common).parent if common else ROOT
        print(f"Catatan: branch aktif '{CURRENT}' bukan branch tugas ini. Buat worktree dulu "
              f"(WAJIB di dalam repo, AGENTS.md §3 aturan 7): "
              f"git -C \"{main_root}\" worktree add .claude/worktrees/{tid} -b {prefix}/{tid}-<slug> origin/{pb}")
    verdict(0, ("BERJALAN — boleh dilanjutkan" if st == "ACTIVE" else "SIAP — boleh mulai")
            + " setelah manusia mengonfirmasi tugas ini. Ubah hanya 'File tugas' (dan area peran bila perlu, dijelaskan di PR).")


# ------------------------------------------------------------------ scope
def pats(field):
    return [p.split(" (")[0].strip() for p in field.split(";") if p.strip() and p.strip() != "—"]


def match(path, pat):
    if "*" in pat:
        return fnmatch.fnmatch(path, pat)
    if pat.endswith("/"):
        return path.startswith(pat)
    return path == pat or path.startswith(pat + "/")


def best(path, patterns):
    return max((len(p) for p in patterns if match(path, p)), default=-1)


def changed_files(base):
    files = set(git("diff", "--name-only", f"{base}...HEAD").split("\n"))
    for ln in git("status", "--porcelain=v1", "-uall").splitlines():
        p = ln[3:].split(" -> ")[-1].strip().strip('"')
        files.add(p)
    return sorted(f for f in files if f)


def tracker_lines_ok(tid, base):
    """Only this task's own line may change in the tracker (the summary block is rewritten by build_plan.py)."""
    bad = []
    diff = git("diff", base, "--", REL_TRACKER) + git("diff", "--cached", base, "--", REL_TRACKER)
    for ln in diff.splitlines():
        if ln[:1] not in "+-" or ln.startswith(("+++", "---")):
            continue
        body = ln[1:]
        if body.startswith("- ["):
            if f"**{tid}**" not in body and not (tid.startswith("X-") and "**GATE-" in body):
                bad.append(body[:90])
        elif body.strip() and not body.startswith(("|", "Format sel", "Gerbang disetujui", "Menunggu persetujuan", "Menunggu review")):
            bad.append(body[:90])
    return sorted(set(bad))


def scope(tid, base):
    tid = tid.upper()
    if tid not in TASK:
        die(f"{tid}: tidak ada di WBS.")
    if not git("rev-parse", "--verify", "--quiet", base).strip():
        die(f"Base '{base}' tidak ditemukan. Pakai --base <branch asal>, mis. --base origin/main.")
    T = TASK[tid]
    allowed, forbidden = pats(T["files_allowed_to_modify"]), pats(T["files_must_not_modify"])
    own = [p.strip() for p in T["files_owned"].split(",") if p.strip() and p.strip() != "—"]
    errors, notes = [], []
    files = changed_files(base)
    for f in files:
        if f == ".env" or (f.startswith(".env.") and f != ".env.example"):
            errors.append(f"{f}: RAHASIA — tidak boleh pernah ada di diff/commit")
        elif f.startswith("data/"):
            errors.append(f"{f}: data mentah — tidak boleh di-commit")
        elif f == REL_TRACKER:
            bad = tracker_lines_ok(tid, base)
            if bad:
                errors.append(f"{f}: mengubah baris selain baris {tid}: " + " | ".join(bad[:3]))
        elif f == REL_GRAPH:
            notes.append(f"{f}: hasil build_plan.py (status) — OK bila dihasilkan ulang, bukan diedit manual")
        elif best(f, forbidden) > best(f, allowed):
            errors.append(f"{f}: DI LUAR AREA peran {T['owner_role_code']} — batalkan, atau ajukan CR/PR ke pemiliknya")
        elif best(f, allowed) < 0:
            errors.append(f"{f}: tidak terdaftar di area mana pun — tanya koordinator")
        elif best(f, own) < 0:
            notes.append(f"{f}: di area peran, tetapi bukan 'File tugas' {tid} — jelaskan alasannya di PR")
    print(f"scope {tid} · base {base} · {len(files)} file berubah (commit di branch + working tree)")
    for f in files:
        mark = "✗" if any(e.startswith(f + ":") for e in errors) else "!" if any(n.startswith(f + ":") for n in notes) else "✓"
        print(f"  {mark} {f}")
    for e in errors:
        print("  ERROR  " + e)
    for n in notes:
        print("  CATAT  " + n)
    if errors:
        print("\nVERDIKT: PELANGGARAN — STOP. Kembalikan file di luar area sebelum melapor/membuka PR.")
        sys.exit(1)
    print("\nVERDIKT: OK — semua file di area tugas. Jalankan build_plan.py (ISSUES: 0) bila tracker berubah.")


# ------------------------------------------------------------------ main
args = sys.argv[1:]
if not args or args[0] not in ("brief", "check", "scope"):
    die(__doc__)
if args[0] == "brief":
    r = args[args.index("--role") + 1].upper() if "--role" in args and len(args) > args.index("--role") + 1 else None
    if r and r not in ROLE_CODE:
        die("--role harus A, B, C, atau D")
    brief(r)
elif len(args) < 2:
    die(__doc__)
elif args[0] == "check":
    check(args[1])
else:
    tid0 = args[1].upper()
    pb = "origin/" + PHASE_BRANCH[TASK[tid0]["phase_id"]] if tid0 in TASK else "main"
    default = pb if git("rev-parse", "--verify", "--quiet", pb).strip() else "main"
    scope(args[1], args[args.index("--base") + 1] if "--base" in args and len(args) > args.index("--base") + 1 else default)
