import streamlit as st
from PIL import Image
import os
import pandas as pd
import json
from dotenv import load_dotenv
import streamlit.components.v1 as components

# ------------------------------
# Setup
# ------------------------------
import streamlit as st
from PIL import Image
import os
import pandas as pd
import json
from dotenv import load_dotenv
import streamlit.components.v1 as components

# ------------------------------
# Hide Streamlit menu, footer, GitHub, and decorations
# ------------------------------
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stFooter"] {visibility: hidden; height: 0px;}
    [data-testid="stDecoration"] {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ------------------------------
# Setup
# ------------------------------
load_dotenv()
base_path = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(base_path, "logo.png")

st.set_page_config(page_title="Multi Recruit AI", page_icon="🤖", layout="wide")
st.title("Multi Recruit AI Assistant")
st.write("Click the 🤖 bot (top-right) and ask your question.")

# Show logo if exists
if os.path.exists(logo_path):
    try:
        img = Image.open(logo_path)
        st.image(img, width=160)
    except Exception:
        pass

# ------------------------------
# Hide Streamlit notifications
# ------------------------------
hide_msg_style = """
<style>
div[data-testid="stNotification"], .stAlert, .stInfo, .stSuccess {
    display: none !important;
}
</style>
"""
st.markdown(hide_msg_style, unsafe_allow_html=True)

# ------------------------------
# Sidebar
# ------------------------------
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
    st.warning("CSV not found. Place 'multi_recruit_ai_full_qa.csv' in the app folder.")

qa_json = json.dumps(qa_records).replace("</", "<\\/")

# ------------------------------
# Floating bot HTML/JS
# ------------------------------
html_template = """
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<style>
#bot-button {
  position: fixed;
  top: 25px;
  right: 100px;
  width: 85px;
  height: 85px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #00bcd4, #01579b);
  box-shadow: 3px 3px 14px rgba(0,0,0,0.4);
  cursor: pointer;
  z-index: 99999;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 44px;
  transition: transform 0.3s ease;
}
#bot-button:hover { transform: scale(1.1); }
#chat-box {
  position: fixed;
  top: 120px;
  right: 40px;
  width: 450px;
  height: 320px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 0 12px rgba(0,0,0,0.3);
  padding: 12px;
  display: none;
  flex-direction: column;
  z-index: 100000;
}
#chat-box h4 {
  margin: 0 0 8px 0;
  text-align: center;
  color:#01579b;
  font-size: 18px;
  font-weight: 600;
}
#chat-log { 
  flex:1; 
  overflow-y:auto; 
  margin-bottom:8px; 
  font-size:14px;
  scroll-behavior: smooth;
}
.chat-message { background:#e3f2fd; padding:8px; margin:6px 0; border-radius:10px; }
.chat-message.bot { background:#e8f5e9; }
#controls { display:flex; gap:4px; }
#chat-input { 
  flex:1; 
  padding:10px; 
  border-radius:6px; 
  border:1px solid #ccc; 
  font-size:16px; 
}
#chat-send, #voice-toggle { 
  padding:10px; 
  border-radius:6px; 
  background:#0288d1; 
  color:#fff; 
  border:none; 
  cursor:pointer; 
  font-size:16px; 
}
@media (max-width: 600px) {
  #chat-box {
    width: 90%;
    height: 70%;
    right: 5%;
    top: 100px;
  }
  #bot-button {
    right: 20px;
    top: 20px;
    width: 70px;
    height: 70px;
    font-size: 36px;
  }
}
</style>
</head>
<body>
<div id="bot-button">🤖</div>
<div id="chat-box">
  <h4>Multi Recruit Bot</h4>
  <div id="chat-log">
    <div class="chat-message bot"><b>Bot:</b> Hi, how can I help you?</div>
  </div>
  <div id="controls">
    <input id="chat-input" type="text" placeholder="Type your question..." />
    <button id="chat-send">Send</button>
    <button id="voice-toggle">Voice Off 🔇</button>
  </div>
</div>

<script>
const QA = <<QA_JSON>>;
console.log("Loaded QA:", QA);

function findAnswer(query) {
  if (!QA || QA.length === 0) return null;
  query = query.trim().toLowerCase();
  // Exact match first
  for (let i = 0; i < QA.length; i++) {
    if (QA[i].question.trim().toLowerCase() === query) {
      return QA[i].answer;
    }
  }
  // Then partial match
  for (let i = 0; i < QA.length; i++) {
    if (QA[i].question.trim().toLowerCase().includes(query)) {
      return QA[i].answer;
    }
  }
  return null;
}

const botBtn = document.getElementById('bot-button');
const chatBox = document.getElementById('chat-box');
const chatLog = document.getElementById('chat-log');
const chatInput = document.getElementById('chat-input');
const chatSend = document.getElementById('chat-send');
let voiceEnabled = false;  

const voiceToggle = document.getElementById('voice-toggle');
voiceToggle.addEventListener('click', () => {
  voiceEnabled = !voiceEnabled;
  voiceToggle.textContent = voiceEnabled ? 'Voice On 🔊' : 'Voice Off 🔇';
});

botBtn.addEventListener('click', () => {
  chatBox.style.display = (chatBox.style.display === 'none' || chatBox.style.display === '') ? 'flex' : 'none';
});

chatSend.addEventListener('click', handleSend);
chatInput.addEventListener('keydown', e => { if (e.key === 'Enter') handleSend(); });

function speak(text) {
  if (!voiceEnabled) return;
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'en-US';
  window.speechSynthesis.speak(utter);
}

function handleSend() {
  const text = chatInput.value.trim();
  if (!text) return;

  chatLog.innerHTML += '<div class="chat-message"><b>You:</b> ' + text + '</div>';
  chatInput.value = '';

  const answer = findAnswer(text);
  const reply = answer ? answer : "Sorry, I don’t have an answer for this.";

  chatLog.innerHTML += '<div class="chat-message bot"><b>Bot:</b> ' + reply + '</div>';
  chatLog.scrollTop = chatLog.scrollHeight;
  speak(reply);
}
</script>
</body>
</html>
"""

components.html(html_template.replace("<<QA_JSON>>", qa_json), height=720)

