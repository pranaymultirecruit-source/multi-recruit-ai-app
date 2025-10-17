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
load_dotenv()
base_path = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(base_path, "logo.png")

st.set_page_config(page_title="Multi Recruit AI", page_icon="🤖", layout="wide")
st.title("Multi Recruit AI Assistant")
st.write("Click the 🤖 bot (top-right) and ask your question — it will answer from the Q&A CSV instantly.")

# Show logo if exists
if os.path.exists(logo_path):
    try:
        img = Image.open(logo_path)
        st.image(img, width=160)
    except Exception:
        pass

# ------------------------------
# Hide Streamlit success/notification messages (including the green 'Loaded' message)
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
# Sidebar (kept)
# ------------------------------
menu = st.sidebar.radio(
    "Select Category:",
    ["🖥️ IT Helpdesk", "👨‍💼 Employee FAQ", "💼 Client FAQ", "🧑‍🎓 Job Seeker FAQ", "📚 Library"]
)

# ------------------------------
# Load CSV (Q&A)
# ------------------------------
csv_path = os.path.join(base_path, "multi_recruit_ai_full_qa.csv")
qa_records = []
if os.path.exists(csv_path):
    try:
        df = pd.read_csv(csv_path, encoding="utf-8", keep_default_na=False, on_bad_lines="skip")
        if "question" in df.columns and "answer" in df.columns:
            qa_records = df[["question", "answer"]].astype(str).to_dict(orient="records")
            # We DO NOT show this success message (we hid success messages above)
        else:
            st.error("CSV must contain columns named 'question' and 'answer'. Floating bot will show a warning.")
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
else:
    st.warning("CSV not found. Place 'multi_recruit_ai_full_qa.csv' in the app folder. Floating bot will be empty until then.")

# JSON for embedding safely
qa_json = json.dumps(qa_records).replace("</", "<\\/")

# ------------------------------
# HTML/JS template (bot beside logo; no Python f-strings inside JS)
# ------------------------------
# ------------------------------
# HTML/JS template (big bot beside logo, new greeting)
# ------------------------------

html_template = """
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<style>
/* --- Bot beside logo, bigger size --- */
#bot-button {
  position: fixed;
  top: 25px;          /* aligns with logo */
  right: 100px;       /* adjust if needed */
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
#bot-button:hover {
  transform: scale(1.1);
}

/* --- Chat box --- */
#chat-box {
  display: none;
  position: fixed;
  top: 120px;
  right: 100px;
  width: 360px;
  background: #ffffff;
  border-radius: 14px;
  padding: 14px;
  box-shadow: 2px 2px 25px rgba(0,0,0,0.2);
  z-index: 99999;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;
}
#chat-box h4 {
  margin: 0 0 8px 0;
  text-align: center;
  color:#01579b;
  font-size: 18px;
  font-weight: 600;
}
#chat-log {
  max-height: 320px;
  overflow-y: auto;
  margin-bottom: 8px;
  font-size: 14px;
}
.chat-message {
  background: #e3f2fd;
  padding: 8px;
  margin: 6px 0;
  border-radius: 10px;
}
.chat-message.bot {
  background: #e8f5e9;
}
#chat-input {
  width: calc(100% - 12px);
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #ccc;
}
#chat-send {
  margin-top: 8px;
  width: 100%;
  padding: 8px;
  border-radius: 6px;
  background: #0288d1;
  color: #fff;
  border: none;
  cursor: pointer;
}
.suggestion {
  font-size:12px;
  color:#555;
  margin-top:4px;
}
</style>
</head>
<body>
<div id="bot-button">🤖</div>

<div id="chat-box" aria-label="Multi Recruit Bot">
  <h4>Multi Recruit Bot</h4>
  <div id="chat-log"><div class="chat-message bot"><b>Bot:</b> Hi, how can I help you?</div></div>
  <input id="chat-input" type="text" placeholder="Type your question..." />
  <button id="chat-send">Send</button>
</div>

<script>
const QA = <<QA_JSON>>;

// ---- Matching functions ----
function levenshtein(a, b) {
  if (!a) return b ? b.length : 0;
  if (!b) return a.length;
  a = a.toLowerCase();
  b = b.toLowerCase();
  const m = a.length, n = b.length;
  const dp = Array(m+1).fill(null).map(() => Array(n+1).fill(0));
  for (let i=0;i<=m;i++) dp[i][0]=i;
  for (let j=0;j<=n;j++) dp[0][j]=j;
  for (let i=1;i<=m;i++) {
    for (let j=1;j<=n;j++) {
      const cost = a[i-1] === b[j-1] ? 0 : 1;
      dp[i][j] = Math.min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost);
    }
  }
  return dp[m][n];
}

function similarity(a,b){
  if(!a||!b)return 0;
  const aa=a.trim().toLowerCase();
  const bb=b.trim().toLowerCase();
  const maxlen=Math.max(aa.length,bb.length);
  if(maxlen===0)return 1;
  return 1-(levenshtein(aa,bb)/maxlen);
}

function findBest(query,topN=3){
  if(!QA||QA.length===0)return[];
  const scores=QA.map(i=>({q:i.question,a:i.answer,s:similarity(query,i.question)}));
  scores.sort((x,y)=>y.s-x.s);
  return scores.slice(0,topN);
}

const botBtn=document.getElementById('bot-button');
const chatBox=document.getElementById('chat-box');
const chatLog=document.getElementById('chat-log');
const chatInput=document.getElementById('chat-input');
const chatSend=document.getElementById('chat-send');

botBtn.addEventListener('click',()=>{
  chatBox.style.display=(chatBox.style.display==='none'||chatBox.style.display==='')?'block':'none';
  chatInput.focus();
});

function escapeHtml(str){if(!str)return'';return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,"&#039;");}

chatSend.addEventListener('click',handleSend);
chatInput.addEventListener('keydown',e=>{if(e.key==='Enter')handleSend();});

function handleSend(){
 const text=chatInput.value.trim();
 if(!text)return;
 chatLog.innerHTML+='<div class="chat-message"><b>You:</b> '+escapeHtml(text)+'</div>';
 chatInput.value='';
 const matches=findBest(text,3);
 const best=matches.length?matches[0]:null;
 const threshold=0.45;
 if(best&&best.s>=threshold){
   chatLog.innerHTML+='<div class="chat-message bot"><b>Bot:</b> '+escapeHtml(best.a)+'</div>';
   if(matches.length>1){
     const others=matches.slice(1).filter(m=>m.s>0.2).map(m=>m.q);
     if(others.length){chatLog.innerHTML+='<div class="suggestion">Other close matches: '+escapeHtml(others.join(' • '))+'</div>';}
   }
 }else{
   chatLog.innerHTML+='<div class="chat-message bot"><b>Bot:</b> I couldn\\'t find a close match in the Q&A file. Try rephrasing or add it to the CSV.</div>';
 }
 chatLog.scrollTop=chatLog.scrollHeight;
}
</script>
</body>
</html>
"""

components_html = html_template.replace("<<QA_JSON>>", qa_json)
components.html(components_html, height=720)

# Replace placeholder with json
components_html = html_template.replace("<<QA_JSON>>", qa_json)

# Render the component
components.html(components_html, height=720)
