import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

COL = {"ai": "#E6D9F5", "rule": "#D6E8FA", "human": "#D5F0DC", "stop": "#FBE0D0"}
EDGE = {"ai": "#6B3FA0", "rule": "#2B6CB0", "human": "#2F855A", "stop": "#C05621"}

fig, ax = plt.subplots(figsize=(13, 17.8)); ax.set_xlim(0, 13); ax.set_ylim(0, 17.8); ax.axis("off")

def box(x, y, w, h, text, kind, size=10.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.15",
                 fc=COL[kind], ec=EDGE[kind], lw=2))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=size)

def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", lw=1.6, color="#333"))

ax.text(6.5, 17.4, "AI Proposal Triage: upload to ranked output", ha="center", fontsize=16, weight="bold")

X, W, H = 1.2, 6.2, 0.95
steps = [
 (15.3, "0. Admin sets criteria, weights, scoring rules\n(saved as a numbered version)", "human"),
 (14.0, "1. Reviewer uploads PDFs and picks a category\n(system loads that category's current criteria version)", "human"),
 (12.7, "2. Extract text from each PDF (OCR if scanned)\nStore original file + text + file hash", "rule"),
 (11.4, "3. Injection screen: scan for text that talks to an AI/reviewer\n(hit = flag proposal for a human, text kept out of scoring)", "rule"),
 (10.1, "4. AI EXTRACTION (temperature 0, fixed JSON schema)\nFacts + exact supporting quote per criterion; 'null' if missing", "ai"),
 (8.8, "5. Validate: schema OK? quote really in the text?\nnumbers parse? (failure = flag, never guess)", "rule"),
 (7.5, "6. Mandatory gate: licence held + stated; WSIB and $5M insurance\nPass / Fail / Unclear", "rule"),
 (6.2, "7. Weighted scoring by formula (code): experience, price,\ntimeline, warranty; team = 4-item checklist x points", "rule"),
 (4.9, "8. Rank by score; build one-line reason from stored evidence\n(AI may only reword the sentence, never change numbers)", "rule"),
 (3.6, "9. HUMAN REVIEW screen: ranked list, flagged queue, ineligible list\nReviewer can confirm, override, or request clarification", "human"),
 (2.3, "10. HUMAN makes the final award decision", "human"),
]
for y, t, k in steps:
    box(X, y, W, H, t, k, 10)
for i in range(len(steps) - 1):
    arrow(X + W/2, steps[i][0], X + W/2, steps[i+1][0] + H)

# side outcome boxes
SX, SW = 8.3, 4.2
box(SX, 11.4, SW, H, "FLAGGED (needs a person)", "stop", 10)
box(SX, 7.5, SW, H, "INELIGIBLE: failed a mandatory\ncriterion (shown with reason)", "stop", 10)
box(SX, 8.8, SW, H, "FLAGGED: unreadable or\nunsupported extraction", "stop", 10)
box(SX, 6.2, SW, H, "FLAGGED: missing data (e.g. no\nschedule): scored partly, not ranked", "stop", 10)
arrow(X + W, 11.88, SX, 11.88); arrow(X + W, 9.27, SX, 9.27)
arrow(X + W, 7.97, SX, 7.97); arrow(X + W, 6.67, SX, 6.67)
ax.text(10.4, 10.55, "Unclear/failed items go to the\nreview screen (step 9)", ha="center", fontsize=9, style="italic")
ax.plot([10.4, 10.4], [6.1, 4.3], color="#C05621", lw=1.5, ls="--"); 
arrow(10.4, 4.3, X + W, 4.07)

# audit bar
ax.add_patch(FancyBboxPatch((0.5, 0.5), 12, 1.1, boxstyle="round,pad=0.05,rounding_size=0.15", fc="#F7F7F7", ec="#555", lw=2))
ax.text(6.5, 1.05, "AUDIT LOG (every step above): criteria version, file hash, prompt version + model name,\nraw AI output, extracted facts, scores, flags, reviewer overrides with reason + user + timestamp",
        ha="center", va="center", fontsize=10)

# legend
for i, (k, lab) in enumerate([("ai", "AI step"), ("rule", "Rule / code step"), ("human", "Human checkpoint"), ("stop", "Exception path")]):
    ax.add_patch(FancyBboxPatch((0.6 + i*3.1, 16.85), 0.35, 0.3, boxstyle="round,pad=0.02", fc=COL[k], ec=EDGE[k], lw=2))
    ax.text(1.05 + i*3.1, 17.0, lab, va="center", fontsize=10)

plt.savefig("../diagram/process-flow.png", dpi=130, bbox_inches="tight", facecolor="white")
