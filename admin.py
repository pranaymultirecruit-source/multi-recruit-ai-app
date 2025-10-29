import streamlit as st
import json
import os
import time
from datetime import datetime

# --------------------------
# CONFIG
# --------------------------
CHAT_FILE = "support_chat.json"
REFRESH_INTERVAL = 2  # seconds (auto-refresh)
ADMIN_KEY = "pranay@8503"

st.set_page_config(page_title="💬 Live Tech Support", page_icon="💬")

# --------------------------
# Helpers: load/save and normalize
# --------------------------
def load_raw():
    if not os.path.exists(CHAT_FILE):
        return {}
    try:
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def normalize_data(raw):
    """Ensure consistent structure for all tickets"""
    if raw is None:
        return {}
    if isinstance(raw, list):
        new_ticket = f"TCKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            new_ticket: {
                "messages": [m if isinstance(m, dict) else {"role": "user", "text": str(m), "time": ""} for m in raw],
                "closed": False,
                "created_at": str(datetime.now())
            }
        }

    if isinstance(raw, dict):
        normalized = {}
        for k, v in raw.items():
            if isinstance(v, list):
                messages = []
                for m in v:
                    if isinstance(m, dict):
                        role = m.get("role", "user")
                        text = m.get("text", m.get("message", str(m)))
                        time_str = m.get("time", m.get("timestamp", ""))
                        messages.append({"role": role, "text": text, "time": time_str})
                    else:
                        messages.append({"role": "user", "text": str(m), "time": ""})
                normalized[k] = {"messages": messages, "closed": False, "created_at": str(datetime.now())}
                continue

            if isinstance(v, dict):
                if "messages" in v:
                    messages_raw = v.get("messages", [])
                    messages = []
                    for m in messages_raw:
                        if isinstance(m, dict):
                            role = m.get("role", "user")
                            text = m.get("text", m.get("message", str(m)))
                            time_str = m.get("time", m.get("timestamp", ""))
                            messages.append({"role": role, "text": text, "time": time_str})
                        else:
                            messages.append({"role": "user", "text": str(m), "time": ""})
                    closed = bool(v.get("closed", False))
                    created_at = v.get("created_at", str(datetime.now()))
                    normalized[k] = {"messages": messages, "closed": closed, "created_at": created_at}
                    continue
                else:
                    maybe_list = []
                    for _, sub_v in v.items():
                        if isinstance(sub_v, dict):
                            role = sub_v.get("role", "user")
                            text = sub_v.get("text", sub_v.get("message", str(sub_v)))
                            time_str = sub_v.get("time", sub_v.get("timestamp", ""))
                            maybe_list.append({"role": role, "text": text, "time": time_str})
                        else:
                            maybe_list.append({"role": "user", "text": str(sub_v), "time": ""})
                    if maybe_list:
                        normalized[k] = {"messages": maybe_list, "closed": False, "created_at": str(datetime.now())}
                        continue

            normalized[k] = {
                "messages": [{"role": "user", "text": str(v), "time": ""}],
                "closed": False,
                "created_at": str(datetime.now())
            }

        return normalized
    return {}

def load_chat():
    raw = load_raw()
    normalized = normalize_data(raw)
    save_chat(normalized)
    return normalized

def save_chat(data):
    with open(CHAT_FILE, "w") as f:
        json.dump(data, f, indent=2)

# --------------------------
# UI Title and input
# --------------------------
st.title("💬 Live Tech Support")

ticket_or_key = st.text_input("🔑 Enter Ticket ID ")

if not ticket_or_key:
    st.stop()

# --------------------------
# Load data
# --------------------------
data = load_chat()

# --------------------------
# ADMIN MODE
# --------------------------
if ticket_or_key.strip() == ADMIN_KEY:
    st.success("✅ Admin Mode Active — Manage Tickets Below")

    open_tickets = [tid for tid, info in data.items() if not info.get("closed")]
    closed_tickets = [tid for tid, info in data.items() if info.get("closed")]
    ticket_choices = open_tickets + closed_tickets

    if not ticket_choices:
        st.info("No tickets found.")
        st.stop()

    selected_ticket = st.selectbox("🎟️ Select a Ticket to View", ticket_choices)
    ticket_info = data.get(selected_ticket, {"messages": [], "closed": False, "created_at": str(datetime.now())})

    status = "Closed" if ticket_info.get("closed") else "Open"
    st.markdown(f"### 💬 Chat for Ticket: `{selected_ticket}` — **{status}**")

    # Display chat
    for msg in ticket_info.get("messages", []):
        sender = "🧑 User" if msg.get("role") == "user" else "👨‍💻 Admin"
        text = msg.get("text", "")
        time_str = msg.get("time", "")
        color = "#f0f2f6" if "User" in sender else "#e8f5e9"
        st.markdown(
            f"<div style='background:{color};padding:10px;border-radius:8px;margin:6px 0;'>"
            f"<b>{sender}:</b> {text}"
            f"<div style='font-size:11px;color:#666;margin-top:4px;'>{time_str}</div></div>",
            unsafe_allow_html=True
        )

    admin_msg = st.text_input("💬 Type your reply to this user:", key="admin_msg_input")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Send Reply"):
            if admin_msg.strip():
                ticket_info["messages"].append({
                    "role": "admin",
                    "text": admin_msg.strip(),
                    "time": str(datetime.now())
                })
                data[selected_ticket] = ticket_info
                save_chat(data)
                st.success("✅ Reply sent!")
                st.session_state.admin_msg_input = ""  # clear input box
                st.rerun()
    with col2:
        if st.button("✅ Close Ticket"):
            ticket_info["closed"] = True
            data[selected_ticket] = ticket_info
            save_chat(data)
            st.warning(f"🎟️ Ticket `{selected_ticket}` marked closed.")
            st.rerun()

    st.markdown("---")
    st.markdown("#### Open Tickets")
    st.write(", ".join(open_tickets) if open_tickets else "None")
    st.markdown("#### Closed Tickets")
    st.write(", ".join(closed_tickets) if closed_tickets else "None")

# --------------------------
# USER MODE
# --------------------------
else:
    ticket_id = ticket_or_key.strip()
    if ticket_id not in data:
        data[ticket_id] = {"messages": [], "closed": False, "created_at": str(datetime.now())}
        save_chat(data)

    ticket_info = data[ticket_id]
    if ticket_info.get("closed"):
        st.warning("🚫 This ticket has been closed by admin.")

    st.markdown(f"### 🎟️ Chat for Ticket: `{ticket_id}`")

    for msg in ticket_info.get("messages", []):
        sender = "🧑 You" if msg.get("role") == "user" else "👨‍💻 Admin"
        text = msg.get("text", "")
        time_str = msg.get("time", "")
        color = "#f0f2f6" if "You" in sender else "#e8f5e9"
        st.markdown(
            f"<div style='background:{color};padding:10px;border-radius:8px;margin:6px 0;'>"
            f"<b>{sender}:</b> {text}"
            f"<div style='font-size:11px;color:#666;margin-top:4px;'>{time_str}</div></div>",
            unsafe_allow_html=True
        )

    if not ticket_info.get("closed"):
        user_msg = st.text_input("✉️ Type your message:", key="user_msg_input")
        if st.button("Send Message"):
            if user_msg.strip():
                ticket_info["messages"].append({
                    "role": "user",
                    "text": user_msg.strip(),
                    "time": str(datetime.now())
                })
                data[ticket_id] = ticket_info
                save_chat(data)
                st.success("✅ Message sent!")
                st.session_state.user_msg_input = ""
                st.rerun()
    else:
        st.info("Ticket closed — new messages disabled.")

# --------------------------
# AUTO REFRESH
# --------------------------
st.markdown(
    f"<p style='color:gray;font-size:12px;text-align:center;'> {REFRESH_INTERVAL} seconds...</p>",
    unsafe_allow_html=True
)

if "last_refresh" not in st.session_state:
    st.session_state["last_refresh"] = time.time()
else:
    if time.time() - st.session_state["last_refresh"] > REFRESH_INTERVAL:
        st.session_state["last_refresh"] = time.time()
        st.rerun()
