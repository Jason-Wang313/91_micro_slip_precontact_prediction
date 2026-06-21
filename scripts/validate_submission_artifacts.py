import csv
import re
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PAPER = ROOT / "paper"
PDF = Path("C:/Users/wangz/Downloads/91.pdf")
DESKTOP_PDF = Path("C:/Users/wangz/Desktop/91.pdf")

EXPECTED_ROWS = {
    "rollouts.csv": 215040,
    "dataset_summary.csv": 15360,
    "raw_seed_metrics.csv": 1120,
    "metrics.csv": 1456,
    "pairwise_stats.csv": 1248,
    "hard_aggregate_seed_metrics.csv": 140,
    "hard_aggregate_metrics.csv": 182,
    "hard_aggregate_pairwise_stats.csv": 156,
    "ablation_rollouts.csv": 76800,
    "ablation_seed_metrics.csv": 100,
    "ablation_metrics.csv": 130,
    "stress_sweep_raw.csv": 302400,
    "stress_sweep_seed_metrics.csv": 840,
    "stress_sweep.csv": 1092,
    "fixed_risk_raw.csv": 69120,
    "fixed_risk_seed_metrics.csv": 480,
    "fixed_risk_metrics.csv": 288,
    "fixed_risk_pairwise.csv": 240,
    "negative_cases.csv": 24,
}


def row_count(path):
    with path.open(newline="", encoding="utf-8") as fh:
        return sum(1 for _ in csv.DictReader(fh))


def sha256(path):
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def main():
    for name, expected in EXPECTED_ROWS.items():
        actual = row_count(RESULTS / name)
        if actual != expected:
            raise SystemExit(f"{name}: expected {expected}, got {actual}")

    summary = (RESULTS / "summary.txt").read_text(encoding="utf-8")
    for token in [
        "Terminal recommendation: KILL_ARCHIVE",
        "main_gate=False",
        "control_gate=False",
        "safety_gate=False",
        "stress_gate=False",
        "fixed_risk_gate=False",
        "scope_gate=False",
        "terminal=KILL_ARCHIVE",
    ]:
        if token not in summary:
            raise SystemExit(f"missing summary token: {token}")

    tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    for token in [
        "citebordercolor={0 1 0}",
        "pdfborder={0 0 1.2}",
        "\\bibliography{references}",
        "KILL/ARCHIVE",
        "calibrated\\_precontact\\_microslip\\_v5",
    ]:
        if token not in tex:
            raise SystemExit(f"missing tex token: {token}")

    bib_entries = len(re.findall(r"^@article\{", (PAPER / "references.bib").read_text(encoding="utf-8"), re.M))
    if bib_entries < 100:
        raise SystemExit(f"too few bib entries: {bib_entries}")

    log_path = PAPER / "main.log"
    if log_path.exists():
        log = log_path.read_text(encoding="utf-8", errors="ignore")
        bad = ["LaTeX Error", "Emergency stop", "Fatal error", "undefined references", "Citation `"]
        for token in bad:
            if token in log:
                raise SystemExit(f"LaTeX log contains {token}")

    if not PDF.exists():
        raise SystemExit(f"missing Downloads PDF: {PDF}")
    if DESKTOP_PDF.exists():
        raise SystemExit(f"Desktop PDF leak: {DESKTOP_PDF}")

    reader = PdfReader(str(PDF))
    pages = len(reader.pages)
    if pages < 25:
        raise SystemExit(f"PDF too short: {pages} pages")
    text = "\n".join(page.extract_text() or "" for page in reader.pages[: min(pages, 10)])
    normalized_text = re.sub(r"\s+", " ", text.lower())
    for token in ["kill/archive", "micro-slip", "fixed-risk", "calibrated precontact"]:
        if token not in normalized_text:
            raise SystemExit(f"PDF text missing token: {token}")

    link_count = 0
    for page in reader.pages:
        annots = page.get("/Annots") or []
        link_count += len(annots)
    if link_count < 100:
        raise SystemExit(f"too few PDF annotations/citation links: {link_count}")

    print(f"validated Paper 91 artifacts: pages={pages}, sha256={sha256(PDF)}")


if __name__ == "__main__":
    main()
