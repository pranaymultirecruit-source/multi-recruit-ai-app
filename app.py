import streamlit as st
from PIL import Image
import pandas as pd
import json
import os
from dotenv import load_dotenv
import streamlit.components.v1 as components
import base64


# ------------------------------
# Helpers
# ------------------------------
def get_bot_response(user_message: str, qa_records: list):
    """Find matching answer from CSV data."""
    if not user_message:
        return None
    q = user_message.strip().lower()
    for rec in qa_records:
        if rec.get("question", "").strip().lower() == q:
            return rec.get("answer", "")
    for rec in qa_records:
        if q in rec.get("question", "").strip().lower():
            return rec.get("answer", "")
    return "Sorry, I don’t have an answer for this."


# ------------------------------
# Setup & Background
# ------------------------------
load_dotenv()
base_path = os.path.dirname(os.path.abspath(__file__))

# ✅ Use your background image here
bg_path = r"C:\Users\hp\Downloads\MR logo BG for Local host.png"

st.set_page_config(page_title="MultiRecruit AI", page_icon="🤖", layout="wide")
# ------------------------------
# Page background setup (using base64 for full compatibility)
# ------------------------------
def set_background(image_path):
    """Encodes image as base64 and sets it as Streamlit background."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
        bg_ext = image_path.split('.')[-1]
        st.markdown(
            f"""
            <style>
            [data-testid="stAppViewContainer"] {{
                background-image: url("data:image/{bg_ext};base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            [data-testid="stHeader"], [data-testid="stToolbar"] {{
                background: rgba(255, 255, 255, 0.2);
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning(f"⚠️ Background image not found: {image_path}")

# ✅ Your background image path
bg_path = r"C:\Users\hp\Downloads\MR logo BG for Local host.png"
set_background(bg_path)

# ------------------------------
# Title & Sidebar
# ------------------------------
st.title("MultiRecruit AI Assistant")
st.write("Click the 🤖 bot (top-right) or one of the quick buttons to get instant help.")

st.sidebar.radio(
    "Select Category:",
    ["🖥️ IT Helpdesk", "👨‍💼 Employee FAQ", "💼 Client FAQ", "🧑‍🎓 Job Seeker FAQ", "📚 Library"]
)


# ------------------------------
# Load CSV
# ------------------------------
csv_path = os.path.join(base_path, "multi_recruit_ai_full_qa.csv")
qa_records = []
if os.path.exists(csv_path):
    try:
        df = pd.read_csv(csv_path, encoding="utf-8", keep_default_na=False, on_bad_lines="skip")
        if "question" in df.columns and "answer" in df.columns:
            qa_records = df[["question", "answer"]].astype(str).to_dict(orient="records")
        else:
            st.error("CSV must have 'question' and 'answer' columns.")
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
else:
    st.warning("CSV not found. Place 'multi_recruit_ai_full_qa.csv' in the app folder.")
    qa_records = [
        {"question": "Forgot Password", "answer": "Go to your password reset page and follow the instructions."},
        {"question": "Laptop Not Turning On", "answer": "Hold the power button for 10 seconds and check your charger."},
        {"question": "Outlook Issue", "answer": "Restart Outlook and check your internet connection."},
    ]

qa_json_str = json.dumps(qa_records)


# ------------------------------
# Bot Component (under subtitle)
# ------------------------------
html_template = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<style>
#bot-container {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-top: 25px;
}}
#bot-button {{
  width: 130px;
  height: 130px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #00bcd4, #01579b);
  box-shadow: 0 0 30px rgba(0,0,0,0.4);
  cursor: pointer;
  font-size: 70px;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}}
#bot-button:hover {{
  transform: scale(1.15);
  box-shadow: 0 0 40px rgba(0,0,0,0.6);
}}
#chat-box {{
  width: 400px;
  height: 340px;
  background: rgba(255,255,255,0.9);
  border-radius: 15px;
  box-shadow: 0 0 15px rgba(0,0,0,0.4);
  padding: 12px;
  margin-top: 20px;
  display: none;
  flex-direction: column;
  font-family: sans-serif;
}}
#chat-log {{
  flex: 1;
  overflow-y: auto;
  margin-bottom: 8px;
  font-size: 15px;
}}
.chat-message {{
  background: #e3f2fd;
  padding: 8px;
  margin: 6px 0;
  border-radius: 10px;
}}
.chat-message.bot {{
  background: #e8f5e9;
}}
#controls {{
  display: flex;
  gap: 4px;
}}
#chat-input {{
  flex: 1;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 15px;
}}
#chat-send {{
  padding: 10px;
  border-radius: 6px;
  background: #0288d1;
  color: #fff;
  border: none;
  cursor: pointer;
}}
</style>
</head>
<body>
<div id="bot-container">
  <div id="bot-button">🤖</div>
  <div id="chat-box">
    <div id="chat-log"></div>
    <div id="controls">
      <input id="chat-input" type="text" placeholder="Type your question..." />
      <button id="chat-send">Send</button>
    </div>
  </div>
</div>

<script>
const QA = {qa_json_str};
const botBtn = document.getElementById('bot-button');
const chatBox = document.getElementById('chat-box');
const chatLog = document.getElementById('chat-log');
const chatInput = document.getElementById('chat-input');
const chatSend = document.getElementById('chat-send');

function findAnswer(query) {{
  if (!QA || QA.length === 0) return null;
  query = query.trim().toLowerCase();
  for (let i = 0; i < QA.length; i++) {{
    if (QA[i].question.trim().toLowerCase() === query) {{
      return QA[i].answer;
    }}
  }}
  for (let i = 0; i < QA.length; i++) {{
    if (QA[i].question.trim().toLowerCase().includes(query)) {{
      return QA[i].answer;
    }}
  }}
  return null;
}}

botBtn.addEventListener('click', () => {{
  if (chatBox.style.display === 'none' || chatBox.style.display === '') {{
    chatBox.style.display = 'flex';
    chatLog.innerHTML = '<div class="chat-message bot"><b>Bot:</b> Hi, how can I help you?</div>';
  }} else {{
    chatBox.style.display = 'none';
  }}
}});

function handleSend() {{
  const text = chatInput.value.trim();
  if (!text) return;
  chatLog.innerHTML += '<div class="chat-message"><b>You:</b> ' + text + '</div>';
  chatInput.value = '';
  const answer = findAnswer(text);
  const reply = answer ? answer : "Sorry, I don’t have an answer for this.";
  chatLog.innerHTML += '<div class="chat-message bot"><b>Bot:</b> ' + reply + '</div>';
  chatLog.scrollTop = chatLog.scrollHeight;
  window.parent.postMessage(
    {{ "isStreamlitMessage": true, "type": "streamlit:setComponentValue", "value": text }},
    "*"
  );
}}

chatSend.addEventListener('click', handleSend);
chatInput.addEventListener('keydown', e => {{ if (e.key === 'Enter') handleSend(); }});
</script>
</body>
</html>
"""

# Render inside Streamlit
user_input = components.html(html_template, height=650)
# ------------------------------
# Display Python-side response (only if a valid string was returned)
# ------------------------------
if isinstance(user_input, str) and user_input.strip():
    msg = user_input.strip()
    reply = get_bot_response(msg, qa_records)
    if reply and "Sorry" not in reply:
        st.markdown(f"**🤖 Bot:** {reply}")
