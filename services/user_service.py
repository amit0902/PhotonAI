from db.database import get_connection
from utils.security import hash_password


def create_user(username, password, role="user"):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, hash_password(password), role)
    )

    conn.commit()
    conn.close()


def get_user(username):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    user = cur.fetchone()

    conn.close()

    return user