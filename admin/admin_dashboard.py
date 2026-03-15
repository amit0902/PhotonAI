import streamlit as st
import pandas as pd
from services.lead_service import get_all_leads
from services.lead_analysis_service import analyze_lead



def admin_dashboard():

    # -----------------------------------
    # Header with Logout
    # -----------------------------------

    header_left, header_right = st.columns([6,1])

    with header_left:
        st.title("PhotonAI Admin Dashboard")

    with header_right:

        if st.button("Logout"):

            for key in list(st.session_state.keys()):
                del st.session_state[key]

            st.rerun()

    # -----------------------------------
    # Load Leads
    # -----------------------------------

    leads = get_all_leads()

    if not leads:
        st.info("No solar requests generated yet.")
        return

    df = pd.DataFrame([dict(row) for row in leads])

    # -----------------------------------
    # Remove Duplicate Leads
    # -----------------------------------

    df = df.drop_duplicates(
        subset=["username", "city", "monthly_units", "system_kw"]
    )

    # -----------------------------------
    # Select Columns
    # -----------------------------------

    df = df[[
        "username",
        "city",
        "monthly_units",
        "system_kw",
        "estimated_price",
        "created_at"
    ]]

    df.columns = [
        "User",
        "City",
        "Power Demand (kWh/month)",
        "PV System Size (kW)",
        "Estimated PV Cost (₹)",
        "Date"
    ]

    # -----------------------------------
    # Display Table
    # -----------------------------------

    st.dataframe(df, use_container_width=True)

    # -----------------------------------
    # Dashboard Metrics
    # -----------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Leads",
        len(df)
    )

    col2.metric(
        "Average System Size",
        f"{round(df['PV System Size (kW)'].mean(),2)} kW"
    )

    col3.metric(
        "Potential Revenue",
        f"₹{int(df['Estimated PV Cost (₹)'].sum()):,}"
    )

    st.markdown("---")
    st.subheader("Lead Profitability Insights")

    for _, row in df.iterrows():

        lead_dict = {
            "username": row["User"],
            "city": row["City"],
            "monthly_units": row["Power Demand (kWh/month)"],
            "system_kw": row["PV System Size (kW)"],
            "estimated_price": row["Estimated PV Cost (₹)"]
        }

        analysis = analyze_lead(lead_dict)

        with st.container():

            st.markdown(f"""
    ### Customer: {lead_dict['username']} ({lead_dict['city']})

    **Estimated PV Size:** {lead_dict['system_kw']} kW  
    **Estimated Project Value:** ₹{lead_dict['estimated_price']:,.0f}  
    **Estimated Profit Margin:** {analysis['margin_percent']}%

    **Sales Priority:** {analysis['priority']}

    Key Observations:
    """)

            for note in analysis["notes"]:
                st.write(f"• {note}")

            st.markdown("---")
