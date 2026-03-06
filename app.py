import os
import csv
import time
from datetime import datetime

import pandas as pd
import streamlit as st
from openai import OpenAI


# ======================
# PAGE CONFIG
# ======================

st.set_page_config(
    page_title="NICU Calm Bot",
    page_icon="💛",
    layout="centered"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

LOG_FILE = "nicu_chat_log.csv"


# ======================
# STYLE
# ======================

st.markdown("""
<style>

.block-container{
padding-top:1.2rem;
max-width:850px;
}

h1{
text-align:center;
color:#ff7f50;
}

.subtitle{
text-align:center;
color:gray;
margin-bottom:25px;
}

[data-testid="stChatMessage"]{
border-radius:18px;
padding:12px;
margin-bottom:10px;
}

textarea{
border-radius:12px !important;
}

.tip-box{
background:#fff4f0;
padding:14px;
border-radius:12px;
margin-top:10px;
}

</style>
""", unsafe_allow_html=True)


# ======================
# HEADER
# ======================

st.title("💛 NICU Calm Bot")

st.markdown(
"<div class='subtitle'>Một người bạn nhỏ giúp bạn bình tĩnh hơn khi bé đang ở NICU</div>",
unsafe_allow_html=True
)

st.caption("NICU Calm Bot hỗ trợ cảm xúc. Không thay thế tư vấn y khoa.")


# ======================
# SESSION
# ======================

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role":"system",
            "content":"""
Bạn là NICU Calm Bot.

Bạn hỗ trợ phụ huynh có con nằm NICU.

Nguyên tắc:
- nói chuyện đồng cảm
- giải thích nhẹ nhàng
- gợi ý hành động nhỏ
- không chẩn đoán y khoa
- trả lời 3-5 câu
"""
        }
    ]

if len(st.session_state.messages) == 1:
    st.session_state.messages.append({
        "role":"assistant",
        "content":"Chào bạn 💛 Mình là NICU Calm Bot. Bạn có thể chia sẻ điều đang khiến bạn lo lắng."
    })


if "risk_level" not in st.session_state:
    st.session_state.risk_level="Low"

if "gad7_score" not in st.session_state:
    st.session_state.gad7_score=0


# ======================
# LOG
# ======================

def ensure_log():

    if not os.path.exists(LOG_FILE):

        with open(LOG_FILE,"w",newline="",encoding="utf-8") as f:

            writer=csv.writer(f)

            writer.writerow([
                "time",
                "message",
                "risk",
                "gad7"
            ])


def save_log(text):

    ensure_log()

    with open(LOG_FILE,"a",newline="",encoding="utf-8") as f:

        writer=csv.writer(f)

        writer.writerow([
            datetime.now().isoformat(),
            text,
            st.session_state.risk_level,
            st.session_state.gad7_score
        ])


# ======================
# QUICK STATUS
# ======================

st.divider()

st.subheader("📊 Bạn đang cảm thấy thế nào hôm nay?")

sleep_hours = st.slider("Bạn ngủ bao nhiêu giờ/đêm?",0,12,5)

support_score = st.slider("Mức hỗ trợ từ người thân (0-10)",0,10,4)

stress = st.slider("Mức căng thẳng hiện tại (0-10)",0,10,6)


if sleep_hours <4 or stress>7:
    risk="High"
elif sleep_hours<6:
    risk="Moderate"
else:
    risk="Low"

st.session_state.risk_level=risk


# ======================
# CONTEXT
# ======================

def build_context(user_text):

    return f"""
Risk level: {st.session_state.risk_level}

GAD7 score: {st.session_state.gad7_score}

User message:
{user_text}
"""


# ======================
# AI RESPONSE
# ======================

def ai_reply(context):

    try:

        response = client.chat.completions.create(

            model="gpt-4o-mini",

            messages=st.session_state.messages+
            [{"role":"user","content":context}],

            temperature=0.6,
            max_tokens=300
        )

        return response.choices[0].message.content

    except:

        return "Xin lỗi, hệ thống đang gặp lỗi tạm thời."


# ======================
# CHAT
# ======================

st.divider()

st.subheader("💬 Trò chuyện")

for m in st.session_state.messages:

    if m["role"]=="system":
        continue

    avatar="👶" if m["role"]=="assistant" else "🧑"

    with st.chat_message(m["role"],avatar=avatar):

        st.markdown(m["content"])


user_text=st.chat_input("Bạn đang lo điều gì lúc này?")

if user_text:

    st.session_state.messages.append({
        "role":"user",
        "content":user_text
    })

    with st.chat_message("user",avatar="🧑"):

        st.markdown(user_text)

    with st.chat_message("assistant",avatar="👶"):

        typing=st.empty()

        typing.markdown("👶 NICU Calm Bot đang suy nghĩ...")

        time.sleep(1)

        context=build_context(user_text)

        reply=ai_reply(context)

        typing.markdown(reply)

    st.session_state.messages.append({
        "role":"assistant",
        "content":reply
    })

    save_log(user_text)


# ======================
# RESET
# ======================

if st.button("🧹 Bắt đầu lại cuộc trò chuyện"):

    st.session_state.messages=st.session_state.messages[:1]

    st.rerun()


# ======================
# DOWNLOAD LOG
# ======================

if os.path.exists(LOG_FILE):

    df=pd.read_csv(LOG_FILE)

    st.download_button(
        "⬇️ Tải dữ liệu chat",
        df.to_csv(index=False),
        "nicu_chat_log.csv"
    )

