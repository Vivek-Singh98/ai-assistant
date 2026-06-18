from dotenv import load_dotenv
load_dotenv()

import html
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import Tool

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="centered")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Session State ---
if "memory" not in st.session_state:
    st.session_state.memory = MemorySaver()
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Agent Setup ---
llm = ChatGroq(model="openai/gpt-oss-20b")

search_tool = Tool(
    name="google_search",
    func=GoogleSerperAPIWrapper().run,
    description="Search Google for current information, news, or facts."
)

agent = create_agent(
    model=llm,
    tools=[search_tool],
    checkpointer=st.session_state.memory
)

# --- Header ---
st.markdown("""
    <div class="header">
        <span class="header-icon">🤖</span>
        <h2>AI Assistant</h2>
    </div>
""", unsafe_allow_html=True)

# --- Chat History ---
if not st.session_state.messages:
    st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">💬</div>
            <p>Ask me anything — I can search the web for real-time answers.</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div style="display:block; overflow:hidden;">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role_class = "user-msg" if msg["role"] == "user" else "ai-msg"
        label = "You" if msg["role"] == "user" else "Assistant"
        content = html.escape(msg["content"])
        st.markdown(f"""
            <div class="chat-bubble {role_class}">
                <span class="msg-label">{label}</span>
                <p>{content}</p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('<div style="clear:both;"></div></div>', unsafe_allow_html=True)

# --- Input ---
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Thinking..."):
        try:
            response = agent.invoke(
                {"messages": [{"role": "user", "content": prompt}]},
                config={"configurable": {"thread_id": "user_session"}}
            )
            answer = response["messages"][-1].content
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Something went wrong: {str(e)}"
            })

    st.rerun()