

# # new one
# # backend/proctor.py

# # Stores per-user proctoring state (in-memory)
# user_state = {}

# MAX_WARNINGS = 2


# def handle_violation(event_type, user_id):
#     """
#     Global Proctoring Rule:
#     - Any violation increments warning
#     - 2 warnings → terminate exam

#     Returns:
#         status   -> "ok" | "warning" | "terminate"
#         warnings -> int
#         reason   -> string
#     """

#     # Initialize user state
#     if user_id not in user_state:
#         user_state[user_id] = {
#             "warnings": 0,
#             "terminated": False
#         }

#     # If already terminated
#     if user_state[user_id]["terminated"]:
#         return "terminate", user_state[user_id]["warnings"], "Exam already terminated"

#     # ⚠️ Any event reaching here is a VALID violation
#     user_state[user_id]["warnings"] += 1

#     # ❌ Terminate if warnings exceeded
#     if user_state[user_id]["warnings"] >= MAX_WARNINGS:
#         user_state[user_id]["terminated"] = True
#         return (
#             "terminate",
#             user_state[user_id]["warnings"],
#             f"Test closed due to repeated violations ({event_type})"
#         )

#     # 🟡 Warning state
#     return (
#         "warning",
#         user_state[user_id]["warnings"],
#         f"Warning: {event_type} detected"
#     )

# backend/proctor.py

user_state = {}
MAX_WARNINGS = 2

CRITICAL_EVENTS = {
    "phone_detected",
    "multiple_faces"
}

def handle_violation(event_type, user_id):
    """
    Returns:
    status   -> ok | warning | terminate
    warnings -> int
    reason   -> string
    """

    if user_id not in user_state:
        user_state[user_id] = {
            "warnings": 0,
            "terminated": False
        }

    state = user_state[user_id]

    if state["terminated"]:
        return "terminate", state["warnings"], "Exam already terminated"

    # 🔴 CRITICAL EVENTS → warning based (not instant)
    if event_type in CRITICAL_EVENTS:
        state["warnings"] += 1

        if state["warnings"] >= MAX_WARNINGS:
            state["terminated"] = True
            return "terminate", state["warnings"], "Repeated critical violations"

        return "warning", state["warnings"], "Critical violation detected"

    return "ok", state["warnings"], "Normal behavior"
