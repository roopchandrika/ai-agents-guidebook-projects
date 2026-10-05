import re

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from crew import find_flights  # noqa: E402

st.set_page_config(page_title="Flight Finder", page_icon="✈️")
st.title("✈️ Multi-agent Flight Finder")
st.caption("CrewAI agents + Browserbase headless browser + Kayak")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("e.g. Flights from SFO to JFK on 21 November, returning 28 November"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Agents are searching Kayak... (1-3 minutes)"):
            try:
                answer = find_flights(prompt)
                answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.S).strip()
            except Exception as e:
                answer = f"Something went wrong: `{e}`"
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
