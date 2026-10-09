"""
Fourth Signal — Unilever Account Sales Strategy Analyzer
=========================================================

Purpose
-------
Turn an Unilever Annual Report PDF into an evidence-led account strategy for
Fourth Signal (SAP Treasury / Finance / Risk transformation).

Designed for:
- Jupyter Notebook
- GitHub
- CLI / local Python execution

Usage
-----
    python fourth_signal_unilever_sales_strategy.py \
        --pdf unilever-annual-report-and-accounts-2024.pdf \
        --out outputs

In Jupyter:
    from fourth_signal_unilever_sales_strategy import analyze_report
    result = analyze_report("unilever-annual-report-and-accounts-2024.pdf")
    result["strategy_df"]

The script deliberately distinguishes:
1. Evidence from Unilever's annual report
2. Fourth Signal capability mapping
3. Sales hypotheses that require validation

It does NOT claim that Unilever uses SAP Treasury or Fourth Signal.
Those are discovery hypotheses to validate with the account.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Any

import fitz  # PyMuPDF
import pandas as pd


FOURTH_SIGNAL = {
    "company": "Fourth Signal",
    "positioning": "SAP-anchored treasury and risk management transformation",
    "capabilities": [
        "Treasury platform solutions",
        "FX and derivatives management",
        "Cash and liquidity management",
        "Borrowings and trade finance",
        "Investments and loans",
        "Risk management and controls",
        "SAP integration",
        "Proprietary cloud/mobile extensions",
        "Analytics and reporting",
        "Process automation and operational efficiency",
    ],
}

# These are intentionally framed as discovery hypotheses, not facts about
# Unilever's technology estate.
SIGNAL_LIBRARY = [
    {
        "signal": "FX exposure and hedging complexity",
        "keywords": [
            "foreign exchange", "currency derivatives", "net investment hedges",
            "cash flow hedge", "currency risk"
        ],
        "fourth_signal_fit": "FX / derivatives management + treasury risk controls",
        "buyer_roles": "Group Treasurer; Head of Treasury; FX/Market Risk; Treasury Operations",
        "discovery_question": "How much of the FX lifecycle is automated from exposure capture through hedge execution, accounting and reporting?",
        "sales_motion": "Treasury diagnostic / FX control and automation workshop",
        "evidence_pages": "174–183",
    },
    {
        "signal": "Interest-rate risk on debt",
        "keywords": [
            "interest rate derivatives", "floating-rate debt",
            "interest rate swaps", "interest cost"
        ],
        "fourth_signal_fit": "Debt / interest-rate risk management",
        "buyer_roles": "Group Treasurer; Funding/Treasury; Market Risk",
        "discovery_question": "Where are debt, benchmark rates, swaps and hedge-accounting data connected today, and where are manual reconciliations still required?",
        "sales_motion": "Debt + hedge-management process assessment",
        "evidence_pages": "177–183",
    },
    {
        "signal": "Centralized counterparty credit controls",
        "keywords": [
            "counter-party", "counterparty", "credit limits",
            "collateral agreements", "netting agreements",
            "credit rating"
        ],
        "fourth_signal_fit": "Counterparty risk, limits, exposure and control automation",
        "buyer_roles": "Treasury Risk; Counterparty Risk; Group Treasury; Internal Controls",
        "discovery_question": "How are counterparty limits, collateral, netting and exposure monitoring consolidated across entities and instruments?",
        "sales_motion": "Counterparty-risk control diagnostic",
        "evidence_pages": "185–187",
    },
    {
        "signal": "Large and distributed cash position",
        "keywords": [
            "cash and cash equivalents", "cash at bank", "cash resources",
            "cash management", "foreign subsidiaries", "repatriate"
        ],
        "fourth_signal_fit": "Cash visibility, liquidity and cash-management platform",
        "buyer_roles": "Group Treasurer; Cash & Liquidity; Regional Treasury",
        "discovery_question": "How quickly can treasury obtain a consolidated view of cash, trapped cash, bank balances and liquidity across legal entities?",
        "sales_motion": "Global cash-visibility / liquidity diagnostic",
        "evidence_pages": "184–186",
    },
    {
        "signal": "Multi-country treasury complexity",
        "keywords": [
            "foreign subsidiaries", "local regulations", "local liquidity",
            "cross-border", "global debt markets", "group companies"
        ],
        "fourth_signal_fit": "Scalable treasury operating model across entities and jurisdictions",
        "buyer_roles": "Group Treasury; Regional Treasury; Finance Transformation; SAP Finance",
        "discovery_question": "Which treasury processes are standardized globally versus handled locally, and where does that create data or control fragmentation?",
        "sales_motion": "Treasury operating-model and SAP landscape assessment",
        "evidence_pages": "174–186",
    },
    {
        "signal": "Technology, AI and productivity agenda",
        "keywords": [
            "artificial intelligence", "AI", "technology", "automation",
            "productivity", "digital", "data"
        ],
        "fourth_signal_fit": "Treasury automation, analytics and SAP-enabled process modernization",
        "buyer_roles": "CFO; Group Treasurer; Finance Transformation; CIO / SAP leadership",
        "discovery_question": "Where can treasury automation and analytics remove manual work while improving control and decision speed?",
        "sales_motion": "Executive treasury automation / analytics use-case workshop",
        "evidence_pages": "4–20, 36, 60",
    },
    {
        "signal": "Working-capital and cash-conversion focus",
        "keywords": [
            "working capital", "cash conversion", "free cash flow",
            "cash generation"
        ],
        "fourth_signal_fit": "Cash visibility, liquidity and finance-process efficiency",
        "buyer_roles": "CFO; Treasurer; Working Capital; Finance Transformation",
        "discovery_question": "Which treasury and intercompany processes are limiting visibility or speed of cash conversion?",
        "sales_motion": "Cash-conversion and liquidity improvement assessment",
        "evidence_pages": "12–16",
    },
]


def extract_pages(pdf_path: str | Path) -> pd.DataFrame:
    """Extract PDF text page-by-page."""
    pdf_path = Path(pdf_path)
    doc = fitz.open(pdf_path)
    rows = []
    for page_num, page in enumerate(doc, start=1):
        rows.append({
            "page": page_num,
            "text": page.get_text("text") or ""
        })
    doc.close()
    return pd.DataFrame(rows)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def find_signal_evidence(pages: pd.DataFrame, signal: Dict[str, Any]) -> Dict[str, Any]:
    """Find pages and snippets supporting a signal."""
    matches = []
    keywords = signal["keywords"]

    for _, row in pages.iterrows():
        text = row["text"]
        low = normalize(text)
        matched = [kw for kw in keywords if normalize(kw) in low]
        if matched:
            # Keep a short evidence window around the first matched keyword.
            first = matched[0].lower()
            pos = low.find(first)
            start = max(0, pos - 220)
            end = min(len(text), pos + 650)
            snippet = re.sub(r"\s+", " ", text[start:end]).strip()
            matches.append({
                "page": int(row["page"]),
                "matched_keywords": matched,
                "snippet": snippet
            })

    return {
        **signal,
        "match_count": len(matches),
        "pages_found": sorted({m["page"] for m in matches}),
        "matches": matches[:8],
    }


def score_signal(match: Dict[str, Any]) -> int:
    """
    Transparent opportunity score.

    0–3   = weak evidence
    4–6   = moderate evidence
    7–9   = strong evidence
    10+   = very strong evidence

    This is an account-prioritization heuristic, not a prediction.
    """
    page_count = len(match["pages_found"])
    keyword_count = len(set(
        kw for m in match["matches"] for kw in m["matched_keywords"]
    ))
    return min(12, keyword_count + min(page_count, 8))


def build_strategy_df(evidence: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for e in evidence:
        score = score_signal(e)
        if score >= 9:
            priority = "High"
        elif score >= 6:
            priority = "Medium"
        else:
            priority = "Explore"

        rows.append({
            "priority": priority,
            "score": score,
            "signal": e["signal"],
            "evidence_pages": e["evidence_pages"],
            "pages_found": ", ".join(map(str, e["pages_found"][:15])),
            "fourth_signal_fit": e["fourth_signal_fit"],
            "buyer_roles": e["buyer_roles"],
            "sales_motion": e["sales_motion"],
            "discovery_question": e["discovery_question"],
            "evidence_snippet": e["matches"][0]["snippet"] if e["matches"] else "",
        })

    return (
        pd.DataFrame(rows)
        .sort_values(["score", "priority"], ascending=[False, True])
        .reset_index(drop=True)
    )


def extract_unilever_headline_metrics(pages: pd.DataFrame) -> Dict[str, Any]:
    """Pull selected headline metrics from the report where available."""
    full = normalize(" ".join(pages["text"].tolist()))

    patterns = {
        "turnover_2024": r"€60\.8bn",
        "underlying_sales_growth": r"4\.2%",
        "underlying_volume_growth": r"2\.9%",
        "power_brand_sales_growth": r"5\.3%",
        "free_cash_flow": r"€6\.9 billion",
        "underlying_operating_profit": r"€11\.2 billion",
        "underlying_operating_margin": r"18\.4%",
        "cash_conversion": r"106%",
    }

    return {k: bool(re.search(v, full, flags=re.I)) for k, v in patterns.items()}


def make_account_strategy(strategy_df: pd.DataFrame) -> Dict[str, Any]:
    high = strategy_df[strategy_df["priority"] == "High"]
    medium = strategy_df[strategy_df["priority"] == "Medium"]

    plays = []
    for _, row in pd.concat([high, medium]).head(5).iterrows():
        plays.append({
            "theme": row["signal"],
            "why_now": row["fourth_signal_fit"],
            "target_buyers": row["buyer_roles"],
            "first_meeting": row["sales_motion"],
            "question": row["discovery_question"],
        })

    return {
        "account": "Unilever",
        "recommended_entry": (
            "Lead with a treasury-control and automation conversation, "
            "not a generic SAP implementation pitch."
        ),
        "primary_themes": plays,
        "90_day_motion": [
            "0–30 days: build an account map across Group Treasury, SAP/Finance Transformation, CFO office and relevant risk owners.",
            "0–30 days: validate the current SAP treasury architecture, bank connectivity, treasury management stack and major process pain points.",
            "31–60 days: run a focused discovery workshop on FX/derivatives, cash visibility and counterparty controls.",
            "31–60 days: quantify manual effort, reconciliation points, control gaps, reporting latency and entity-level fragmentation.",
            "61–90 days: propose one bounded pilot with measurable KPIs rather than a broad transformation programme.",
            "61–90 days: develop an executive business case around control, visibility, automation, speed and total cost of ownership.",
        ],
        "pilot_kpis": [
            "Time to produce consolidated treasury exposure reports",
            "Manual reconciliation hours",
            "Exception / break volumes",
            "Counterparty exposure visibility",
            "Cash-position visibility latency",
            "Number of manual handoffs",
            "Treasury reporting cycle time",
            "Control evidence / audit preparation effort",
        ],
        "important_validation": [
            "Confirm whether the relevant Unilever entities use SAP Treasury / SAP S/4HANA Finance.",
            "Identify incumbent treasury-management and bank-connectivity platforms.",
            "Map global versus regional treasury ownership.",
            "Determine whether current pain is process, data, integration, controls, reporting or platform-related.",
            "Do not assume a technology replacement is required; test whether an SAP-integrated overlay/add-on is the better fit.",
        ],
    }


def export_outputs(result: Dict[str, Any], output_dir: str | Path) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    result["strategy_df"].to_csv(out / "unilever_fourth_signal_opportunities.csv", index=False)

    strategy = result["account_strategy"]
    lines = [
        "# Unilever × Fourth Signal — Account Sales Strategy",
        "",
        f"**Recommended entry:** {strategy['recommended_entry']}",
        "",
        "## Priority opportunity themes",
    ]
    for p in strategy["primary_themes"]:
        lines += [
            f"### {p['theme']}",
            f"- **Why / fit:** {p['why_now']}",
            f"- **Target buyers:** {p['target_buyers']}",
            f"- **First meeting:** {p['first_meeting']}",
            f"- **Discovery question:** {p['question']}",
            "",
        ]

    lines += ["## 90-day sales motion"]
    lines += [f"{i+1}. {x}" for i, x in enumerate(strategy["90_day_motion"])]
    lines += ["", "## Pilot KPIs"]
    lines += [f"- {x}" for x in strategy["pilot_kpis"]]
    lines += ["", "## Validation before pitching"]
    lines += [f"- {x}" for x in strategy["important_validation"]]
    lines += [
        "",
        "## Source",
        "Unilever Annual Report and Accounts 2024 (provided PDF).",
        "",
        "## Method",
        "Keyword/evidence extraction + transparent account-fit mapping. "
        "Scores are prioritization heuristics and should be validated through discovery.",
    ]

    (out / "unilever_fourth_signal_account_strategy.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def analyze_report(pdf_path: str | Path, output_dir: str | Path | None = None) -> Dict[str, Any]:
    pages = extract_pages(pdf_path)

    evidence = [find_signal_evidence(pages, s) for s in SIGNAL_LIBRARY]
    strategy_df = build_strategy_df(evidence)
    headline_metrics = extract_unilever_headline_metrics(pages)
    account_strategy = make_account_strategy(strategy_df)

    result = {
        "pages": pages,
        "evidence": evidence,
        "strategy_df": strategy_df,
        "headline_metrics": headline_metrics,
        "account_strategy": account_strategy,
    }

    if output_dir:
        export_outputs(result, output_dir)

    return result


def print_strategy(result: Dict[str, Any]) -> None:
    print("\nUNILEVER × FOURTH SIGNAL — SALES OPPORTUNITY MAP")
    print("=" * 58)
    print(result["strategy_df"][
        ["priority", "score", "signal", "fourth_signal_fit", "buyer_roles"]
    ].to_string(index=False))

    print("\n90-DAY MOTION")
    print("-" * 58)
    for i, item in enumerate(result["account_strategy"]["90_day_motion"], 1):
        print(f"{i}. {item}")

    print("\nIMPORTANT: All technology/platform assumptions must be validated in discovery.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, help="Path to annual report PDF")
    parser.add_argument("--out", default="outputs", help="Output directory")
    args = parser.parse_args()

    result = analyze_report(args.pdf, args.out)
    print_strategy(result)


if __name__ == "__main__":
    main()
