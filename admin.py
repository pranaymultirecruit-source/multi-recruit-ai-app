import streamlit as st
import json
import os
import time
from datetime import datetime

# --------------------------
# CONFIG
# --------------------------
CHAT_FILE = "support_chat.json"
ADMIN_PASSWORD = "pranay@8503"  # 🔒 Change this password
REFRESH_INTERVAL = 5  # seconds (auto-refresh delay)

st.set_page_config(page_title="💬 Live Tech Support", page_icon="💬", layout="centered")

# --------------------------
# Ensure chat file exists
# --------------------------
if not os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "w") as f:
        json.dump({"messages": []}, f)

# --------------------------
# Load / Save helpers
# --------------------------
def load_chat():
    with open(CHAT_FILE, "r") as f:
        data = json.load(f)
    if "messages" not in data:
        data["messages"] = []
    return data

def save_chat(data):
    with open(CHAT_FILE, "w") as f:
        json.dump(data, f, indent=2)

# --------------------------
# Sidebar: Admin Login
# --------------------------
st.sidebar.header("⚙️ Settings")

admin_mode = False
if st.sidebar.checkbox("Enable Admin Mode"):
    password = st.sidebar.text_input("Enter Admin Password", type="password")
    if password == ADMIN_PASSWORD:
        st.sidebar.success("✅ Access granted — Admin Mode Active")
        admin_mode = True
    elif password:
        st.sidebar.error("❌ Incorrect Password")

if not admin_mode:
    st.sidebar.info("👤 User Mode — You can message tech support.")

# --------------------------
# Main Interface
# --------------------------
st.title("💬 Live Tech Support")

data = load_chat()
st.markdown("### Chat History")

# Display chat messages
for msg in data["messages"]:
    sender = "🧑 User" if msg["role"] == "user" else "👨‍💻 Admin"
    color = "#f0f2f6" if msg["role"] == "user" else "#e8f5e9"
    st.markdown(
        f"<div style='background:{color};padding:10px;border-radius:8px;margin:6px 0;'>"
        f"<b>{sender}:</b> {msg['text']}</div>",
        unsafe_allow_html=True
    )

# --------------------------
# Message Input
# --------------------------
user_input = st.text_input("Type your message here...")

col1, col2 = st.columns(2)

with col1:
    if st.button("Send"):
        if user_input.strip():
            role = "admin" if admin_mode else "user"
            data["messages"].append({
                "role": role,
                "text": user_input.strip(),
                "time": str(datetime.now())
            })
            save_chat(data)
            st.success("✅ Message sent!")
            st.rerun()

with col2:
    if admin_mode and st.button("🗑️ Clear Chat"):
        save_chat({"messages": []})
        st.warning("🧹 Chat cleared!")
        st.rerun()

# --------------------------
# Auto-refresh setup (no external package)
# --------------------------
st.markdown(
    f"<p style='color:gray;font-size:12px'>🔄 Auto-refreshing every {REFRESH_INTERVAL} seconds...</p>",
    unsafe_allow_html=True
)

# Use session_state to avoid tight infinite loop
if "last_refresh" not in st.session_state:
    st.session_state["last_refresh"] = time.time()
else:
    if time.time() - st.session_state["last_refresh"] > REFRESH_INTERVAL:
        st.session_state["last_refresh"] = time.time()
        st.rerun()

st.caption(f"⏱️ Last refreshed at {datetime.now().strftime('%H:%M:%S')}")
