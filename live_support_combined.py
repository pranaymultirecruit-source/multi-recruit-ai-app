import streamlit as st
import json
import os

# File to store chat history
CHAT_FILE = "support_chat.json"

st.set_page_config(page_title="💬 Live Tech Support", page_icon="💬", layout="centered")

# Initialize chat storage
if not os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "w") as f:
        json.dump({"messages": []}, f)

# Load messages
with open(CHAT_FILE, "r") as f:
    data = json.load(f)

if "messages" not in data:
    data["messages"] = []

# --- SIDEBAR: Admin Mode Toggle ---
st.sidebar.header("⚙️ Settings")
admin_mode = st.sidebar.checkbox("Enable Admin Mode")

if admin_mode:
    st.sidebar.success("🧑‍💻 Admin Mode Active — You can clear chat or reply manually.")
else:
    st.sidebar.info("👤 User Mode — You can send messages to support.")

# --- MAIN INTERFACE ---
st.title("💬 Live Tech Support")

# Display chat messages
st.markdown("### Chat History")
chat_placeholder = st.empty()

def render_chat():
    with chat_placeholder.container():
        for msg in data["messages"]:
            sender = "🧑 User" if msg["role"] == "user" else "👨‍💻 Admin"
            st.markdown(f"**{sender}:** {msg['text']}")

render_chat()

# --- INPUT BOX ---
user_input = st.text_input("Type your message here...")

if st.button("Send") and user_input.strip():
    role = "admin" if admin_mode else "user"
    data["messages"].append({"role": role, "text": user_input})
    with open(CHAT_FILE, "w") as f:
        json.dump(data, f)
    st.experimental_rerun()

# --- CLEAR CHAT (Admin Only) ---
if admin_mode:
    if st.button("🗑️ Clear Chat"):
        data["messages"] = []
        with open(CHAT_FILE, "w") as f:
            json.dump(data, f)
        st.experimental_rerun()
