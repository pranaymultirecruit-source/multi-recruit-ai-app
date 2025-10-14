import streamlit as st
from PIL import Image  # for handling images

# Load your logo
logo = Image.open("logo.png")

# Display the logo in your app
st.image(logo, width=200) 

import streamlit as st
import openai
from dotenv import load_dotenv
import os

# Load OpenAI API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Page setup
st.set_page_config(page_title="Multi Recruit AI", page_icon="🤖")
st.title(" Multi Recruit AI Assistant")
st.write("Welcome! I can help with IT support, FAQs, and questions from employees, job seekers, or clients.")

# Sidebar navigation
menu = st.sidebar.radio(
    "Select Category:",
    ["🖥️ IT Helpdesk", "👨‍💼 Employee FAQ", "💼 Client FAQ", "🧑‍🎓 Job Seeker FAQ"]
)

# Function to get AI response using new OpenAI API
def get_ai_response(prompt):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are Multi Recruit AI, a helpful support assistant for a recruiting company."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Main app logic
st.subheader(f"You selected: {menu}")
query = st.text_area("Ask your question below:")

if st.button("Get Answer"):
    if query:
        answer = get_ai_response(f"{menu} question: {query}")
        st.success(answer)
    else:
        st.warning("Please enter a question first.")
