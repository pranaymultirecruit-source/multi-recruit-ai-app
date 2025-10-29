import streamlit as st
import json
import os
import re
import time
from datetime import datetime

# --------------------------
# CONFIG
# --------------------------
CHAT_FILE = "support_chat.json"
REFRESH_INTERVAL = 2  # seconds
ADMIN_KEY = "pranay@8503"

TICKET_REGEX = re.compile(r"^TCKT-\d{8}-[A-Z0-9]{6}$")

st.set_page_config(page_title="💬 Live Tech Support", page_icon="💬", layout="wide")


# --------------------------
# Helpers: load/save
# --------------------------
def load_raw():
    if not os.path.exists(CHAT_FILE):
        return {}
    try:
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def normalize_data(raw):
    if raw is None:
        return {}
    if isinstance(raw, list):
        new_ticket = f"TCKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            new_ticket: {
                "messages": [
                    m if isinstance(m, dict) else {"role": "user", "text": str(m), "time": ""}
                    for m in raw
                ],
                "closed": False,
                "created_at": str(datetime.now()),
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
                normalized[k] = {
                    "messages": messages,
                    "closed": False,
                    "created_at": str(datetime.now()),
                }
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
                    normalized[k] = {
                        "messages": messages,
                        "closed": closed,
                        "created_at": created_at,
                    }
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
                        normalized[k] = {
                            "messages": maybe_list,
                            "closed": False,
                            "created_at": str(datetime.now()),
                        }
                        continue

            normalized[k] = {
                "messages": [{"role": "user", "text": str(v), "time": ""}],
                "closed": False,
                "created_at": str(datetime.now()),
            }
        return normalized
    return {}


def load_chat():
    raw = load_raw()
    normalized = normalize_data(raw)
    save_chat(normalized)
    return normalized


def save_chat(data):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# --------------------------
# UI
# --------------------------
st.title("💬 Live Tech Support")
ticket_or_key = st.text_input("🔑 Enter Ticket ID ")

if not ticket_or_key:
    st.stop()

ticket_or_key = ticket_or_key.strip()
is_admin = ticket_or_key == ADMIN_KEY
data = load_chat()

if not is_admin and not TICKET_REGEX.match(ticket_or_key):
    st.error("Please enter a correct Ticket ID")
    st.stop()

if not is_admin:
    if ticket_or_key not in data:
        data[ticket_or_key] = {"messages": [], "closed": False, "created_at": str(datetime.now())}
        save_chat(data)

open_tickets = [tid for tid, info in data.items() if not info.get("closed")]
closed_tickets = [tid for tid, info in data.items() if info.get("closed")]

# --------------------------
# Admin Mode
# --------------------------
if is_admin:
    if "admin_selected_ticket" not in st.session_state or st.session_state.admin_selected_ticket not in open_tickets:
        st.session_state.admin_selected_ticket = open_tickets[0] if open_tickets else None

    left_col, mid_col, right_col = st.columns([1.2, 2.6, 1.2])

    with left_col:
        st.markdown("### 📂 Open Tickets")
        if not open_tickets:
            st.info("No open tickets.")
        else:
            sel = st.radio(
                "Select an open ticket",
                options=open_tickets,
                index=open_tickets.index(st.session_state.admin_selected_ticket)
                if st.session_state.admin_selected_ticket in open_tickets
                else 0,
                key="open_radio",
            )
            st.session_state.admin_selected_ticket = sel

    with right_col:
        st.markdown("### 📦 Closed Tickets")
        if not closed_tickets:
            st.info("No closed tickets.")
        else:
            sel_closed = st.selectbox(
                "View closed ticket (read-only):", options=["-- select --"] + closed_tickets, index=0, key="closed_select"
            )
            if sel_closed and sel_closed != "-- select --":
                st.markdown(f"#### Viewing Closed Ticket `{sel_closed}`")
                tinfo = data.get(sel_closed, {"messages": [], "closed": True, "created_at": ""})
                for msg in tinfo.get("messages", []):
                    sender = "🧑 User" if msg.get("role") == "user" else "👨‍💻 Admin"
                    bg = "#f0f2f6" if sender.startswith("🧑") else "#e8f5e9"
                    st.markdown(
                        f"<div style='background:{bg};padding:10px;border-radius:8px;margin:6px 0;'>"
                        f"<b>{sender}:</b> {msg.get('text')}"
                        f"<div style='font-size:11px;color:#666;margin-top:6px;'>{msg.get('time','')}</div></div>",
                        unsafe_allow_html=True,
                    )

    with mid_col:
        selected = st.session_state.admin_selected_ticket
        if not selected:
            st.info("No open ticket selected.")
        else:
            ticket_info = data.get(selected, {"messages": [], "closed": False, "created_at": ""})
            status = "Closed" if ticket_info.get("closed") else "Open"
            st.markdown(f"### 💬 Ticket: `{selected}` — **{status}**")

            for msg in ticket_info.get("messages", []):
                sender = "🧑 User" if msg.get("role") == "user" else "👨‍💻 Admin"
                bg = "#f0f2f6" if sender.startswith("🧑") else "#e8f5e9"
                st.markdown(
                    f"<div style='background:{bg};padding:10px;border-radius:8px;margin:6px 0;'>"
                    f"<b>{sender}:</b> {msg.get('text')}"
                    f"<div style='font-size:11px;color:#666;margin-top:6px;'>{msg.get('time','')}</div></div>",
                    unsafe_allow_html=True,
                )

            if ticket_info.get("closed"):
                st.warning("This ticket has been closed. New messages are disabled.")
            else:
                reply_key = f"admin_reply_{selected}"
                if reply_key not in st.session_state:
                    st.session_state[reply_key] = ""
                st.text_area("Reply to user:", key=reply_key, height=100)
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Send Reply", key=f"send_{selected}"):
                        reply_text = st.session_state.get(reply_key, "").strip()
                        if reply_text:
                            ticket_info.setdefault("messages", []).append(
                                {"role": "admin", "text": reply_text, "time": str(datetime.now())}
                            )
                            data[selected] = ticket_info
                            save_chat(data)
                            st.success(f"Reply sent to `{selected}`.")
                            st.session_state.pop(reply_key, None)
                            st.query_params.update({"refresh": str(time.time())})
                            st.stop()
                        else:
                            st.warning("Reply cannot be empty.")
                with col_b:
                    if st.button("Close Ticket", key=f"close_{selected}"):
                        ticket_info["closed"] = True
                        data[selected] = ticket_info
                        save_chat(data)
                        st.warning(f"🎟️ Ticket `{selected}` marked closed.")
                        st.query_params.update({"refresh": str(time.time())})
                        st.stop()

# --------------------------
# User Mode
# --------------------------
else:
    st.markdown("### 💬 Live Chat")
    ticket_id = ticket_or_key
    ticket_info = data.get(ticket_id, {"messages": [], "closed": False, "created_at": str(datetime.now())})
    status = "Closed" if ticket_info.get("closed") else "Open"
    st.markdown(f"#### Ticket: `{ticket_id}` — **{status}**")

    for msg in ticket_info.get("messages", []):
        sender = "🧑 You" if msg.get("role") == "user" else "👨‍💻 Admin"
        bg = "#f0f2f6" if sender.startswith("🧑") else "#e8f5e9"
        st.markdown(
            f"<div style='background:{bg};padding:10px;border-radius:8px;margin:6px 0;'>"
            f"<b>{sender}:</b> {msg.get('text')}"
            f"<div style='font-size:11px;color:#666;margin-top:6px;'>{msg.get('time','')}</div></div>",
            unsafe_allow_html=True,
        )

    if ticket_info.get("closed"):
        st.warning("This ticket has been closed by admin. New messages are disabled.")
    else:
        user_key = f"user_msg_{ticket_id}"
        if user_key not in st.session_state:
            st.session_state[user_key] = ""
        st.text_area("Type your message:", key=user_key, height=120)
        if st.button("Send Message", key=f"send_user_{ticket_id}"):
            msg_text = st.session_state.get(user_key, "").strip()
            if msg_text:
                ticket_info.setdefault("messages", []).append(
                    {"role": "user", "text": msg_text, "time": str(datetime.now())}
                )
                data[ticket_id] = ticket_info
                save_chat(data)
                st.success("✅ Message sent!")
                st.session_state.pop(user_key, None)
                st.query_params.update({"refresh": str(time.time())})
                st.stop()
            else:
                st.warning("Message cannot be empty.")

# --------------------------
# Auto-refresh
# --------------------------
st.markdown(
    f"<p style='color:gray;font-size:12px;text-align:center;'>Auto-refresh every {REFRESH_INTERVAL} seconds</p>",
    unsafe_allow_html=True,
)

if "last_refresh" not in st.session_state:
    st.session_state["last_refresh"] = time.time()
else:
    if time.time() - st.session_state["last_refresh"] > REFRESH_INTERVAL:
        st.session_state["last_refresh"] = time.time()
        st.query_params.update({"refresh": str(time.time())})
        st.stop()
