import os
import tempfile
import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# 1. Page Config & Custom Gemini UI Style
# ==========================================
st.set_page_config(
    page_title="Gemini AI Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark / Modern Gemini UI Custom CSS
st.markdown("""
<style>
    /* Dark background like Gemini */
    .stApp {
        background-color: #131314;
        color: #e3e3e3;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1e1f20;
        border-right: 1px solid #2e2f31;
    }

    /* New Chat Button Styling */
    div.stButton > button[kind="primary"] {
        border-radius: 20px;
        background-color: #1a73e8;
        color: white;
        border: none;
        font-weight: 600;
    }

    /* Mode Badge Indicator */
    .mode-badge-agent {
        background-color: #004a77;
        color: #c2e7ff;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 10px;
    }
    .mode-badge-chat {
        background-color: #2b2c2e;
        color: #e3e3e3;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 10px;
    }

    /* Uploaded File Chip */
    .file-chip {
        background-color: #2a2b2d;
        border: 1px solid #444746;
        border-radius: 12px;
        padding: 8px 12px;
        margin-bottom: 10px;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Session State Initialization
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_file_ref" not in st.session_state:
    st.session_state.uploaded_file_ref = None

# ==========================================
# 3. Sidebar Controls (New Chat, Mode, Uploads)
# ==========================================
with st.sidebar:
    st.title("✨ Gemini Studio")
    st.caption("Powered by Google GenAI SDK")
    st.divider()

    # --- 1. Button: New Chat ---
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.uploaded_file_ref = None
        st.rerun()

    st.divider()

    # --- 2. API Key Configuration ---
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        api_key = st.text_input("🔑 Enter Gemini API Key:", type="password")
        if not api_key:
            st.warning("กรุณาใส่ API Key หรือตั้งค่า `GEMINI_API_KEY` ใน Environment")

    # --- 3. Mode Selection (Chatbot vs AI Agent) ---
    st.subheader("⚙️ Select Mode")
    app_mode = st.radio(
        "โหมดการทำงาน:",
        options=["🤖 Chatbot", "⚡ AI Agent"],
        help="• Chatbot: สนทนาโต้ตอบทั่วไป\n• AI Agent: ค้นหาข้อมูลล่าสุดบน Google Search อัตโนมัติ"
    )

    # --- 4. Model Selection ---
    model_name = st.selectbox(
        "รุ่นของ Gemini Model:",
        options=["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"],
        index=0
    )

    st.divider()

    # --- 5. File Upload Option ---
    st.subheader("📎 File Upload")
    uploaded_file = st.file_uploader(
        "อัพโหลดไฟล์เพื่อร่วมวิเคราะห์ (PDF, Image, Text, CSV, Audio, Video)",
        type=["pdf", "txt", "png", "jpg", "jpeg", "csv", "mp3", "mp4"]
    )

    if uploaded_file and api_key:
        if st.button("📤 ประมวลผลไฟล์เข้าสู่ Chat", use_container_width=True):
            with st.spinner("กำลังอัพโหลดและประมวลผลไฟล์ไปยัง Gemini..."):
                try:
                    client = genai.Client(api_key=api_key)
                    # Save temporary file locally
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name

                    # Upload to Gemini Files API
                    g_file = client.files.upload(file=tmp_path)
                    st.session_state.uploaded_file_ref = {
                        "name": uploaded_file.name,
                        "file_obj": g_file
                    }
                    st.success(f"แนบไฟล์สำเร็จ: {uploaded_file.name}")
                    # Remove temp local file
                    os.remove(tmp_path)
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการอัพโหลดไฟล์: {e}")

    # Show active file badge if attached
    if st.session_state.uploaded_file_ref:
        st.markdown(
            f'<div class="file-chip">📄 แนบไฟล์อยู่: <b>{st.session_state.uploaded_file_ref["name"]}</b></div>',
            unsafe_allow_html=True
        )
        if st.button("❌ ลบไฟล์ที่แนบ", size="small"):
            st.session_state.uploaded_file_ref = None
            st.rerun()

# ==========================================
# 4. Main Chat Interface
# ==========================================

# Mode Header Display
if app_mode == "⚡ AI Agent":
    st.markdown('<div class="mode-badge-agent">⚡ AI Agent Active (Web Search Grounding Enabled)</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="mode-badge-chat">🤖 Standard Chatbot Active</div>', unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Box
if prompt := st.chat_input("พิมพ์คำถามของคุณที่นี่..."):
    if not api_key:
        st.error("กรุณากรอก Gemini API Key ใน Sidebar ก่อนเริ่มใช้งาน")
        st.stop()

    # Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response from Gemini
    with st.chat_message("assistant"):
        with st.spinner("Gemini กำลังประมวลผล..."):
            try:
                client = genai.Client(api_key=api_key)

                # Configure tools based on selected mode
                tools = []
                if app_mode == "⚡ AI Agent":
                    # Enable Google Search Grounding for AI Agent
                    tools.append(types.Tool(google_search=types.GoogleSearch()))

                config = types.GenerateContentConfig(
                    tools=tools if tools else None,
                    temperature=0.7 if app_mode == "🤖 Chatbot" else 0.3
                )

                # Prepare contents payload
                contents = []

                # Include history messages
                for msg in st.session_state.messages:
                    contents.append(msg["content"])

                # If a file is attached, pass the file object along with the latest user query
                if st.session_state.uploaded_file_ref:
                    g_file = st.session_state.uploaded_file_ref["file_obj"]
                    # Attach file reference with the payload
                    contents.append(g_file)

                # Request model generation
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config
                )

                # Display response
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการรับข้อมูล: {e}")
```eof

ฉันได้ปรับปรุงเว็บแอปพลิเคชัน Streamlit ของคุณให้เรียบร้อยแล้ว โดยถอดแบบความสวยงามและฟังก์ชันการทำงานมาจาก **Google Gemini** โดยมีฟีเจอร์ใหม่ๆ ดังนี้:

### 🌟 ฟีเจอร์ที่เพิ่มเข้ามาใหม่:
1. **แท็บ/โหมดการทำงาน (Chatbot vs AI Agent):**
   - **🤖 Chatbot:** โหมดสนทนาโต้ตอบทั่วไป รวดเร็ว แม่นยำ
   - **⚡ AI Agent:** โหมดเอเจนต์ขั้นสูง โดยเปิดใช้งาน **Google Search Grounding** ช่วยให้ค้นหาข้อมูลสดใหม่บนอินเทอร์เน็ตมาตอบคำถามให้อัตโนมัติ
2. **ปุ่ม New Chat (➕ New Chat):**
   - อยู่ด้านบนสุดของ Sidebar สามารถกดล้างประวัติการสนทนาและคืนค่าสถานะเพื่อเริ่มแชตใหม่ได้ทันที
3. **ระบบ Upload ไฟล์ (File Upload):**
   - รองรับไฟล์หลากหลายชนิด (PDF, TXT, CSV, รูปภาพ, เสียง, วิดีโอ)
   - ส่งไฟล์ผ่าน `Gemini Files API` (ด้วย SDK ตัวใหม่ `google-genai`) ให้โมเดลอ่านและวิเคราะห์ไฟล์ร่วมกับคำถามได้ทันที
4. **จัดระเบียบหน้าตาเว็บแบบ Gemini UI (Dark Theme):**
   - ตกแต่งด้วย CSS ปรับแต่ง Sidebar, ปุ่มกด, และ Badge แสดงสถานะโหมดให้สวยงาม สะอาดตา เหมือนการใช้งาน Gemini Web App

---

### 📦 ไลบรารีที่จำเป็นต้องติดตั้ง (`requirements.txt`):
```text
streamlit
google-genai
pillow
