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
    layout="centered",
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
LOG_FILE = "nicu_chat_log.csv"


# ======================
# STYLE
# ======================

st.markdown(
    """
<style>
.block-container {
    padding-top: 1.2rem;
    max-width: 860px;
}

h1 {
    text-align: center;
    color: #ff7f50;
    margin-bottom: 0.2rem;
}

.subtitle {
    text-align: center;
    color: #6b7280;
    margin-bottom: 0.8rem;
    font-size: 1rem;
}

.small-note {
    text-align: center;
    color: #9ca3af;
    font-size: 0.92rem;
    margin-bottom: 1rem;
}

.card {
    background: #fff7f3;
    border: 1px solid #ffe3d6;
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 12px;
}

.tip-box {
    background: #fff4f0;
    border: 1px solid #ffd9cc;
    padding: 14px 16px;
    border-radius: 14px;
    margin-top: 8px;
    margin-bottom: 10px;
}

.metric-pill {
    display: inline-block;
    padding: 8px 12px;
    border-radius: 999px;
    background: #fff1eb;
    border: 1px solid #ffd8c8;
    margin-right: 8px;
    margin-bottom: 8px;
    font-size: 0.92rem;
}

[data-testid="stChatMessage"] {
    border-radius: 18px;
    padding: 12px;
    margin-bottom: 10px;
}

textarea {
    border-radius: 12px !important;
}

.quick-btn-row {
    margin-top: 6px;
    margin-bottom: 8px;
}
</style>
""",
    unsafe_allow_html=True,
)


# ======================
# HELPERS
# ======================

def ensure_log_file() -> None:
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "timestamp",
                    "user_message",
                    "assistant_reply",
                    "risk_level",
                    "gad7_score",
                    "sleep_hours",
                    "support_score",
                    "stress_score",
                    "text_stress_level",
                ]
            )


def save_log(
    user_message: str,
    assistant_reply: str,
    risk_level: str,
    gad7_score: int,
    sleep_hours: int,
    support_score: int,
    stress_score: int,
    text_stress_level: str,
) -> None:
    ensure_log_file()
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                datetime.now().isoformat(timespec="seconds"),
                user_message,
                assistant_reply,
                risk_level,
                gad7_score,
                sleep_hours,
                support_score,
                stress_score,
                text_stress_level,
            ]
        )
def load_log_df():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame()

    try:
        return pd.read_csv(LOG_FILE)
    except:
        return pd.DataFrame()



def stress_from_text(text: str) -> str:
    t = (text or "").lower().strip()

    high_keywords = [
        "quá mệt",
        "kiệt sức",
        "hoảng",
        "không chịu nổi",
        "mất ngủ",
        "sợ lắm",
        "rất lo",
        "rối quá",
        "áp lực quá",
        "quá căng",
        "bế tắc",
        "không ổn",
    ]
    moderate_keywords = [
        "lo",
        "căng thẳng",
        "mệt",
        "sợ",
        "buồn",
        "áp lực",
        "khó ngủ",
        "mất bình tĩnh",
    ]

    if any(k in t for k in high_keywords):
        return "High"
    if any(k in t for k in moderate_keywords):
        return "Moderate"
    return "Low"


def blended_risk(
    sleep_hours: int,
    stress_score: int,
    text_level: str,
    gad7_score: int,
) -> str:
    level_points = {"Low": 0, "Moderate": 1, "High": 2}
    score = 0

    if sleep_hours < 4:
        score += 2
    elif sleep_hours < 6:
        score += 1

    if stress_score >= 8:
        score += 2
    elif stress_score >= 5:
        score += 1

    score += level_points[text_level]

    if gad7_score >= 15:
        score += 2
    elif gad7_score >= 10:
        score += 1

    if score >= 4:
        return "High"
    if score >= 2:
        return "Moderate"
    return "Low"


def risk_badge(level: str) -> str:
    if level == "High":
        return "🔴 Căng thẳng cao"
    if level == "Moderate":
        return "🟠 Căng thẳng vừa"
    return "🟢 Tương đối ổn"


def stress_label(score: int) -> tuple[str, str]:
    if score >= 8:
        return "Cao", "error"
    if score >= 5:
        return "Trung bình", "warning"
    return "Thấp", "success"


def build_context(
    user_text: str,
    risk_level: str,
    gad7_score: int,
    sleep_hours: int,
    support_score: int,
    stress_score: int,
    text_stress_level: str,
) -> str:
    return f"""
Bạn đang hỗ trợ một phụ huynh có con nằm NICU.

Thông tin hệ thống:
- Overall risk level: {risk_level}
- GAD7 score: {gad7_score}/21
- Sleep hours: {sleep_hours}
- Family support score: {support_score}/10
- Stress score: {stress_score}/10
- Text-based stress level: {text_stress_level}

Yêu cầu trả lời:
- Viết bằng tiếng Việt
- Đồng cảm, ấm áp, dễ hiểu
- Không chẩn đoán y khoa
- Không thay thế bác sĩ
- Trả lời 3-5 câu
- Có 1 gợi ý nhỏ ngay lúc này
- Kết thúc bằng 1 câu hỏi nhẹ để người dùng tiếp tục chia sẻ

Tin nhắn người dùng:
{user_text}
"""


def ai_reply(context: str, messages: list[dict]) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages + [{"role": "user", "content": context}],
            temperature=0.6,
            max_tokens=320,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Mình đang gặp trục trặc nhỏ nên chưa trả lời mượt được. Bạn thử gửi lại sau vài giây nhé."


# ======================
# SESSION STATE
# ======================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": """
Bạn là NICU Calm Bot.

Nhiệm vụ:
- hỗ trợ cảm xúc phụ huynh có con nằm NICU
- trả lời đồng cảm, bình tĩnh, thực tế
- không chẩn đoán y khoa
- không hứa hẹn điều chắc chắn
- ưu tiên những gợi ý nhỏ, dễ làm ngay
""",
        },
        {
            "role": "assistant",
            "content": "Chào bạn 💛 Mình là NICU Calm Bot. Nếu hôm nay bạn đang thấy lo, mệt hoặc mất ngủ vì bé nằm NICU, bạn có thể kể cho mình nghe.",
        },
    ]

if "gad7_score" not in st.session_state:
    st.session_state.gad7_score = 0

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# ======================
# HEADER
# ======================

st.title("💛 NICU Calm Bot")
st.markdown(
    "<div class='subtitle'>Một người bạn nhỏ giúp bạn bình tĩnh hơn khi bé đang ở NICU</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='small-note'>Hỗ trợ cảm xúc và thông tin chung — không thay thế tư vấn y khoa.</div>",
    unsafe_allow_html=True,
)


# ======================
# STATUS INPUTS
# ======================

st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📊 Hôm nay bạn đang thế nào?")

sleep_hours = st.slider("Bạn ngủ bao nhiêu giờ/đêm?", 0, 12, 5)
support_score = st.slider("Bạn đang nhận được bao nhiêu hỗ trợ từ người thân? (0-10)", 0, 10, 4)
stress_score = st.slider("Mức căng thẳng hiện tại của bạn? (0-10)", 0, 10, 6)

level_text, level_type = stress_label(stress_score)
if level_type == "error":
    st.error(f"🔴 Mức căng thẳng hiện tại: {level_text}")
elif level_type == "warning":
    st.warning(f"🟠 Mức căng thẳng hiện tại: {level_text}")
else:
    st.success(f"🟢 Mức căng thẳng hiện tại: {level_text}")

st.markdown("</div>", unsafe_allow_html=True)


# ======================
# GAD-7
# ======================

with st.expander("🧾 Kiểm tra nhanh mức lo âu (GAD-7)"):
    questions = [
        "Lo lắng, bồn chồn",
        "Không kiểm soát được lo lắng",
        "Lo nhiều việc",
        "Khó thư giãn",
        "Bồn chồn đến mức khó ngồi yên",
        "Dễ cáu hoặc bực bội",
        "Sợ điều xấu sẽ xảy ra",
    ]
    score_map = {
        "Không bao giờ": 0,
        "Vài ngày": 1,
        "Hơn nửa số ngày": 2,
        "Gần như mỗi ngày": 3,
    }

    answers = []
    for i, q in enumerate(questions):
        a = st.radio(q, list(score_map.keys()), key=f"gad7_{i}")
        answers.append(score_map[a])

    if st.button("Tính điểm GAD-7"):
        st.session_state.gad7_score = sum(answers)
        st.success(f"Điểm GAD-7 hiện tại: {st.session_state.gad7_score}/21")


# ======================
# QUICK INSIGHT
# ======================

text_level_preview = stress_from_text(st.session_state.pending_prompt or "")
overall_preview = blended_risk(
    sleep_hours=sleep_hours,
    stress_score=stress_score,
    text_level=text_level_preview,
    gad7_score=st.session_state.gad7_score,
)

st.markdown(
    f"""
<span class="metric-pill">{risk_badge(overall_preview)}</span>
<span class="metric-pill">🛌 Ngủ: {sleep_hours}h</span>
<span class="metric-pill">🤝 Hỗ trợ: {support_score}/10</span>
<span class="metric-pill">🌡 Căng thẳng: {stress_score}/10</span>
<span class="metric-pill">🧾 GAD-7: {st.session_state.gad7_score}/21</span>
""",
    unsafe_allow_html=True,
)


# ======================
# QUICK ACTIONS
# ======================

st.markdown("<div class='tip-box'><b>💡 Gợi ý nhanh:</b></div>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("Mình rất lo cho bé", use_container_width=True):
        st.session_state.pending_prompt = "Mình rất lo cho bé trong NICU và không biết làm sao để bình tĩnh hơn."
with c2:
    if st.button("Mình đang mất ngủ", use_container_width=True):
        st.session_state.pending_prompt = "Mình đang mất ngủ vì lo cho bé nằm NICU."
with c3:
    if st.button("Mình cần bình tĩnh lại", use_container_width=True):
        st.session_state.pending_prompt = "Mình muốn bình tĩnh lại ngay bây giờ, bạn giúp mình được không?"


# ======================
# CHAT
# ======================

st.subheader("💬 Trò chuyện")

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    avatar = "👶" if msg["role"] == "assistant" else "🧑"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

chat_input = st.chat_input("Bạn đang lo điều gì lúc này?")
user_text = chat_input or st.session_state.pending_prompt

if user_text:
    st.session_state.pending_prompt = None

    text_stress_level = stress_from_text(user_text)
    overall_risk = blended_risk(
        sleep_hours=sleep_hours,
        stress_score=stress_score,
        text_level=text_stress_level,
        gad7_score=st.session_state.gad7_score,
    )

    st.session_state.messages.append(
        {"role": "user", "content": user_text}
    )

    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_text)

    context = build_context(
        user_text=user_text,
        risk_level=overall_risk,
        gad7_score=st.session_state.gad7_score,
        sleep_hours=sleep_hours,
        support_score=support_score,
        stress_score=stress_score,
        text_stress_level=text_stress_level,
    )

    with st.chat_message("assistant", avatar="👶"):
        holder = st.empty()
        holder.markdown("👶 NICU Calm Bot đang suy nghĩ...")
        time.sleep(0.8)
        reply = ai_reply(context, st.session_state.messages)
        holder.markdown(reply)

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )

    save_log(
        user_message=user_text,
        assistant_reply=reply,
        risk_level=overall_risk,
        gad7_score=st.session_state.gad7_score,
        sleep_hours=sleep_hours,
        support_score=support_score,
        stress_score=stress_score,
        text_stress_level=text_stress_level,
    )


# ======================
# TREND
# ======================
df = load_log_df()

if not df.empty:

    st.subheader("📈 Xu hướng gần đây")

    chart_df = df.copy()

    if "timestamp" in chart_df.columns:
        chart_df["timestamp"] = pd.to_datetime(chart_df["timestamp"], errors="coerce")
        chart_df = chart_df.dropna(subset=["timestamp"])
        chart_df = chart_df.sort_values("timestamp")

        cols = []

        if "gad7_score" in chart_df.columns:
            cols.append("gad7_score")

        if "stress_score" in chart_df.columns:
            cols.append("stress_score")

        if cols:
            chart_df = chart_df.set_index("timestamp")
            st.line_chart(chart_df[cols])

    chart_df = chart_df.sort_values("timestamp").tail(20)
    chart_df = chart_df.set_index("timestamp")

cols = []
if "gad7_score" in chart_df.columns:
    cols.append("gad7_score")
if "stress_score" in chart_df.columns:
    cols.append("stress_score")

if cols:
    st.line_chart(chart_df[cols])

    if not chart_df.empty:
        st.line_chart(chart_df)

    st.download_button(
        "⬇️ Tải dữ liệu cuộc trò chuyện",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="nicu_chat_log.csv",
        mime="text/csv",
    )


# ======================
# RESET
# ======================

if st.button("🧹 Bắt đầu lại cuộc trò chuyện"):
    st.session_state.messages = st.session_state.messages[:2]
    st.session_state.pending_prompt = None
    st.rerun()
