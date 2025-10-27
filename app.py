import streamlit as st
from PIL import Image
import pandas as pd
import json
import os
from dotenv import load_dotenv
import streamlit.components.v1 as components
import base64
from pathlib import Path

# ------------------------------
# Setup
# ------------------------------
load_dotenv()
base_path = os.path.dirname(os.path.abspath(__file__))
chat_file = os.path.join(base_path, "support_chat.json")

# Ensure chat file exists
if not os.path.exists(chat_file):
    with open(chat_file, "w", encoding="utf-8") as f:
        json.dump({"messages": []}, f, indent=2)

# ------------------------------
# Helper: Bot response logic
# ------------------------------
def get_bot_response(user_message: str, qa_records: list):
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
# Page Config and Background
# ------------------------------
st.set_page_config(page_title="MultiRecruit AI", page_icon="🤖", layout="wide")

local_bg_path = Path(base_path) / "MR logo BG for Local host (1).png"
github_bg_url = "https://raw.githubusercontent.com/pranaymultirecruit-source/multi-recruit-ai-app/main/MR%20logo%20BG%20for%20Local%20host%20(1).png"

def set_background():
    if local_bg_path.exists():
        # Local background (localhost)
        with open(local_bg_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
        bg_ext = local_bg_path.suffix.replace(".", "")
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
        # Fallback for Streamlit Cloud (load from GitHub)
        st.markdown(
            f"""
            <style>
            [data-testid="stAppViewContainer"] {{
                background-image: url("{github_bg_url}");
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

set_background()

# ------------------------------
# Title and Sidebar
# ------------------------------
st.title("MultiRecruit AI Assistant")
st.write("Click the 🤖 bot (top-right) or one of the quick buttons to get instant help.")

st.sidebar.radio(
    "Select Category:",
    ["🖥️ IT Helpdesk", "👨‍💼 Employee FAQ", "💼 Client FAQ", "🧑‍🎓 Job Seeker FAQ", "📚 Library"]
)

# ------------------------------
# Load CSV Q&A
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
    qa_records = [
        {"question": "Forgot Password", "answer": "Go to your password reset page."},
        {"question": "Laptop Not Turning On", "answer": "Hold the power button for 10 seconds."},
        {"question": "Outlook Issue", "answer": "Restart Outlook and check your internet connection."},
    ]

qa_json_str = json.dumps(qa_records)

# ------------------------------
# Bot + Tech Support (HTML + JS)
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
#chat-box, #support-box {{
  width: 400px;
  height: 340px;
  background: rgba(255,255,255,0.95);
  border-radius: 15px;
  box-shadow: 0 0 15px rgba(0,0,0,0.4);
  padding: 12px;
  margin-top: 20px;
  display: none;
  flex-direction: column;
  font-family: sans-serif;
}}
#chat-log, #support-log {{
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
#controls, #support-controls {{
  display: flex;
  gap: 4px;
}}
input[type=text] {{
  flex: 1;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 15px;
}}
button {{
  padding: 10px;
  border-radius: 6px;
  background: #0288d1;
  color: #fff;
  border: none;
  cursor: pointer;
}}
#tech-btn {{
  background: #43a047;
  margin-top: 5px;
  display: none;
}}
#back-btn {{
  background: #f57c00;
  margin-top: 5px;
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
    <button id="tech-btn">💬 Contact Live Tech Support</button>
  </div>

  <div id="support-box">
    <div id="support-log">
      <div class="chat-message bot"><b>Pranay:</b> Hi, this is Pranay. How can I help you today?</div>
    </div>
    <div id="support-controls">
      <input id="support-input" type="text" placeholder="Type your message..." />
      <button id="support-send">Send</button>
    </div>
    <button id="back-btn">🔙 Back to Bot Chat</button>
  </div>
</div>

<script>
const QA = {qa_json_str};
const botBtn = document.getElementById('bot-button');
const chatBox = document.getElementById('chat-box');
const supportBox = document.getElementById('support-box');
const chatLog = document.getElementById('chat-log');
const chatInput = document.getElementById('chat-input');
const chatSend = document.getElementById('chat-send');
const techBtn = document.getElementById('tech-btn');
const supportLog = document.getElementById('support-log');
const supportInput = document.getElementById('support-input');
const supportSend = document.getElementById('support-send');
const backBtn = document.getElementById('back-btn');

function findAnswer(query) {{
  query = query.trim().toLowerCase();
  for (let i = 0; i < QA.length; i++) {{
    if (QA[i].question.trim().toLowerCase() === query) return QA[i].answer;
  }}
  for (let i = 0; i < QA.length; i++) {{
    if (QA[i].question.trim().toLowerCase().includes(query)) return QA[i].answer;
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
  if (reply.includes("Sorry")) {{
    techBtn.style.display = 'block';
  }}
}}

chatSend.addEventListener('click', handleSend);
chatInput.addEventListener('keydown', e => {{ if (e.key === 'Enter') handleSend(); }});

techBtn.addEventListener('click', () => {{
  chatBox.style.display = 'none';
  supportBox.style.display = 'flex';
}});

backBtn.addEventListener('click', () => {{
  supportBox.style.display = 'none';
  chatBox.style.display = 'flex';
}});

function handleSupportSend() {{
  const text = supportInput.value.trim();
  if (!text) return;
  supportLog.innerHTML += '<div class="chat-message"><b>You:</b> ' + text + '</div>';
  supportInput.value = '';
  supportLog.scrollTop = supportLog.scrollHeight;
  window.parent.postMessage({{
    "isStreamlitMessage": true,
    "type": "streamlit:setComponentValue",
    "value": "support:" + text
  }}, "*");
}}

supportSend.addEventListener('click', handleSupportSend);
supportInput.addEventListener('keydown', e => {{ if (e.key === 'Enter') handleSupportSend(); }});
</script>
</body>
</html>
"""

# ------------------------------
# Render Chat Interface
# ------------------------------
user_input = components.html(html_template, height=700)

# ------------------------------
# Save Tech Support Messages
# ------------------------------
if isinstance(user_input, str) and user_input.startswith("support:"):
    message = user_input.replace("support:", "").strip()
    if message:
        try:
            with open(chat_file, "r+", encoding="utf-8") as f:
                data = json.load(f)
                data["messages"].append({"sender": "user", "text": message})
                f.seek(0)
                json.dump(data, f, indent=2)
            st.success("📨 Message sent to Tech Support!")
        except Exception as e:
            st.error(f"⚠️ Could not save support message: {e}")
