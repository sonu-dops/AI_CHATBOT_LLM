import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# --------------------------------------------------
# UI Configuration
# --------------------------------------------------
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")

# Maps for personality and model
model_map = {"Gemini 2.5 Flash": "gemini-2.5-flash", "Gemini 2.5 Pro": "gemini-2.5-pro"}
persona_map = {
    "Helpful Assistant": "You are a helpful, polite, and friendly assistant.",
    "Professional Expert": "You are a professional, formal, and authoritative expert who provides precise and detailed information.",
    "Funny/Witty Companion": "You are a witty, humorous, and laid-back companion who loves to joke around while answering.",
    "Concise Teacher": "You are a direct, clear, and concise teacher who explains complex topics simply and briefly."
}

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.title("🤖 AI Chatbot Settings")
    if st.button("🆕 New Chat", key="new_chat"): st.session_state.messages = []
    
    model_choice = st.selectbox("Model", list(model_map.keys()), key="model_select")
    personality = st.selectbox("Choose Personality", list(persona_map.keys()), key="personality_select")
    
    st.markdown("---")
    st.info("The AI will adapt its tone based on your personality choice.")

# --------------------------------------------------
# Main Logic
# --------------------------------------------------
st.title("🤖 AI Chatbot Using LLM")
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize LLM
selected_model = model_map[model_choice]
llm = ChatGoogleGenerativeAI(model=selected_model, google_api_key=api_key)

# Display Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat Input
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Construct History + System Prompt
                system_instruction = persona_map[personality]
                history = [SystemMessage(content=system_instruction)] + [
                    HumanMessage(content=m["content"]) if m["role"] == "user" 
                    else AIMessage(content=m["content"]) 
                    for m in st.session_state.messages[:-1]
                ]
                
                # Get response
                response = llm.invoke(history + [HumanMessage(content=prompt)])
                ai_reply = response.content
                
                st.write(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            except Exception as e:
                st.error(f"Error: {e}")