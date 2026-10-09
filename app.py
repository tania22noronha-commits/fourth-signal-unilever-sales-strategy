from pathlib import Path
import tempfile

import pandas as pd
import plotly.express as px
import streamlit as st

from fourth_signal_unilever_sales_strategy import analyze_report

st.set_page_config(
    page_title="Unilever Sales Strategy Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("Unilever × Fourth Signal")
st.subheader("Sales Strategy Dashboard")
st.caption(
    "Explore priority opportunities, sales motions, and evidence extracted "
    "from the Unilever Annual Report."
)

st.sidebar.header("Report")
uploaded_pdf = st.sidebar.file_uploader(
    "Upload the Unilever annual report PDF",
    type=["pdf"],
    help="Upload a report PDF to generate the analysis. The PDF does not need to be stored in the public GitHub repository.",
)

st.sidebar.info(
    "This dashboard uses the project's existing analysis module. "
    "Keep fourth_signal_unilever_sales_strategy.py in the same GitHub repository as app.py."
)

if uploaded_pdf is None:
    st.info("To begin, upload the annual report PDF in the left sidebar.")
    st.markdown(
        """
        ### What you can explore
        - Priority opportunities and scores
        - Fourth Signal fit and recommended sales motions
        - Buyer roles associated with each opportunity
        - The 90-day account motion
        - Evidence snippets and report page references
        """
    )
    st.stop()

with tempfile.TemporaryDirectory() as temp_dir:
    pdf_path = Path(temp_dir) / uploaded_pdf.name
    pdf_path.write_bytes(uploaded_pdf.getvalue())

    with st.spinner("Analyzing the report. This may take a little while..."):
        try:
            result = analyze_report(str(pdf_path), output_dir=str(Path(temp_dir) / "output"))
        except Exception as exc:
            st.error("The report analysis could not be completed.")
            st.exception(exc)
            st.stop()

strategy_df = result.get("strategy_df")
if strategy_df is None or not isinstance(strategy_df, pd.DataFrame) or strategy_df.empty:
    st.warning("The analysis completed, but it did not return any strategy rows.")
    st.stop()

df = strategy_df.copy()

# Summary metrics
m1, m2, m3 = st.columns(3)
m1.metric("Opportunities identified", len(df))
if "score" in df.columns:
    scores = pd.to_numeric(df["score"], errors="coerce")
    m2.metric("Highest opportunity score", f"{scores.max():.1f}" if scores.notna().any() else "N/A")
else:
    m2.metric("Scoring", "Not available")
if "priority" in df.columns:
    m3.metric("Priority categories", int(df["priority"].nunique(dropna=True)))
else:
    m3.metric("Priority categories", "Not available")

st.divider()
st.header("Priority opportunity map")

if "priority" in df.columns:
    priority_values = sorted(df["priority"].dropna().astype(str).unique().tolist())
    selected_priorities = st.multiselect(
        "Filter by priority",
        options=priority_values,
        default=priority_values,
    )
    visible_df = df[df["priority"].astype(str).isin(selected_priorities)]
else:
    visible_df = df

if "score" in visible_df.columns and "signal" in visible_df.columns and not visible_df.empty:
    chart_df = visible_df.copy()
    chart_df["score"] = pd.to_numeric(chart_df["score"], errors="coerce")
    chart_df = chart_df.dropna(subset=["score"])
    if not chart_df.empty:
        chart_df = chart_df.sort_values("score", ascending=True)
        fig = px.bar(
            chart_df,
            x="score",
            y="signal",
            color="priority" if "priority" in chart_df.columns else None,
            orientation="h",
            title="Opportunity score by signal",
            labels={"score": "Score", "signal": "Opportunity signal"},
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

preferred_columns = [
    "priority", "score", "signal", "fourth_signal_fit", "buyer_roles", "sales_motion"
]
table_columns = [column for column in preferred_columns if column in visible_df.columns]
if not table_columns:
    table_columns = list(visible_df.columns)
st.dataframe(visible_df[table_columns], use_container_width=True, hide_index=True)

st.download_button(
    "Download filtered opportunities as CSV",
    data=visible_df.to_csv(index=False).encode("utf-8"),
    file_name="unilever_sales_strategy_opportunities.csv",
    mime="text/csv",
)

st.divider()
st.header("90-day account motion")
account_strategy = result.get("account_strategy", {})
motion = account_strategy.get("90_day_motion", []) if isinstance(account_strategy, dict) else []
if motion:
    for index, step in enumerate(motion, start=1):
        st.markdown(f"**Step {index}.** {step}")
else:
    st.caption("No 90-day account motion was returned by the analysis module.")

st.divider()
st.header("Evidence")
evidence_items = result.get("evidence", [])
if evidence_items:
    available_signals = [
        str(item.get("signal", f"Signal {i + 1}"))
        for i, item in enumerate(evidence_items)
        if isinstance(item, dict)
    ]
    if available_signals:
        selected_signal = st.selectbox("Choose an opportunity signal", available_signals)
        selected_items = [
            item for item in evidence_items
            if isinstance(item, dict) and str(item.get("signal", "")) == selected_signal
        ]
        for item in selected_items:
            for match in item.get("matches", []):
                if not isinstance(match, dict):
                    continue
                page = match.get("page", "Unknown")
                snippet = match.get("snippet", "")
                with st.expander(f"Report page {page}"):
                    st.write(snippet or "No snippet available.")
else:
    st.caption("No evidence snippets were returned by the analysis module.")

st.caption(
    "Analytical outputs depend on the uploaded report and the project's analysis logic. "
    "Review findings before using them for business decisions."
)
