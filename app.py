import streamlit as st
from dotenv import load_dotenv
import os
import time

from utils.groq_llm import GroqChatLLM
from graph.graph_builder import build_graph
from services.pdf_report_service import generate_pdf_report
<<<<<<< HEAD


# ----------------------------------------
# Page Setup
# ----------------------------------------
load_dotenv()

st.set_page_config(
    page_title="Solar Advisor",
=======
from database.db import init_db
from auth.auth_ui import login_page
from services.lead_service import save_lead


# ----------------------------------------
# Page Setup (MUST BE FIRST STREAMLIT CALL)
# ----------------------------------------

st.set_page_config(
    page_title="PhotonAI Solar Advisor",
>>>>>>> 36c2420 (Modified version of PhotonAI)
    page_icon="☀️",
    layout="wide"
)

<<<<<<< HEAD

# ----------------------------------------
# Custom Styling
# ----------------------------------------
=======
load_dotenv()
init_db()


# ----------------------------------------
# Authentication
# ----------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
    st.stop()


# ----------------------------------------
# Admin Routing
# ----------------------------------------

if st.session_state.role == "admin":

    from admin.admin_dashboard import admin_dashboard
    admin_dashboard()
    st.stop()


# ----------------------------------------
# Session Flags
# ----------------------------------------

if "lead_saved" not in st.session_state:
    st.session_state.lead_saved = False

if "streamed_messages" not in st.session_state:
    st.session_state.streamed_messages = set()


# ----------------------------------------
# Styling
# ----------------------------------------

>>>>>>> 36c2420 (Modified version of PhotonAI)
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
<<<<<<< HEAD
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

=======

header_left, header_right = st.columns([6,2])

with header_left:

    st.markdown("""
    <h1 style='margin-bottom:0;'>PhotonAI</h1>
    <p style='font-size:18px; color:gray; margin-top:0;'>
    Intelligent Rooftop Solar Design & Advisory Platform
    </p>
    """, unsafe_allow_html=True)


with header_right:

    st.markdown(
        f"""
        <div style="text-align:right; margin-top:10px">
            <b>👤 {st.session_state.username}</b><br>
            <span style="font-size:12px;color:gray">
            {st.session_state.role}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Logout"):

        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.rerun()


st.markdown("<hr>", unsafe_allow_html=True)


# ----------------------------------------
# Streaming Text Helper
# ----------------------------------------

def stream_text(text, delay=0.02):

>>>>>>> 36c2420 (Modified version of PhotonAI)
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
<<<<<<< HEAD
=======

>>>>>>> 36c2420 (Modified version of PhotonAI)
if "graph" not in st.session_state:

    llm = GroqChatLLM(api_key=os.getenv("GROQ_API_KEY"))
    st.session_state.graph = build_graph(llm)


# ----------------------------------------
# Initialize Conversation State
# ----------------------------------------
<<<<<<< HEAD
=======

>>>>>>> 36c2420 (Modified version of PhotonAI)
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
<<<<<<< HEAD
if not st.session_state.state["messages"]:
=======

if "graph_initialized" not in st.session_state:

>>>>>>> 36c2420 (Modified version of PhotonAI)
    st.session_state.state = st.session_state.graph.invoke(
        st.session_state.state
    )

<<<<<<< HEAD
=======
    st.session_state.graph_initialized = True

>>>>>>> 36c2420 (Modified version of PhotonAI)

# ----------------------------------------
# Display Chat Messages
# ----------------------------------------
<<<<<<< HEAD
=======

>>>>>>> 36c2420 (Modified version of PhotonAI)
for msg in st.session_state.state["messages"]:

    with st.chat_message(msg["role"]):

        if msg["role"] == "assistant":
            stream_text(msg["content"])
        else:
            st.markdown(msg["content"])

<<<<<<< HEAD
        # Display break-even chart after financial message
=======
        # Display break-even chart
>>>>>>> 36c2420 (Modified version of PhotonAI)
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

<<<<<<< HEAD
if st.session_state.state.get("annual_kwh"):

    pdf = generate_pdf_report(st.session_state.state)

=======

# ----------------------------------------
# PDF Generation + Lead Capture
# ----------------------------------------

if (
    st.session_state.state.get("annual_kwh")
    and not st.session_state.lead_saved
):

    pdf = generate_pdf_report(st.session_state.state)

    save_lead(
        st.session_state.state,
        st.session_state.username,
        st.session_state.role
    )

>>>>>>> 36c2420 (Modified version of PhotonAI)
    st.download_button(
        label="📄 Download Solar Analysis Report",
        data=pdf,
        file_name="solar_analysis_report.pdf",
        mime="application/pdf"
    )

<<<<<<< HEAD
# ----------------------------------------
# Chat Input
# ----------------------------------------
=======
    st.session_state.lead_saved = True


# ----------------------------------------
# Chat Input
# ----------------------------------------

>>>>>>> 36c2420 (Modified version of PhotonAI)
user_input = st.chat_input("Type your response...")


if user_input:

<<<<<<< HEAD
    st.session_state.state["messages"].append({
        "role": "user",
        "content": user_input
    })
=======
    if (
        not st.session_state.state["messages"]
        or st.session_state.state["messages"][-1]["content"] != user_input
    ):

        st.session_state.state["messages"].append({
            "role": "user",
            "content": user_input
        })
>>>>>>> 36c2420 (Modified version of PhotonAI)

    with st.status("Analyzing solar performance...", expanded=False) as status:

        st.session_state.state = st.session_state.graph.invoke(
            st.session_state.state
        )

<<<<<<< HEAD
        status.update(label="Solar analysis complete ✅", state="complete")
=======
        # Remove duplicate assistant messages
        cleaned = []
        seen = set()

        for msg in st.session_state.state["messages"]:

            key = (msg["role"], msg["content"])

            if key not in seen:
                cleaned.append(msg)
                seen.add(key)

        st.session_state.state["messages"] = cleaned

        status.update(
            label="Solar analysis complete ✅",
            state="complete"
        )
>>>>>>> 36c2420 (Modified version of PhotonAI)

    st.rerun()


# ----------------------------------------
<<<<<<< HEAD
# Restart Button
# ----------------------------------------
st.markdown("---")

if st.button("🔄 Restart Conversation"):
    st.session_state.clear()
    st.rerun()
=======
# Restart Conversation
# ----------------------------------------

st.markdown("---")

if st.button("🔄 Restart Conversation"):

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

    # Reset flags
    st.session_state.graph_initialized = False
    st.session_state.streamed_messages = set()
    st.session_state.lead_saved = False

    # Run graph again
    st.session_state.state = st.session_state.graph.invoke(
        st.session_state.state
    )

    st.session_state.graph_initialized = True

    st.rerun()
>>>>>>> 36c2420 (Modified version of PhotonAI)
