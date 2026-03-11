import streamlit as st
from dotenv import load_dotenv
import os
import time

from utils.groq_llm import GroqChatLLM
from graph.graph_builder import build_graph
from services.pdf_report_service import generate_pdf_report


# ----------------------------------------
# Page Setup
# ----------------------------------------
load_dotenv()

st.set_page_config(
    page_title="Solar Advisor",
    page_icon="☀️",
    layout="wide"
)


# ----------------------------------------
# Custom Styling
# ----------------------------------------
st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}
h1 {
    color: #1f4e79;
}
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------
# Header
# ----------------------------------------
st.markdown("""
<h1>Photon AI</h1>
<p style='font-size:18px; color:gray;'>
Intelligent Rooftop Solar Design & Advisory Platform
</p>
<hr>
""", unsafe_allow_html=True)


# ----------------------------------------
# Streaming Helper
# ----------------------------------------
def stream_text(text, delay=0.02):

    if "streamed_messages" not in st.session_state:
        st.session_state.streamed_messages = set()

    key = hash(text)

    if key in st.session_state.streamed_messages:
        st.markdown(text)
        return

    placeholder = st.empty()
    streamed = ""

    for word in text.split(" "):
        streamed += word + " "
        placeholder.markdown(streamed)
        time.sleep(delay)

    st.session_state.streamed_messages.add(key)


# ----------------------------------------
# Initialize Graph
# ----------------------------------------
if "graph" not in st.session_state:

    llm = GroqChatLLM(api_key=os.getenv("GROQ_API_KEY"))
    st.session_state.graph = build_graph(llm)


# ----------------------------------------
# Initialize Conversation State
# ----------------------------------------
if "state" not in st.session_state:

    st.session_state.state = {
        "messages": [],
        "name": None,
        "monthly_units": None,
        "city": None,
        "tilt": None,
        "azimuth": None,
        "installation_goal": None,
        "system_kw": None,
        "annual_kwh": None,
        "current_stage": "ask_name",
        "completed": False
    }


# ----------------------------------------
# Run Graph First Time
# ----------------------------------------
if not st.session_state.state["messages"]:
    st.session_state.state = st.session_state.graph.invoke(
        st.session_state.state
    )


# ----------------------------------------
# Display Chat Messages
# ----------------------------------------
for msg in st.session_state.state["messages"]:

    with st.chat_message(msg["role"]):

        if msg["role"] == "assistant":
            stream_text(msg["content"])
        else:
            st.markdown(msg["content"])

        # Display break-even chart after financial message
        if (
            msg["role"] == "assistant"
            and "break-even analysis" in msg["content"].lower()
            and st.session_state.state.get("breakeven_chart")
        ):

            st.markdown("### 📈 Break-even Analysis")

            st.plotly_chart(
                st.session_state.state["breakeven_chart"],
                use_container_width=True
            )

if st.session_state.state.get("annual_kwh"):

    pdf = generate_pdf_report(st.session_state.state)

    st.download_button(
        label="📄 Download Solar Analysis Report",
        data=pdf,
        file_name="solar_analysis_report.pdf",
        mime="application/pdf"
    )

# ----------------------------------------
# Chat Input
# ----------------------------------------
user_input = st.chat_input("Type your response...")


if user_input:

    st.session_state.state["messages"].append({
        "role": "user",
        "content": user_input
    })

    with st.status("Analyzing solar performance...", expanded=False) as status:

        st.session_state.state = st.session_state.graph.invoke(
            st.session_state.state
        )

        status.update(label="Solar analysis complete ✅", state="complete")

    st.rerun()


# ----------------------------------------
# Restart Button
# ----------------------------------------
st.markdown("---")

if st.button("🔄 Restart Conversation"):
    st.session_state.clear()
    st.rerun()