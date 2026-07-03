import streamlit as st
import sqlite3
import base64
import uuid
import datetime
import requests
from io import BytesIO
from google import genai
from google.genai import types
from streamlit_lottie import st_lottie

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="Advanced Gemini Workspace",
    page_icon="🧠",
    layout="wide"
)

# --------------------------------------------------
# Custom CSS Styling
# --------------------------------------------------
st.markdown("""
<style>
.main {
    background-color: #F7F9FC;
}
h1 {
    text-align:center;
}
.user-msg{
    background:#DCF8C6;
    padding:12px;
    border-radius:10px;
    margin:8px 0;
}
.bot-msg{
    background:#EEEEEE;
    padding:12px;
    border-radius:10px;
    margin:8px 0;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Lottie Asset Loader Helper
# --------------------------------------------------
@st.cache_data
def load_lottie_url(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# Validated active community hosting links for our AI Companion
ANIMATIONS = {
    "idle": "https://lottie.host/6cc5c636-161e-4fe2-a29e-d0a010fb857d/oUxnN8jMLv.json",       
    "thinking": "https://lottie.host/6db67e84-29ca-4df7-9aed-e918be35c04f/GUHZd8ZAiP.json",   
    "success": "https://lottie.host/0d17b47d-7e01-4b7d-a8fb-f94b6c69dd48/jycOqQmo4J.json"     
}

# --------------------------------------------------
# Custom Database Persistence Engine (SQLite)
# --------------------------------------------------
def init_db():
    conn = sqlite3.connect("chat_workspace.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions 
                 (session_id TEXT PRIMARY KEY, title TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages 
                 (session_id TEXT, role TEXT, content TEXT, image_b64 TEXT, mime_type TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def get_all_sessions():
    conn = sqlite3.connect("chat_workspace.db")
    c = conn.cursor()
    c.execute("SELECT session_id, title FROM sessions ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def create_session(title="New Conversation"):
    sid = str(uuid.uuid4())
    conn = sqlite3.connect("chat_workspace.db")
    c = conn.cursor()
    c.execute("INSERT INTO sessions (session_id, title, created_at) VALUES (?, ?, ?)", 
              (sid, title, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return sid

def load_messages(sid):
    conn = sqlite3.connect("chat_workspace.db")
    c = conn.cursor()
    c.execute("SELECT role, content, image_b64, mime_type FROM messages WHERE session_id = ? ORDER BY timestamp ASC", (sid,))
    rows = c.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1], "image_b64": r[2], "mime_type": r[3]} for r in rows]

def save_message(sid, role, content, image_b64=None, mime_type=None):
    conn = sqlite3.connect("chat_workspace.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, role, content, image_b64, mime_type, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
              (sid, role, content, image_b64, mime_type, datetime.datetime.now().isoformat()))
    
    c.execute("SELECT COUNT(*) FROM messages WHERE session_id = ?", (sid,))
    if c.fetchone()[0] == 1 and role == "user":
        title = content[:25] + "..." if len(content) > 25 else content
        c.execute("UPDATE sessions SET title = ? WHERE session_id = ?", (title, sid))
    conn.commit()
    conn.close()

def delete_session(sid):
    conn = sqlite3.connect("chat_workspace.db")
    c = conn.cursor()
    c.execute("DELETE FROM sessions WHERE session_id = ?", (sid,))
    c.execute("DELETE FROM messages WHERE session_id = ?", (sid,))
    conn.commit()
    conn.close()

init_db()

# --------------------------------------------------
# Initialize Live Gemini Client
# --------------------------------------------------
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Missing Gemini API Key! Please set up your key inside `.streamlit/secrets.toml`.")
    st.stop()

# --------------------------------------------------
# Session State Synchronization Block
# --------------------------------------------------
if "current_session_id" not in st.session_state:
    sessions = get_all_sessions()
    if not sessions:
        st.session_state.current_session_id = create_session("Initial Workspace")
    else:
        st.session_state.current_session_id = sessions[0][0]
st.session_state.messages = load_messages(st.session_state.current_session_id)

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "pet_state" not in st.session_state:
    st.session_state.pet_state = "idle"

if "token_count" not in st.session_state:
    st.session_state.token_count = 0

# --------------------------------------------------
# Sidebar Control Panel
# --------------------------------------------------
with st.sidebar:
    st.title("🧠 Workspace Panel")
    st.markdown("---")
    
    st.subheader("📂 Chat History")
    all_sessions = get_all_sessions()
    session_dict = {title: sid for sid, title in all_sessions}
    
    try:
        current_idx = [sid for sid, _ in all_sessions].index(st.session_state.current_session_id)
    except ValueError:
        current_idx = 0
        
    selected_title = st.selectbox("Select Active Session", list(session_dict.keys()), index=current_idx)
    
    if session_dict and session_dict[selected_title] != st.session_state.current_session_id:
        st.session_state.current_session_id = session_dict[selected_title]
        st.session_state.messages = load_messages(st.session_state.current_session_id)
        st.session_state.pet_state = "idle"
        st.session_state.token_count = 0  
        st.rerun()
        
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 New Chat", use_container_width=True):
            st.session_state.current_session_id = create_session()
            st.session_state.messages = []
            st.session_state.pet_state = "idle"
            st.session_state.token_count = 0
            st.rerun()
    with col2:
        if st.button("🗑️ Delete Chat", use_container_width=True):
            delete_session(st.session_state.current_session_id)
            del st.session_state.current_session_id
            st.session_state.pet_state = "idle"
            st.session_state.token_count = 0
            st.rerun()

    st.markdown("---")
    
    st.subheader("🎭 Bot Persona")
    personas = {
        "General Assistant": "You are a helpful, clever, and grounded AI assistant.",
        "Code Wizard": "You are an expert software developer. Provide production-grade, optimized code and clear logic reviews.",
        "Data Analyst": "You are a senior data scientist. Focus heavily on clean structured breakdowns, analytics insights, and mathematical clarity.",
        "Creative Writer": "You are an expressive copywriter. Use descriptive prose, analogies, and highly engaging phrasing."
    }
    selected_persona = st.selectbox("Active Persona", list(personas.keys()))
    system_instruction = personas[selected_persona]

    st.subheader("⚙️ Settings")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    
    model_mapping = {
        "Gemini 2.5 Flash": "gemini-2.5-flash",
        "Gemini 2.5 Pro": "gemini-2.5-pro"
    }
    selected_model_display = st.selectbox("Model Engine", list(model_mapping.keys()))
    chosen_model = model_mapping[selected_model_display]

    st.markdown("---")
    
    # 🖼️ / 📄 Multimodal Upload Section (FIXED: Added PDF support)
    st.subheader("📎 Attachments")
    uploaded_file = st.file_uploader(
        "Upload image or PDF document", 
        type=["png", "jpg", "jpeg", "pdf"], 
        key=f"uploader_{st.session_state.uploader_key}"
    )
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            st.caption(f"📄 **{uploaded_file.name}** queued for next prompt.")
        else:
            st.image(uploaded_file, caption="Image queued for next prompt", width=150)

    st.markdown("---")
    
    st.subheader("📊 Session Telemetry")
    st.metric(label="Context Tokens Consumed", value=f"{st.session_state.token_count:,}")

    st.markdown("---")
    chat_md = f"# Chat Session: {selected_title}\n\n"
    for msg in st.session_state.messages:
        label = "User" if msg["role"] == "user" else "Gemini"
        chat_md += f"### **{label}**:\n{msg['content']}\n\n"
    
    st.download_button(
        label="📥 Export Chat Log (.md)",
        data=chat_md,
        file_name=f"chat_history_{st.session_state.current_session_id[:8]}.md",
        mime="text/markdown",
        use_container_width=True
    )

# --------------------------------------------------
# Main UI Presentation Arena
# --------------------------------------------------
st.title("🧠 Advanced Multi-Session GenAI Workspace")
st.caption(f"Active Hub: {selected_title} | Engine: {selected_model_display} ({selected_persona})")
st.markdown("---")

# Render active conversation timeline
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            if message.get("image_b64"):
                # Checked file type rendering branch rules
                if message.get("mime_type") == "application/pdf":
                    st.caption("📄 **Attached Document:** (PDF File Data Stream Injected)")
                else:
                    st.image(BytesIO(base64.b64decode(message["image_b64"])), width=350)
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])

# --------------------------------------------------
# Dedicated Companion Pet Integration Zone (Above Input Box)
# --------------------------------------------------
pet_placeholder = st.empty()

lottie_json = load_lottie_url(ANIMATIONS[st.session_state.pet_state])
with pet_placeholder.container():
    if lottie_json:
        st_lottie(lottie_json, height=120, key="workspace_pet_anim")
    else:
        emoji_map = {"idle": "🤖 💤", "thinking": "🤖 ⚡ *Thinking...*", "success": "🤖 🎉 *Success!*"}
        st.markdown(f"<div style='text-align: center; font-size: 1.2rem; font-weight: bold;'>{emoji_map[st.session_state.pet_state]}</div>", unsafe_allow_html=True)

# --------------------------------------------------
# Operational Inference Logic Block (Streaming + Search Grounding + Pet Swapping)
# --------------------------------------------------
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    
    api_contents = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        parts = []
        if msg.get("image_b64"):
            img_bytes = base64.b64decode(msg["image_b64"])
            parts.append(types.Part.from_bytes(data=img_bytes, mime_type=msg["mime_type"]))
        parts.append(types.Part.from_text(text=msg["content"]))
        api_contents.append(types.Content(role=role, parts=parts))

    with st.chat_message("assistant"):
        def chunk_generator():
            try:
                current_date_ctx = f"\n\nCurrent real-world date time context: {datetime.datetime.now().strftime('%B %d, %Y - %H:%M Local Time')}."
                
                response_stream = client.models.generate_content_stream(
                    model=chosen_model,
                    contents=api_contents,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        system_instruction=system_instruction + current_date_ctx,
                        tools=[types.Tool(google_search=types.GoogleSearch())]
                    )
                )
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
            except Exception as e:
                yield f"\n\n⚠️ **API Engine Exception Encountered:** {e}"

        st.session_state.pet_state = "thinking"
        thinking_lottie = load_lottie_url(ANIMATIONS["thinking"])
        with pet_placeholder.container():
            if thinking_lottie:
                st_lottie(thinking_lottie, height=120, key="workspace_pet_thinking")
            else:
                st.markdown("<div style='text-align: center; color: #F5A623;'>🤖 ⚡ Processing Data Pool...</div>", unsafe_allow_html=True)

        ai_response = st.write_stream(chunk_generator())
        
    save_message(st.session_state.current_session_id, "assistant", ai_response)
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # Calculate token count updates
    try:
        updated_api_contents = []
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            parts = []
            if msg.get("image_b64"):
                parts.append(types.Part.from_bytes(data=base64.b64decode(msg["image_b64"]), mime_type=msg["mime_type"]))
            parts.append(types.Part.from_text(text=msg["content"]))
            updated_api_contents.append(types.Content(role=role, parts=parts))
            
        token_resp = client.models.count_tokens(model=chosen_model, contents=updated_api_contents)
        st.session_state.token_count = token_resp.total_tokens
    except Exception:
        pass

    st.session_state.pet_state = "success"
    st.rerun()

# Accept new prompt interface commands
prompt = st.chat_input("Input workspace instruction...")

if prompt:
    img_b64 = None
    m_type = None
    
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        img_b64 = base64.b64encode(file_bytes).decode()
        m_type = uploaded_file.type
        st.session_state.uploader_key += 1 
        
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "image_b64": img_b64,
        "mime_type": m_type
    })
    save_message(st.session_state.current_session_id, "user", prompt, img_b64, m_type)
    
    st.session_state.pet_state = "idle"
    st.rerun()