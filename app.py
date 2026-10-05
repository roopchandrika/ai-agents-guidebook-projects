import asyncio

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from memory_agent import ZepMemory, build_zep, chat_turn, ensure_user, new_thread  # noqa: E402

st.set_page_config(page_title="Agent with Memory", page_icon="🧠")
st.title("🧠 AI Agent with Human-like Memory")
st.caption("Zep Cloud memory layer + Microsoft AutoGen + local Qwen 3")

with st.sidebar:
    st.header("User")
    first_name = st.text_input("Your first name", "Alex")
    user_id = st.text_input("User ID", "alex-demo")
    if st.button("Start new session", type="primary"):
        zep = build_zep()
        ensure_user(zep, user_id, first_name)
        st.session_state.zep = zep
        st.session_state.thread_id = new_thread(zep, user_id)
        st.session_state.messages = []
        st.session_state.agent_state = None
    if "thread_id" in st.session_state:
        st.success(f"Session: {st.session_state.thread_id}")
        if st.button("Show what Zep remembers"):
            mem = ZepMemory(st.session_state.zep, st.session_state.thread_id, first_name)
            st.text(mem.get_context() or "(nothing yet — facts appear after a few messages)")
    st.markdown(
        "Tip: tell the agent about yourself, start a **new session**, and ask what it remembers."
    )

if "thread_id" not in st.session_state:
    st.info("Enter your name and click **Start new session** in the sidebar.")
    st.stop()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Say something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    memory = ZepMemory(st.session_state.zep, st.session_state.thread_id, first_name)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply, st.session_state.agent_state = asyncio.run(
                chat_turn(memory, prompt, st.session_state.agent_state)
            )
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
