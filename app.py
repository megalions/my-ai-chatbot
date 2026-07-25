import streamlit as st
from google import genai

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="My AI Chatbot", page_icon="🤖")
st.title("🤖 My Local-Style AI Chatbot")

# ดึง API Key จาก Secrets ของ Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("กรุณาตั้งค่า GEMINI_API_KEY ใน Streamlit Secrets ก่อนใช้งานครับ")
    st.stop()

# สร้าง Client เชื่อมต่อ Gemini API
client = genai.Client(api_key=api_key)

# จัดการประวัติการคุย (Chat History)
if "messages" not in st.session_state:
    st.session_state.messages = []

# แสดงประวัติการคุยเก่าบนหน้าจอ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# รับข้อความจากผู้ใช้
if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    # แสดงข้อความฝั่งผู้ใช้
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ส่งให้ AI ตอบกลับ
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # รันโมเดล gemini-2.5-flash
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            full_response = response.text
            message_placeholder.markdown(full_response)
            
            # บันทึกคำตอบของ AI ลงประวัติ
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
