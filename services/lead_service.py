from database.db import get_connection


def save_lead(state, username, role):

    # Do not store admin activity
    if role == "admin":
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO solar_requests
        (username, city, monthly_units, system_kw, estimated_price)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            username,
            state.get("city"),
            state.get("monthly_units"),
            state.get("system_kw"),
            state.get("net_system_cost")
        )
    )

    conn.commit()
    conn.close()


def get_all_leads():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM solar_requests
    ORDER BY created_at DESC
    """)

    rows = cur.fetchall()

    conn.close()

    return rows
