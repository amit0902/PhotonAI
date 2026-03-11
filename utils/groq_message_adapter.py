def normalize_messages(messages):
    """
    Convert LangGraph / agent-style roles into Groq-compatible roles.
    Allowed roles: system, user, assistant
    """

    normalized = []

    for msg in messages:
        role = msg.get("role", "user")

        if role in ("human", "user"):
            role = "user"
        elif role in ("ai", "assistant"):
            role = "assistant"
        elif role == "system":
            role = "system"
        else:
            # tool / function / agent → assistant
            role = "assistant"

        normalized.append({
            "role": role,
            "content": str(msg.get("content", ""))
        })

    return normalized

def map_langchain_role_to_groq(role: str) -> str:
    if role in ("human", "user"):
        return "user"
    if role in ("ai", "assistant"):
        return "assistant"
    if role == "system":
        return "system"
    # tool / function / other → assistant
    return "assistant"

