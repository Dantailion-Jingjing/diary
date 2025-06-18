import streamlit as st
import csv
from datetime import date

CSV_PATH = "data/honey_diary.csv"

st.title("💗静静和老公的甜蜜回忆")

today = st.date_input("📅日期",value=date.today())

emotion_jingjing = st.text_area("🐈静静今天的心情")
emotion_quanquan = st.text_area("🐈<200d>⬛圈圈今天的心情")
diary = st.text_area("💌今天的小小记录")
plan = st.text_area("🌖想做的事情")


if st.button("🛏️  保存"):
    with open(CSV_PATH, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["today","emotion_jingjing", "emotion_quanquan", "diary", "plan"])
        try:
            f.seek(0)
            first_line = f.readline()
            if "date" not in first_line:
                writer.writeheader()
        except:
            writer.writeheader()
        writer.writerow({
            "today": today,
            "emotion_jingjing": emotion_jingjing,
            "emotion_quanquan": emotion_quanquan,
            "diary": diary,
            "plan": plan
        })
    st.success("✅已经刻入花花的脑袋瓜啦～")

# データ読み込み＆表示
st.markdown("---")
st.subheader("🧸过去的回忆...")

try:
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reversed(list(reader)):
 #            st.write(f"### 🗓️  {row['today']}")
            st.markdown(f"""
**🐈静静今天的心情**
{row['emotion_jingjing']}

**🐈<200d>⬛圈圈今天的心情**
{row['emotion_quanquan']}

**💌今天的小小记录**
{row['diary']}

**🌖想做的事情**
{row['plan']}
---
""")
except FileNotFoundError:
    st.info("快来记录我们的心情吧～！")
