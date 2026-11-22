"""Shared task-status rules for the NusaFire execution plan (planning tool, not application code).

Used by build_plan.py (status icons in 04-dependency-graph.mmd) and task.py (agent CLI), so the graph the team
reads and the check an agent runs always apply the same rules. Stdlib only.

Status of a node (task or gate), from 13-progress-tracker.md + the dependency graph:
  DONE     `[x]` and `disetujui:` filled           (approved by any human; no review by another role is required)
  REVIEW   `[x]`, `disetujui:` empty               (implementer finished, waiting for a human to approve)
  BLOCKED  not `[x]`, some blocking dependency is not DONE
  ACTIVE   not `[x]`, no blocker, `bukti:` already filled (work started / partial)
  READY    not `[x]`, no blocker, nothing started

Blocking dependency types follow the Definition of Ready (10-phase-gates.md §3): Hard (H), Interface (I) and
Human approval (HA) must be DONE before a task may start, i.e. approved by a human (any team member). Soft (S) and
Review (R, no longer used: cross-role review is not mandatory) never block.
"""
import re

LINE_RE = re.compile(r"^- \[( |x|X)\] \*\*([ABCDX]-P\d-\d{3}|GATE-[A-Z0-9]+)\*\*(.*)$")
FIELDS_RE = re.compile(r"· bukti: (.*?) · disetujui: (.*)$")
EMPTY = {"", "—", "-"}
BLOCKING = ("H", "I", "HA")
DEP_NAMES = {"H": "Hard", "S": "Soft", "I": "Interface", "R": "Review", "HA": "Human approval"}

ICON = {"DONE": "✅", "REVIEW": "⏳", "ACTIVE": "🔧", "READY": "▶", "BLOCKED": "⛔"}
LABEL = {"DONE": "SELESAI", "REVIEW": "MENUNGGU PERSETUJUAN", "ACTIVE": "BERJALAN", "READY": "SIAP", "BLOCKED": "TERBLOKIR"}


def parse_tracker(text):
    """Return {node_id: {"done": bool, "ev": str, "ok": bool}} for every well-formed tracker line."""
    state = {}
    for ln in text.splitlines():
        m = LINE_RE.match(ln)
        if not m:
            continue
        fm = FIELDS_RE.search(m.group(3))
        if not fm:
            continue
        state[m.group(2)] = dict(done=m.group(1) != " ", ev=fm.group(1).strip(), ok=fm.group(2).strip() not in EMPTY)
    return state


def own_status(st):
    """Status from the node's own tracker line only (dependencies ignored)."""
    st = st or {}
    if st.get("done"):
        return "DONE" if st.get("ok") else "REVIEW"
    return "ACTIVE" if st.get("ev", "—") not in EMPTY else "READY"


def classify(nodes, deps_of, state):
    """Return {node: (status, blockers)}; blockers = [(dep_id, dep_type, dep_status), ...] (blocking types only)."""
    out = {}

    def resolve(n):  # the plan is acyclic (build_plan.py checks), so plain recursion terminates
        if n not in out:
            own = own_status(state.get(n))
            if own in ("DONE", "REVIEW"):
                out[n] = (own, [])
            else:
                blockers = [(d, ty, resolve(d)[0]) for d, ty in deps_of(n) if ty in BLOCKING and own_status(state.get(d)) != "DONE"]
                out[n] = ("BLOCKED" if blockers else own, blockers)
        return out[n]

    for n in nodes:
        resolve(n)
    return out
