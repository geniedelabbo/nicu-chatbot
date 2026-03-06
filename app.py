import os
import csv
from datetime import datetime
import pandas as pd
import streamlit as st

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="NICU Calm Bot – BigML Integrated",
    page_icon="💛",
    layout="wide"
)

# =========================
# CONSTANTS
# =========================
APP_TITLE = "💛 NICU Calm Bot – BigML Integrated"
APP_SUBTITLE = "Demo: Chatbot hỗ trợ phụ huynh NICU + GAD-7 + AI Risk Level (BigML rules) + log & export CSV"

LOG_FILE = "nicu_chat_log.csv"
REPORT_MODEL_ID = "699d80da0c539f20892733f4"  # Model ID của bà (đúng như BigML hiện)

GAD7_ITEMS = [
    "Cảm thấy lo lắng, bồn chồn hoặc căng thẳng",
    "Không thể ngừng hoặc kiểm soát lo lắng",
    "Lo lắng quá nhiều về nhiều việc khác nhau",
    "Khó thư giãn",
    "Bồn chồn đến mức khó ngồi yên",
    "Dễ cáu hoặc bực bội",
    "Sợ điều gì đó tệ hại sẽ xảy ra",
]

GAD7_CHOICES = {
    "0 - Không bao giờ": 0,
    "1 - Vài ngày": 1,
    "2 - Hơn nửa số ngày": 2,
    "3 - Gần như mỗi ngày": 3,
}

# =========================
# BIGML EXPORTED RULES (Python)
# =========================
# Đây là hàm bà copy từ BigML "Actionable Model Download" (model/699d80da0c539f20892733f4)
def predict_anxiety_level(sleep_hours=None,
                          baby_rehospital=None,
                          support_score=None,
                          emotion_score=None):
    """ Predictor for anxiety_level from model/699d80da0c539f20892733f4

        Predictive model by BigML - Machine Learning Made Easy
    """
    if (support_score is None):
        return 'Low'
    if (support_score > 9):
        if (sleep_hours is None):
            return 'Low'
        if (sleep_hours > 7):
            return 'Moderate'
        if (sleep_hours <= 7):
            if (baby_rehospital is None):
                return 'Low'
            if (baby_rehospital > 0):
                return 'Low'
            if (baby_rehospital <= 0):
                if (emotion_score is None):
                    return 'Low'
                if (emotion_score > 4):
                    return 'Low'
                if (emotion_score <= 4):
                    return 'Moderate'
    if (support_score <= 9):
        if (support_score > 3):
            if (sleep_hours is None):
                return 'Moderate'
            if (sleep_hours > 6):
                if (emotion_score is None):
                    return 'Moderate'
                if (emotion_score > 2):
                    if (emotion_score > 6):
                        if (emotion_score > 9):
                            if (support_score > 8):
                                return 'Moderate'
                            if (support_score <= 8):
                                return 'Low'
                        if (emotion_score <= 9):
                            if (sleep_hours > 7):
                                if (support_score > 8):
                                    return 'High'
                                if (support_score <= 8):
                                    if (baby_rehospital is None):
                                        return 'Moderate'
                                    if (baby_rehospital > 0):
                                        return 'Moderate'
                                    if (baby_rehospital <= 0):
                                        return 'High'
                            if (sleep_hours <= 7):
                                if (support_score > 6):
                                    if (support_score > 8):
                                        return 'Moderate'
                                    if (support_score <= 8):
                                        return 'Low'
                                if (support_score <= 6):
                                    return 'Moderate'
                    if (emotion_score <= 6):
                        if (emotion_score > 5):
                            return 'Low'
                        if (emotion_score <= 5):
                            if (support_score > 4):
                                if (support_score > 8):
                                    return 'Low'
                                if (support_score <= 8):
                                    if (baby_rehospital is None):
                                        return 'Moderate'
                                    if (baby_rehospital > 1):
                                        return 'Low'
                                    if (baby_rehospital <= 1):
                                        if (emotion_score > 4):
                                            return 'Moderate'
                                        if (emotion_score <= 4):
                                            if (support_score > 7):
                                                return 'Moderate'
                                            if (support_score <= 7):
                                                if (sleep_hours > 8):
                                                    return 'Low'
                                                if (sleep_hours <= 8):
                                                    return 'Low'
                            if (support_score <= 4):
                                return 'Low'
                if (emotion_score <= 2):
                    if (sleep_hours > 7):
                        if (support_score > 5):
                            return 'Moderate'
                        if (support_score <= 5):
                            return 'High'
                    if (sleep_hours <= 7):
                        if (support_score > 7):
                            return 'High'
                        if (support_score <= 7):
                            if (support_score > 5):
                                return 'Low'
                            if (support_score <= 5):
                                if (emotion_score > 1):
                                    return 'Low'
                                if (emotion_score <= 1):
                                    return 'Moderate'
            if (sleep_hours <= 6):
                if (emotion_score is None):
                    return 'Moderate'
                if (emotion_score > 2):
                    if (sleep_hours > 5):
                        if (support_score > 7):
                            if (support_score > 8):
                                return 'High'
                            if (support_score <= 8):
                                return 'Moderate'
                        if (support_score <= 7):
                            return 'High'
                    if (sleep_hours <= 5):
                        if (support_score > 4):
                            if (baby_rehospital is None):
                                return 'Moderate'
                            if (baby_rehospital > 1):
                                if (emotion_score > 6):
                                    return 'High'
                                if (emotion_score <= 6):
                                    return 'Moderate'
                            if (baby_rehospital <= 1):
                                if (emotion_score > 3):
                                    if (baby_rehospital > 0):
                                        if (emotion_score > 7):
                                            if (emotion_score > 9):
                                                return 'Low'
                                            if (emotion_score <= 9):
                                                return 'Moderate'
                                        if (emotion_score <= 7):
                                            return 'Low'
                                    if (baby_rehospital <= 0):
                                        if (support_score > 5):
                                            if (emotion_score > 8):
                                                return 'High'
                                            if (emotion_score <= 8):
                                                if (support_score > 7):
                                                    return 'Low'
                                                if (support_score <= 7):
                                                    if (emotion_score > 5):
                                                        if (support_score > 6):
                                                            return 'Moderate'
                                                        if (support_score <= 6):
                                                            return 'Low'
                                                    if (emotion_score <= 5):
                                                        if (sleep_hours > 4):
                                                            return 'High'
                                                        if (sleep_hours <= 4):
                                                            return 'Moderate'
                                        if (support_score <= 5):
                                            if (sleep_hours > 3):
                                                return 'Low'
                                            if (sleep_hours <= 3):
                                                return 'High'
                                if (emotion_score <= 3):
                                    if (sleep_hours > 4):
                                        return 'High'
                                    if (sleep_hours <= 4):
                                        return 'Moderate'
                        if (support_score <= 4):
                            if (sleep_hours > 3):
                                return 'Moderate'
                            if (sleep_hours <= 3):
                                return 'High'
                if (emotion_score <= 2):
                    if (sleep_hours > 3):
                        if (support_score > 7):
                            if (emotion_score > 1):
                                return 'Moderate'
                            if (emotion_score <= 1):
                                if (emotion_score > 0):
                                    if (support_score > 8):
                                        return 'Low'
                                    if (support_score <= 8):
                                        if (baby_rehospital is None):
                                            return 'Low'
                                        if (baby_rehospital > 1):
                                            return 'Low'
                                        if (baby_rehospital <= 1):
                                            return 'Low'
                                if (emotion_score <= 0):
                                    return 'High'
                        if (support_score <= 7):
                            if (support_score > 4):
                                return 'Low'
                            if (support_score <= 4):
                                if (sleep_hours > 5):
                                    return 'Moderate'
                                if (sleep_hours <= 5):
                                    return 'Low'
                    if (sleep_hours <= 3):
                        if (baby_rehospital is None):
                            return 'Moderate'
                        if (baby_rehospital > 1):
                            return 'Moderate'
                        if (baby_rehospital <= 1):
                            if (support_score > 7):
                                if (emotion_score > 0):
                                    return 'Moderate'
                                if (emotion_score <= 0):
                                    return 'Low'
                            if (support_score <= 7):
                                return 'High'
        if (support_score <= 3):
            if (emotion_score is None):
                return 'Low'
            if (emotion_score > 3):
                if (support_score > 1):
                    if (baby_rehospital is None):
                        return 'High'
                    if (baby_rehospital > 1):
                        if (emotion_score > 7):
                            if (emotion_score > 8):
                                return 'High'
                            if (emotion_score <= 8):
                                return 'Low'
                        if (emotion_score <= 7):
                            return 'High'
                    if (baby_rehospital <= 1):
                        if (support_score > 2):
                            if (emotion_score > 6):
                                return 'High'
                            if (emotion_score <= 6):
                                return 'Low'
                        if (support_score <= 2):
                            if (emotion_score > 6):
                                if (emotion_score > 9):
                                    return 'Moderate'
                                if (emotion_score <= 9):
                                    return 'High'
                            if (emotion_score <= 6):
                                return 'Moderate'
                if (support_score <= 1):
                    if (sleep_hours is None):
                        return 'Low'
                    if (sleep_hours > 4):
                        if (sleep_hours > 7):
                            if (sleep_hours > 8):
                                if (emotion_score > 5):
                                    if (baby_rehospital is None):
                                        return 'Moderate'
                                    if (baby_rehospital > 0):
                                        if (emotion_score > 9):
                                            return 'Low'
                                        if (emotion_score <= 9):
                                            if (support_score > 0):
                                                if (emotion_score > 7):
                                                    return 'Moderate'
                                                if (emotion_score <= 7):
                                                    return 'Low'
                                            if (support_score <= 0):
                                                return 'Moderate'
                                    if (baby_rehospital <= 0):
                                        if (support_score > 0):
                                            return 'High'
                                        if (support_score <= 0):
                                            return 'Moderate'
                                if (emotion_score <= 5):
                                    return 'High'
                            if (sleep_hours <= 8):
                                return 'High'
                        if (sleep_hours <= 7):
                            return 'Moderate'
                    if (sleep_hours <= 4):
                        if (baby_rehospital is None):
                            return 'Low'
                        if (baby_rehospital > 0):
                            return 'Low'
                        if (baby_rehospital <= 0):
                            if (emotion_score > 7):
                                return 'Low'
                            if (emotion_score <= 7):
                                if (emotion_score > 5):
                                    return 'Moderate'
                                if (emotion_score <= 5):
                                    if (support_score > 0):
                                        if (sleep_hours > 3):
                                            return 'Low'
                                        if (sleep_hours <= 3):
                                            return 'Moderate'
                                    if (support_score <= 0):
                                        return 'Low'
            if (emotion_score <= 3):
                if (support_score > 0):
                    if (sleep_hours is None):
                        return 'High'
                    if (sleep_hours > 3):
                        if (baby_rehospital is None):
                            return 'Low'
                        if (baby_rehospital > 1):
                            return 'Low'
                        if (baby_rehospital <= 1):
                            if (sleep_hours > 5):
                                if (baby_rehospital > 0):
                                    return 'High'
                                if (baby_rehospital <= 0):
                                    if (sleep_hours > 6):
                                        if (support_score > 1):
                                            return 'Low'
                                        if (support_score <= 1):
                                            return 'High'
                                    if (sleep_hours <= 6):
                                        return 'High'
                            if (sleep_hours <= 5):
                                return 'Low'
                    if (sleep_hours <= 3):
                        return 'High'
                if (support_score <= 0):
                    return 'Low'


# =========================
# EXPLAINABLE TRACING (no need to rewrite the tree)
# =========================
class TraceNumber(float):
    """A float that logs comparisons so we can reconstruct the decision path."""
    def __new__(cls, name, value, trace):
        obj = float.__new__(cls, value)
        obj.name = name
        obj.trace = trace
        return obj

    def _log(self, op, other, result):
        try:
            other_v = float(other)
        except Exception:
            other_v = other
        self.trace.append(f"{self.name} {op} {other_v} -> {result}")
        return result

    def __gt__(self, other):  # >
        return self._log(">", other, float(self) > float(other))
    def __ge__(self, other):  # >=
        return self._log(">=", other, float(self) >= float(other))
    def __lt__(self, other):  # <
        return self._log("<", other, float(self) < float(other))
    def __le__(self, other):  # <=
        return self._log("<=", other, float(self) <= float(other))
    def __eq__(self, other):  # ==
        return self._log("==", other, float(self) == float(other))

def predict_with_trace(predict_fn, *, sleep_hours, baby_rehospital, support_score, emotion_score):
    trace = []
    y = predict_fn(
        TraceNumber("sleep_hours", sleep_hours, trace),
        TraceNumber("baby_rehospital", baby_rehospital, trace),
        TraceNumber("support_score", support_score, trace),
        TraceNumber("emotion_score", emotion_score, trace),
    )
    true_path = [t for t in trace if t.endswith("-> True")]
    return y, (true_path if true_path else trace)

# =========================
# UTILITIES: LOG / EXPORT
# =========================
def ensure_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "timestamp",
                "user_text",
                "sleep_hours",
                "support_score",
                "emotion_score",
                "baby_rehospital",
                "gad7_score",
                "bigml_risk",
            ])

def append_log(row: dict):
    ensure_log_file()
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            row.get("timestamp"),
            row.get("user_text"),
            row.get("sleep_hours"),
            row.get("support_score"),
            row.get("emotion_score"),
            row.get("baby_rehospital"),
            row.get("gad7_score"),
            row.get("bigml_risk"),
        ])

def load_log_df():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=[
            "timestamp","user_text","sleep_hours","support_score","emotion_score",
            "baby_rehospital","gad7_score","bigml_risk"
        ])
    return pd.read_csv(LOG_FILE)

def gad7_level_from_score(score: int) -> str:
    # chuẩn hay dùng: 0–4 minimal, 5–9 mild, 10–14 moderate, 15–21 severe
    if score >= 15:
        return "Cao (Severe)"
    if score >= 10:
        return "Vừa (Moderate)"
    if score >= 5:
        return "Nhẹ (Mild)"
    return "Thấp (Minimal)"

def interventions(bigml_risk: str, gad7_score: int):
    # Khuyến nghị can thiệp dạng an toàn – không mô tả/hướng dẫn tự hại.
    gad_level = gad7_level_from_score(gad7_score)
    items = []

    # Ưu tiên theo gad7 và bigml
    if gad7_score >= 15 or bigml_risk == "High":
        badge = "🔴 Nguy cơ cao"
        items.append("Ưu tiên tìm hỗ trợ trực tiếp: trao đổi với bác sĩ theo dõi NICU hoặc chuyên gia tâm lý.")
        items.append("Giảm tải ngay trong hôm nay: nhờ người thân chia ca chăm, xin nghỉ 1–2 giờ để ngủ bù/ăn uống.")
        items.append("Kỹ thuật nhanh 3 phút: thở chậm đều (hít 4 – thở 6) + thả lỏng vai/hàm.")
        items.append("Viết ra 1 việc nhỏ có thể làm ngay (vd: gọi 1 người thân, ăn 1 bữa, tắm nhanh, chợp mắt 20 phút).")
    elif gad7_score >= 10 or bigml_risk == "Moderate":
        badge = "🟠 Nguy cơ mức vừa"
        items.append("Tăng hỗ trợ: nhắn 1 người thân/nhóm phụ huynh NICU để có người lắng nghe và hỗ trợ việc cụ thể.")
        items.append("Ổn định lại giấc ngủ: chốt 1 khung ngủ bù 20–40 phút/ngày, hạn chế caffein sau 14h.")
        items.append("Grounding 5-4-3-2-1 (nhìn 5 thứ, chạm 4 thứ, nghe 3 âm, ngửi 2 mùi, nếm 1 vị).")
        items.append("Ghi chú lo âu: 'Mình đang lo điều gì? Mình kiểm soát được phần nào? 1 bước nhỏ tiếp theo là gì?'")
    else:
        badge = "🟢 Nguy cơ thấp"
        items.append("Duy trì nhịp sinh hoạt: ngủ đủ nhất có thể + ăn đúng bữa + uống nước.")
        items.append("Tự chăm 10 phút/ngày: đi bộ nhẹ, tắm ấm, nghe nhạc, giãn cơ cổ/vai.")
        items.append("Theo dõi định kỳ: làm lại GAD-7 mỗi 1–2 tuần để thấy xu hướng.")

    return badge, gad_level, items

def build_report_md(model_id, bigml_risk, gad7_score, rule_path, sleep_hours, support_score, emotion_score, baby_rehospital, user_text):
    baby_txt = "Có" if baby_rehospital > 0 else "Không"
    badge, gad_level, items = interventions(bigml_risk, gad7_score)

    lines = []
    lines.append("# Báo cáo đồ án – Ứng dụng AI (BigML) cho Chatbot NICU")
    lines.append("")
    lines.append("## 1) Mục tiêu")
    lines.append("- Xây dựng chatbot hỗ trợ phụ huynh có con nằm NICU.")
    lines.append("- Tích hợp mô hình BigML (Supervised) để phân loại mức nguy cơ lo âu (Low/Moderate/High).")
    lines.append("- Kết hợp thang đo GAD-7 để có thêm góc nhìn sàng lọc.")
    lines.append("")
    lines.append("## 2) Mô hình")
    lines.append(f"- Model ID (BigML): `{model_id}`")
    lines.append("- Kiểu mô hình: Decision Tree (rules).")
    lines.append("")
    lines.append("## 3) Dữ liệu đầu vào (demo)")
    lines.append(f"- Nội dung người dùng nhập: {user_text if user_text else '(trống)'}")
    lines.append(f"- sleep_hours: {sleep_hours}")
    lines.append(f"- support_score: {support_score}")
    lines.append(f"- emotion_score: {emotion_score}")
    lines.append(f"- baby_rehospital: {baby_txt}")
    lines.append(f"- GAD-7 score: {gad7_score}/21  →  mức: {gad_level}")
    lines.append("")
    lines.append("## 4) Kết quả dự đoán")
    lines.append(f"- BigML Risk Level: **{bigml_risk}**")
    lines.append(f"- Nhãn can thiệp: {badge}")
    lines.append("")
    lines.append("## 5) Giải thích mô hình (Rule path)")
    for r in rule_path[:25]:
        lines.append(f"- {r}")
    if len(rule_path) > 25:
        lines.append(f"- (Còn {len(rule_path)-25} điều kiện nữa...)")
    lines.append("")
    lines.append("## 6) Khuyến nghị can thiệp")
    for it in items:
        lines.append(f"- {it}")
    lines.append("")
    lines.append("## 7) Evaluation (mô tả cách làm)")
    lines.append("- Tạo dataset Train/Test (80/20) trên BigML.")
    lines.append("- Create Model từ Training dataset.")
    lines.append("- Evaluate model với Test dataset để lấy Accuracy/Precision/Recall/F1 và Confusion Matrix.")
    lines.append("")
    return "\n".join(lines)

def simple_chat_reply(text: str, risk: str, gad7_score: int):
    # Trả lời an toàn, hỗ trợ cảm xúc, không nhập vai tình cảm.
    text_l = (text or "").lower()
    if not text_l.strip():
        return "Bạn có thể kể ngắn: điều gì làm bạn lo nhất lúc này? (vd: kết quả của bé, lịch thăm, tài chính, mất ngủ...)"

    badge, gad_level, items = interventions(risk, gad7_score)

    # 1 câu phản hồi + 1 câu hỏi + 1 gợi ý nhỏ
    resp = []
    resp.append("Mình nghe bạn rồi. Chăm con trong NICU dễ khiến người lớn căng thẳng và mất ngủ, điều đó rất bình thường.")
    resp.append(f"Hiện hệ thống đang ghi nhận: **BigML = {risk}**, **GAD-7 = {gad7_score}/21 ({gad_level})**.")
    resp.append(f"{badge}: gợi ý 1 việc nhỏ ngay bây giờ → **{items[0]}**")
    resp.append("Bạn muốn mình giúp theo hướng nào trước: **(1) giảm lo nhanh 3 phút**, **(2) sắp lịch ngủ/nghỉ**, hay **(3) soạn câu hỏi để hỏi bác sĩ NICU**?")
    return "\n\n".join(resp)

# =========================
# SESSION STATE INIT
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role":"user/assistant","content":...}]
if "last_rule_path" not in st.session_state:
    st.session_state.last_rule_path = []
if "last_gad7_score" not in st.session_state:
    st.session_state.last_gad7_score = 0
if "model_risk" not in st.session_state:
    st.session_state.model_risk = "Low"

# =========================
# UI HEADER
# =========================
st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

# Layout columns
left, right = st.columns([1.35, 1.0], gap="large")

# =========================
# RIGHT: AI DASHBOARD + GAD7
# =========================
with right:
    st.subheader("📊 AI Dashboard")

    # Quick info sliders
    sleep_hours = st.slider("Bạn ngủ trung bình bao nhiêu giờ/đêm?", 0, 12, 5)
    support_score = st.slider("Mức hỗ trợ bạn đang có (0=không ai, 10=rất nhiều)?", 0, 10, 4)
    emotion_score = st.slider("Mức căng thẳng/kiệt sức cảm xúc (0-10)?", 0, 10, 6)
    baby_rehospital_txt = st.selectbox("Bé có tái nhập viện gần đây không?", ["Không", "Có"])
    baby_rehospital = 1 if baby_rehospital_txt == "Có" else 0

    # BigML prediction + trace
    bigml_risk, rule_path = predict_with_trace(
        predict_anxiety_level,
        sleep_hours=float(sleep_hours),
        baby_rehospital=float(baby_rehospital),
        support_score=float(support_score),
        emotion_score=float(emotion_score),
    )
    st.session_state.model_risk = bigml_risk
    st.session_state.last_rule_path = rule_path

    st.markdown(f"**BigML Risk Level:** `{bigml_risk}`")

    with st.expander("🧠 Vì sao AI ra kết quả này? (Rule path)"):
        for r in rule_path[:20]:
            st.write("• " + r)
        if len(rule_path) > 20:
            st.caption(f"(Còn {len(rule_path)-20} điều kiện nữa…)")

    st.divider()
    st.subheader("🧾 GAD-7 Screening")

    with st.form("gad7_form"):
        answers = []
        for i, item in enumerate(GAD7_ITEMS, start=1):
            choice = st.radio(
                f"{i}. {item}",
                list(GAD7_CHOICES.keys()),
                index=0,
                key=f"gad7_{i}"
            )
            answers.append(GAD7_CHOICES[choice])

        submitted = st.form_submit_button("Tính điểm & Phân loại")

    if submitted:
        gad7_score = int(sum(answers))
        st.session_state.last_gad7_score = gad7_score
        st.success(f"Điểm GAD-7: {gad7_score}/21  →  {gad7_level_from_score(gad7_score)}")

        badge, gad_level, items = interventions(bigml_risk, gad7_score)
        st.markdown("### 🧩 Khuyến nghị can thiệp")
        st.info(f"{badge} • GAD-7: {gad_level}")
        for it in items:
            st.write("• " + it)

# =========================
# LEFT: CHAT
# =========================
with left:
    st.subheader("💬 Trò chuyện")
    # Chat history
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Chat input
    user_text = st.chat_input("Bạn đang lo điều gì hôm nay? (vd: bé đang nằm NICU, mình mất ngủ, lo bé tái nhập viện...)")

    if user_text is not None:
        # add user message
        st.session_state.messages.append({"role": "user", "content": user_text})

        gad7_score = int(st.session_state.last_gad7_score)
        risk = st.session_state.model_risk

        # assistant reply
        reply = simple_chat_reply(user_text, risk, gad7_score)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # log
        append_log({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "user_text": user_text,
            "sleep_hours": sleep_hours,
            "support_score": support_score,
            "emotion_score": emotion_score,
            "baby_rehospital": baby_rehospital,
            "gad7_score": gad7_score,
            "bigml_risk": risk,
        })

        # render last assistant message immediately
        with st.chat_message("assistant"):
            st.markdown(reply)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🧹 Xóa phiên chat (không xóa file log)"):
            st.session_state.messages = []
            st.success("Đã xóa chat trên màn hình. File log vẫn giữ nguyên.")
    with col_b:
        df = load_log_df()
        st.download_button(
            "⬇️ Tải log CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="nicu_chat_log.csv",
            mime="text/csv"
        )

    st.divider()
    st.subheader("📄 Xuất báo cáo (copy nộp Word)")
    gad7_score_now = int(st.session_state.last_gad7_score)
    risk_now = st.session_state.model_risk
    rule_path_now = st.session_state.last_rule_path

    if st.button("Tạo báo cáo Markdown"):
        md = build_report_md(
            REPORT_MODEL_ID,
            risk_now,
            gad7_score_now,
            rule_path_now,
            sleep_hours,
            support_score,
            emotion_score,
            baby_rehospital,
            user_text or ""
        )
        st.code(md, language="markdown")
        st.success("Copy toàn bộ khung Markdown này dán vào Word/Google Docs là xong ✅")

    with st.expander("📌 Gợi ý phần Evaluation để bà điền vào báo cáo"):
        st.markdown(
            """
- Vào BigML → **Supervised** → mở **Model**
- Chọn **Evaluate** → chọn **Test dataset (20%)** → bấm **Evaluate**
- Ghi lại: **Accuracy, Precision, Recall, F1, Confusion Matrix**
- Nếu Accuracy quá cao (100%) thì giải thích khả năng **dữ liệu quá ít / quá dễ / có leakage**, và đề xuất tăng dữ liệu, thêm biến, làm kiểm định chéo.
            """.strip()
        )