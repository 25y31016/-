import streamlit as st
import requests
import datetime
import pytz
import re
import plotly.graph_objects as go
import random

# ===== 한국 시간 =====
KST = pytz.timezone("Asia/Seoul")
today = datetime.datetime.now(KST).strftime("%Y%m%d")

# ===== Streamlit 기본 설정 =====
st.set_page_config(page_title="상암고 급식", page_icon="🍴", layout="wide")

# ===== CSS =====
st.markdown("""
    <style>
        body {
            background-color: #f9f9f9;
            color: #222222;
        }
        .title {
            font-size: 40px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
            color: #1a1a1a;
        }
        .shake-emoji {
          display:inline-block;
          animation: shake 0.8s 6;
          font-size:25px;
        }
        @keyframes shake {
          0% { transform: translate(1px, 1px) rotate(0deg); }
          20% { transform: translate(-1px, -2px) rotate(-2deg); }
          40% { transform: translate(-3px, 0px) rotate(2deg); }
          60% { transform: translate(3px, 2px) rotate(0deg); }
          80% { transform: translate(1px, -1px) rotate(2deg); }
          100% { transform: translate(-1px, 2px) rotate(-2deg); }
        }
        /* 팝업 스타일 */
        .popup {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
            z-index: 9999;
            max-width: 400px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# ===== Fun Fact 리스트 =====
fun_facts = [
    "🥦 비타민 C는 면역력을 강화하고 피로 회복에 도움을 줘요!",
    "🥛 칼슘은 뼈 건강에 필수적이며 성장기 학생에게 꼭 필요합니다.",
    "🍚 탄수화물은 뇌의 주 에너지원이에요.",
    "🍗 단백질은 근육 형성과 회복에 중요한 역할을 해요.",
    "🥕 채소에 들어있는 식이섬유는 소화 건강을 도와줘요.",
    "🥩 철분은 혈액 속 산소 운반을 도와 피로를 줄여줍니다.",
]

# ===== 제목 =====
st.markdown("<div class='title'>🍴 상암고 오늘의 급식 🍴</div>", unsafe_allow_html=True)

# ===== 날짜 선택 =====
selected_date = st.date_input("날짜 선택", datetime.datetime.now(KST)).strftime("%Y%m%d")

# ===== NEIS API 요청 =====
url = (
    "https://open.neis.go.kr/hub/mealServiceDietInfo"
    "?ATPT_OFCDC_SC_CODE=B10&SD_SCHUL_CODE=7010806&Type=json&MLSV_YMD=" + selected_date
)
response = requests.get(url)
data = response.json()

if "mealServiceDietInfo" not in data:
    st.warning("해당 날짜에는 급식 정보가 없습니다 🍽️")
else:
    meals = data["mealServiceDietInfo"][1]["row"]

    for meal in meals:
        meal_name = meal["MMEAL_SC_NM"]  # 조식/중식/석식
        dish_str = meal["DDISH_NM"].replace("<br/>", "\n")
        clean = re.sub(r"\d|\(|\)|\.", "", dish_str).strip()
        nutr_info = meal.get("NTR_INFO", "").replace("<br/>", "\n").strip()

        with st.expander(f"{meal_name} 🍱"):
            # 중식 이모지 애니메이션
            if meal_name == "중식":
                st.markdown('<div class="shake-emoji">🍽️</div>', unsafe_allow_html=True)

            # 메뉴 표시
            st.markdown(
                f"<pre style='font-size:15px; color:#222222; "
                f"background:#f1f1f1; padding:12px; border-radius:12px;'>{clean}</pre>",
                unsafe_allow_html=True
            )

            # 영양 정보 표시
            if nutr_info:
                st.markdown(f"**🔍 영양 정보:**\n{nutr_info}")

                # 숫자 추출
                nutr_dict = {}
                tokens = nutr_info.split()
                i = 0
                while i < len(tokens) - 1:
                    key = tokens[i]
                    value = tokens[i + 1]
                    try:
                        nutr_dict[key] = float(value)
                    except:
                        pass
                    i += 2

                # 탄수화물, 단백질, 지방 추출
                labels = []
                values = []
                colors = ['#ffcc80', '#81d4fa', '#ffab91']
                if "탄수화물(g)" in nutr_dict:
                    labels.append("탄수화물")
                    values.append(nutr_dict["탄수화물(g)"])
                if "단백질(g)" in nutr_dict:
                    labels.append("단백질")
                    values.append(nutr_dict["단백질(g)"])
                if "지방(g)" in nutr_dict:
                    labels.append("지방")
                    values.append(nutr_dict["지방(g)"])

                # 차트 그리기
                if values:
                    fig = go.Figure(
                        data=[go.Pie(labels=labels, values=values, hole=0.3,
                                     marker_colors=colors, textinfo='label+percent')]
                    )
                else:
                    # 데이터가 없을 때 샘플 차트
                    fig = go.Figure(
                        data=[go.Pie(labels=["탄수화물", "단백질", "지방"], values=[60, 20, 20],
                                     hole=0.3, marker_colors=colors, textinfo='label+percent')]
                    )

                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.info("⚠️ 영양 정보가 제공되지 않았습니다.")

# ===== Fun Fact 팝업 =====
if "show_popup" not in st.session_state:
    st.session_state.show_popup = False

if st.button("💡 오늘의 Fun Fact 보기"):
    st.session_state.show_popup = True

if st.session_state.show_popup:
    fun_fact = random.choice(fun_facts)
    st.markdown(f"""
        <div class="popup">
            <h3>💡 오늘의 Fun Fact</h3>
            <p style="font-size:16px;">{fun_fact}</p>
            <form action="" method="get">
                <button name="close" style="padding:8px 15px; border:none; border-radius:8px; background:#444; color:white; cursor:pointer;">닫기</button>
            </form>
        </div>
    """, unsafe_allow_html=True)

    # 닫기 버튼 처리
    if "close" in st.query_params:
        st.session_state.show_popup = False

