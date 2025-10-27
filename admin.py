import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Tech Support Dashboard", page_icon="🧑‍💻", layout="wide")

chat_file = "support_chat.json"

st.title("💬 Tech Support Dashboard")
st.write("View user messages and reply to them instantly from here.")

# Ensure chat file exists
if not os.path.exists(chat_file):
    with open(chat_file, "w", encoding="utf-8") as f:
        json.dump([], f)

# Load chat
with open(chat_file, "r", encoding="utf-8") as f:
    try:
        chat_data = json.load(f)
    except json.JSONDecodeError:
        chat_data = []

# Display chat
st.subheader("📨 Chat Messages")
if not chat_data:
    st.info("No messages yet. Wait for users to contact tech support.")
else:
    for msg in chat_data[-10:]:
        if msg["sender"] == "user":
            st.markdown(f"🧑‍💼 **User:** {msg['text']}  \n🕒 {msg['timestamp']}")
        elif msg["sender"] == "admin":
            st.markdown(f"🤖 **You:** {msg['text']}  \n🕒 {msg['timestamp']}")
        st.markdown("---")

# Input box to reply
reply_text = st.text_input("✏️ Type your reply here:")
if st.button("Send Reply"):
    if reply_text.strip():
        new_msg = {
            "sender": "admin",
            "text": reply_text.strip(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        chat_data.append(new_msg)
        with open(chat_file, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, indent=2)
        st.success("✅ Reply sent!")
        st.rerun()
    else:
        st.warning("Please type a message before sending.")

st.markdown("---")
st.caption("This dashboard automatically updates when reloaded. (You can press **R** to refresh.)")
