import re
from datetime import date, timedelta

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from crew import find_hotels  # noqa: E402

st.set_page_config(page_title="Hotel Finder", page_icon="🏨")
st.title("🏨 Multi-agent Hotel Finder")
st.caption("CrewAI agents + Browserbase headless browser + Kayak")

with st.form("search"):
    location = st.text_input("Destination", "Paris, France")
    col1, col2, col3 = st.columns(3)
    check_in = col1.date_input("Check-in", date.today() + timedelta(days=30))
    check_out = col2.date_input("Check-out", date.today() + timedelta(days=34))
    adults = col3.number_input("Adults", min_value=1, max_value=10, value=2)
    notes = st.text_input("Preferences (optional)", placeholder="near the city centre, free breakfast")
    submitted = st.form_submit_button("Search hotels")

if submitted:
    request = (
        f"Hotels in {location} from {check_in.isoformat()} to {check_out.isoformat()} "
        f"for {adults} adults. {notes}"
    )
    with st.spinner("Agents are searching Kayak... (1-3 minutes)"):
        try:
            answer = find_hotels(request)
            st.markdown(re.sub(r"<think>.*?</think>", "", answer, flags=re.S).strip())
        except Exception as e:
            st.error(f"Something went wrong: {e}")
