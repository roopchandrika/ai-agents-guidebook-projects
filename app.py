import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from flow import BrandMonitoringFlow  # noqa: E402

st.set_page_config(page_title="Brand Monitor", page_icon="📡", layout="wide")
st.title("📡 Multi-agent Brand Monitoring")
st.caption("Bright Data scraping + CrewAI Flows + local LLM")

brand = st.text_input("Brand or company name", "Lightning AI")

if st.button("Generate report", type="primary") and brand:
    flow = BrandMonitoringFlow()
    with st.spinner("Scraping mentions and running platform crews... (a few minutes)"):
        try:
            flow.kickoff(inputs={"brand": brand})
        except Exception as e:
            st.error(f"Flow failed: {e}")
            st.stop()

    st.download_button("Download report (.md)", flow.state.final_report, file_name=f"{brand}_report.md")
    tabs = st.tabs(["Full report"] + list(flow.state.reports) + ["Raw mentions"])
    tabs[0].markdown(flow.state.final_report)
    for tab, (platform, text) in zip(tabs[1:], flow.state.reports.items()):
        tab.markdown(text)
    tabs[-1].json(flow.state.raw)
