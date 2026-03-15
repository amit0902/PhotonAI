import streamlit as st
from auth.auth_service import create_user, authenticate


def login_page():

    st.title("PhotonAI Login")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    # -------------------------
    # LOGIN
    # -------------------------

    with tab1:

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            user = authenticate(username, password)

            if user:

                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.role = user["role"]

                st.rerun()

            else:
                st.error("Invalid credentials")

    # -------------------------
    # SIGNUP
    # -------------------------

    with tab2:

        email = st.text_input("Email")
        username = st.text_input("Create Username")
        password = st.text_input("Create Password", type="password")

        if st.button("Create Account"):

            if create_user(email, username, password):
                st.success("Account created! Please login.")
            else:
                st.error("Username or Email already exists.")