# Fourth Signal × Unilever — Sales Strategy Analyzer

This repository turns the **Unilever Annual Report and Accounts 2024** into an
evidence-led account strategy for **Fourth Signal**, with a focus on SAP
Treasury / Finance / Risk transformation.

## What it does

The script:

1. Reads the annual report page-by-page.
2. Searches for treasury, FX, liquidity, debt, counterparty-risk, automation,
   AI, working-capital and technology signals.
3. Extracts supporting snippets and page numbers.
4. Maps those signals to Fourth Signal capabilities.
5. Creates a transparent opportunity score.
6. Produces:
   - a CSV opportunity map
   - a Markdown account strategy
   - a Python object that can be explored in Jupyter

## Important methodology

The report can establish what **Unilever says about its business, risks and
priorities**.

It cannot establish:
- whether Unilever currently uses SAP Treasury;
- which treasury-management system is currently deployed;
- whether Fourth Signal has already engaged a specific Unilever entity;
- who the current decision-makers are;
- whether a specific project is funded.

Those are deliberately treated as **sales-discovery hypotheses**.

## Run locally

```bash
pip install -r requirements.txt

python fourth_signal_unilever_sales_strategy.py \
  --pdf unilever-annual-report-and-accounts-2024.pdf \
  --out outputs
```

## Use in Jupyter

```python
from fourth_signal_unilever_sales_strategy import analyze_report

result = analyze_report(
    "unilever-annual-report-and-accounts-2024.pdf",
    output_dir="outputs"
)

result["strategy_df"]
```

Show the 90-day sales motion:

```python
for step in result["account_strategy"]["90_day_motion"]:
    print(step)
```

Show the evidence behind a theme:

```python
for item in result["evidence"]:
    if item["signal"] == "FX exposure and hedging complexity":
        for match in item["matches"]:
            print(match["page"], match["snippet"])
```

## Sales logic

The intended sales motion is:

**Annual-report signal → business problem hypothesis → buyer → discovery
question → bounded workshop/pilot → quantified business case**

Rather than:

**Annual-report keyword → generic product pitch**

## Initial account thesis

The strongest evidence-led themes are around:

- FX and derivatives / hedging complexity
- interest-rate risk on debt
- centralized counterparty controls
- cash and liquidity visibility
- multi-country treasury complexity
- finance automation and productivity

The first conversation should therefore be framed around **treasury visibility,
risk control, automation and SAP-enabled process improvement**, subject to
validation of Unilever's existing technology landscape.

## Fourth Signal context

Fourth Signal describes itself as an SAP-anchored treasury and risk-management
provider, with capabilities spanning treasury, FX/derivatives, cash and
liquidity, borrowings/trade finance, investments/loans and proprietary
platform extensions.

Official website:

https://www.fourthsignal.com/

## Source

Unilever Annual Report and Accounts 2024 — supplied as the source PDF.

## Disclaimer

This is an account-research and sales-planning tool, not an investment
analysis or a claim about Unilever's internal systems. Always validate the
technology stack, ownership, current projects and procurement process with
the account.
